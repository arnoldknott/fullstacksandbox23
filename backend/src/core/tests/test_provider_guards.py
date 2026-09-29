"""Outer policy and signed-token tests; no live identity provider is needed."""

import time
from typing import cast
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, HTTPException
from httpx2 import ASGITransport, AsyncClient
from jwt.algorithms import RSAAlgorithm
from pydantic import ValidationError

from core.authentication.base import (
    ProviderValidator,
    VerifiedIdentity,
    verify_provider_token,
)
from core.authentication.linkedin import (
    LINKEDIN_ISSUER,
    validate_linkedin_identity_token,
)
from core.cache import encryption
from core.config import config
from core.security import (
    AllowAnonymous,
    CurrentAccessToken,
    Guards,
    LinkedInGuard,
    MicrosoftGuard,
    SessionReferenceCredential,
    authorize_session_candidates,
    check_token_against_guards_with_status,
    check_token_against_guards,
    evaluate_guards,
    get_token_payload_from_cache,
    load_session_provider_candidates,
    get_http_access_token_payload,
    provide_http_token_payload,
    resolve_session_provider_identity,
    select_provider_candidate,
)
from core.types import (
    CurrentUserData,
    EventGuard,
    GuardOutcome,
    GuardTypes,
    IdentityProvider,
)
from routers.socketio.v1.base import (
    BaseNamespace,
    SocketAuthenticationExpiredError,
    SocketAuthorizationFailedError,
)

pytestmark = pytest.mark.anyio

ISSUER = LINKEDIN_ISSUER
CLIENT_ID = "synthetic-client"


@pytest.fixture(scope="module")
def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def signed_identity(signing_key):
    claims = {
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "sub": "CaseSensitive-sub",
        "iat": int(time.time()) - 5,
        "exp": int(time.time()) + 300,
    }
    key = RSAAlgorithm.to_jwk(signing_key.public_key(), as_dict=True)
    key.update(kid="test-key", use="sig", alg="RS256")

    def create(overrides=None, omit=(), headers=None):
        payload = {**claims, **(overrides or {})}
        for name in omit:
            payload.pop(name)
        token = jwt.encode(
            payload,
            signing_key,
            algorithm="RS256",
            headers=headers or {"kid": "test-key"},
        )
        return token, {"keys": [key]}

    return create


def validate(token, jwks):
    return validate_linkedin_identity_token(token, jwks, client_id=CLIENT_ID)


async def test_signed_linkedin_token_preserves_subject(signed_identity):
    token, jwks = signed_identity()
    assert validate(token, jwks)["sub"] == "CaseSensitive-sub"


@pytest.mark.parametrize(
    "overrides",
    [
        {"iss": "https://attacker.invalid"},
        {"aud": "another-app"},
        {"exp": int(time.time()) - 10},
        {"iat": int(time.time()) + 600},
        {"nbf": int(time.time()) + 600},
        {"sub": ""},
        {"sub": "  "},
        {"sub": 123},
        {"iat": "123"},
        {"iat": True},
        {"azp": "another-app"},
        {"aud": [CLIENT_ID, "another-app"]},
        {"aud": [CLIENT_ID, "another-app"], "azp": "another-app"},
    ],
)
async def test_linkedin_rejects_invalid_claims(signed_identity, overrides):
    token, jwks = signed_identity(overrides)
    with pytest.raises(jwt.PyJWTError):
        validate(token, jwks)


@pytest.mark.parametrize("claim", ["iss", "aud", "sub", "iat", "exp"])
async def test_linkedin_requires_identity_claims(signed_identity, claim):
    token, jwks = signed_identity(omit=[claim])
    with pytest.raises(jwt.PyJWTError):
        validate(token, jwks)


async def test_linkedin_multiple_audiences_require_matching_authorized_party(
    signed_identity,
):
    token, jwks = signed_identity({"aud": [CLIENT_ID, "other"], "azp": CLIENT_ID})
    assert validate(token, jwks)["azp"] == CLIENT_ID


async def test_linkedin_rejects_wrong_signing_key(signed_identity):
    token, _ = signed_identity()
    wrong = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = RSAAlgorithm.to_jwk(wrong.public_key(), as_dict=True)
    key["kid"] = "test-key"
    with pytest.raises(jwt.InvalidSignatureError):
        validate(token, {"keys": [key]})


@pytest.mark.parametrize(
    "key_change", [{"kid": "other"}, {"use": "enc"}, {"alg": "RS512"}]
)
async def test_linkedin_rejects_wrong_key_metadata(signed_identity, key_change):
    token, jwks = signed_identity()
    jwks["keys"][0].update(key_change)
    with pytest.raises(jwt.PyJWTError):
        validate(token, jwks)


async def test_linkedin_rejects_unsigned_token(signed_identity):
    _, jwks = signed_identity()
    token = jwt.encode(
        {"iss": ISSUER}, key="", algorithm="none", headers={"kid": "test-key"}
    )
    with pytest.raises(jwt.PyJWTError):
        validate(token, jwks)


@pytest.mark.anyio
async def test_dispatch_uses_issuer_only_as_hint(signed_identity):
    token, jwks = signed_identity()
    microsoft = AsyncMock()
    linkedin = AsyncMock(side_effect=lambda value: validate(value, jwks))
    identity = await verify_provider_token(
        token,
        {
            "https://microsoft.invalid": ProviderValidator(
                IdentityProvider.microsoft, microsoft
            ),
            ISSUER: ProviderValidator(IdentityProvider.linkedin, linkedin),
        },
    )
    assert identity.provider == IdentityProvider.linkedin
    assert identity.claims["sub"] == "CaseSensitive-sub"
    microsoft.assert_not_awaited()
    linkedin.assert_awaited_once_with(token)


@pytest.mark.anyio
async def test_dispatch_does_not_fetch_unknown_issuer(signed_identity):
    token, _ = signed_identity({"iss": "https://attacker.invalid"})
    validator = AsyncMock()
    with pytest.raises(HTTPException) as error:
        await verify_provider_token(
            token, {ISSUER: ProviderValidator(IdentityProvider.linkedin, validator)}
        )
    assert error.value.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.anyio
async def test_dispatch_rejects_signature_failure(signed_identity):
    token, _ = signed_identity()
    validator = AsyncMock(side_effect=jwt.InvalidSignatureError())
    with pytest.raises(HTTPException) as error:
        await verify_provider_token(
            token, {ISSUER: ProviderValidator(IdentityProvider.linkedin, validator)}
        )
    assert error.value.status_code == 401


async def test_policy_requires_explicit_configuration():
    policy = Guards(
        MicrosoftGuard(scopes=["api.read"]), LinkedInGuard(), AllowAnonymous()
    )()
    assert policy.allows_anonymous
    assert EventGuard(event="read", guards=policy).guards == policy
    with pytest.raises(ValidationError):
        Guards()
    with pytest.raises(TypeError):
        # Deliberately exercise the removed constructor argument.
        Guards(scopes=["api.read"])  # pyright: ignore[reportCallIssue]


async def test_policy_rejects_empty_or_mixed_alternatives():
    with pytest.raises(ValidationError):
        GuardTypes(alternatives=())
    with pytest.raises(ValidationError):
        GuardTypes.model_validate(
            {"alternatives": (LinkedInGuard(),), "scopes": ["api.read"]}
        )
    with pytest.raises(ValidationError):
        LinkedInGuard.model_validate({"roles": ["Admin"]})


async def test_policy_is_immutable():
    policy = Guards(MicrosoftGuard(scopes=["api.read"]))()
    with pytest.raises(ValidationError):
        policy.alternatives = (AllowAnonymous(),)
    microsoft_guard = policy.alternatives[0]
    assert isinstance(microsoft_guard, MicrosoftGuard)
    with pytest.raises(ValidationError):
        microsoft_guard.scopes = ("api.write",)


@pytest.mark.anyio
async def test_fastapi_injects_configuration_not_current_user():
    app = FastAPI()
    declaration = Guards(MicrosoftGuard(scopes=["api.read"]), LinkedInGuard())

    @app.get("/policy")
    def endpoint(guards: GuardTypes = Depends(declaration)):
        return guards

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/policy")
    assert response.status_code == 200
    assert [item["provider"] for item in response.json()["alternatives"]] == [
        "microsoft",
        "linkedin",
    ]


@pytest.mark.parametrize(
    "scopes,allowed",
    [
        ("api.read api.write", True),
        ("api.read.all api.write", False),
        ("api.read", False),
    ],
)
async def test_microsoft_requirements_are_exact_and_combined(scopes, allowed):
    identity = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": scopes, "roles": ["User"]}
    )
    policy = Guards(MicrosoftGuard(scopes=["api.read", "api.write"], roles=["User"]))()
    if allowed:
        assert evaluate_guards(identity, policy) is GuardOutcome.AUTHENTICATED
    else:
        with pytest.raises(HTTPException):
            evaluate_guards(identity, policy)


async def test_microsoft_admin_override_does_not_override_scopes_or_groups():
    group = uuid4()
    identity = VerifiedIdentity(
        IdentityProvider.microsoft,
        {"roles": ["Admin"], "scp": "api.read", "groups": [str(group)]},
    )
    assert (
        evaluate_guards(
            identity,
            Guards(
                MicrosoftGuard(roles=["User"], scopes=["api.read"], groups=[group])
            )(),
        )
        is GuardOutcome.AUTHENTICATED
    )
    for guard in [
        MicrosoftGuard(scopes=["api.write"]),
        MicrosoftGuard(groups=[uuid4()]),
    ]:
        with pytest.raises(HTTPException):
            evaluate_guards(identity, Guards(guard)())


async def test_linkedin_cannot_satisfy_microsoft_admin_guard():
    identity = VerifiedIdentity(
        IdentityProvider.linkedin,
        {"roles": ["Admin"], "scp": "api.read", "provider": "microsoft"},
    )
    assert (
        evaluate_guards(
            identity, Guards(MicrosoftGuard(roles=["Admin"]), AllowAnonymous())()
        )
        is GuardOutcome.ANONYMOUS
    )
    assert (
        evaluate_guards(
            identity, Guards(MicrosoftGuard(roles=["Admin"]), LinkedInGuard())()
        )
        is GuardOutcome.AUTHENTICATED
    )


async def test_anonymous_is_the_final_explicit_fallback_without_claims():
    assert (
        evaluate_guards(None, Guards(MicrosoftGuard(), AllowAnonymous())())
        is GuardOutcome.ANONYMOUS
    )
    with pytest.raises(HTTPException):
        evaluate_guards(None, Guards(MicrosoftGuard(), LinkedInGuard())())
    identity = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": "api.read", "roles": []}
    )
    assert (
        evaluate_guards(
            identity, Guards(AllowAnonymous(), MicrosoftGuard(roles=["User"]))()
        )
        is GuardOutcome.ANONYMOUS
    )


async def test_session_candidate_selection_prefers_eligible_microsoft():
    microsoft = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": "api.read", "roles": ["User"]}
    )
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member"})
    selected = select_provider_candidate(
        (linkedin, microsoft),
        Guards(MicrosoftGuard(scopes=["api.read"]), LinkedInGuard())(),
    )
    assert selected is microsoft


async def test_session_candidate_selection_falls_back_only_to_declared_provider():
    microsoft = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": "api.read", "roles": []}
    )
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member"})
    assert (
        select_provider_candidate(
            (microsoft, linkedin),
            Guards(MicrosoftGuard(roles=["User"]), LinkedInGuard())(),
        )
        is linkedin
    )
    with pytest.raises(HTTPException):
        select_provider_candidate(
            (microsoft, linkedin), Guards(MicrosoftGuard(roles=["User"]))()
        )


async def test_session_candidate_selection_uses_guard_order():
    microsoft = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": "api.read", "roles": ["User"]}
    )
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member"})
    assert (
        select_provider_candidate(
            (microsoft, linkedin), Guards(LinkedInGuard(), MicrosoftGuard())()
        )
        is linkedin
    )


async def test_session_candidate_selection_uses_anonymous_as_final_fallback():
    microsoft = VerifiedIdentity(IdentityProvider.microsoft, {"roles": []})
    assert (
        select_provider_candidate(
            (microsoft,),
            Guards(AllowAnonymous(), MicrosoftGuard(roles=["User"]))(),
        )
        is None
    )
    assert (
        select_provider_candidate((), Guards(MicrosoftGuard(), AllowAnonymous())())
        is None
    )


@pytest.mark.anyio
async def test_session_candidates_must_all_resolve_to_session_user(monkeypatch):
    session_user_id = uuid4()
    microsoft = VerifiedIdentity(IdentityProvider.microsoft, {"roles": ["User"]})
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member"})
    resolved = {
        IdentityProvider.microsoft: CurrentUserData(user_id=session_user_id),
        IdentityProvider.linkedin: CurrentUserData(user_id=session_user_id),
    }
    resolver = AsyncMock(side_effect=lambda identity: resolved[identity.provider])
    monkeypatch.setattr(
        "core.security.get_session_value",
        lambda session_id, path: {"id": str(session_user_id)},
    )
    monkeypatch.setattr("core.security.resolve_session_identity", resolver)
    selected, current_user = await authorize_session_candidates(
        "session",
        (linkedin, microsoft),
        Guards(MicrosoftGuard(roles=["User"]), LinkedInGuard())(),
    )
    assert selected is microsoft
    assert current_user == resolved[IdentityProvider.microsoft]
    assert resolver.await_count == 2


@pytest.mark.anyio
async def test_session_candidate_user_mismatch_fails_closed(monkeypatch):
    session_user_id = uuid4()
    microsoft = VerifiedIdentity(IdentityProvider.microsoft, {"roles": ["User"]})
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member"})
    resolver = AsyncMock(
        side_effect=[
            CurrentUserData(user_id=session_user_id),
            CurrentUserData(user_id=uuid4()),
        ]
    )
    monkeypatch.setattr(
        "core.security.get_session_value",
        lambda session_id, path: {"id": str(session_user_id)},
    )
    monkeypatch.setattr("core.security.resolve_session_identity", resolver)
    with pytest.raises(HTTPException) as error:
        await authorize_session_candidates(
            "session",
            (microsoft, linkedin),
            Guards(MicrosoftGuard(roles=["User"]), LinkedInGuard())(),
        )
    assert error.value.status_code == 401
    assert error.value.detail == "Session provider identity mismatch."


@pytest.mark.anyio
async def test_account_link_resolves_only_the_initiating_session_provider(monkeypatch):
    session_user_id = uuid4()
    microsoft = VerifiedIdentity(IdentityProvider.microsoft, {"oid": "survivor"})
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "merge-source"})
    values = {
        "$.identityProvider": IdentityProvider.microsoft.value,
        "$.currentUser": {"id": str(session_user_id)},
    }
    monkeypatch.setattr(
        "core.security.get_session_value", lambda session_id, path: values[path]
    )
    monkeypatch.setattr(
        "core.security.load_session_provider_candidates",
        AsyncMock(return_value=(microsoft, linkedin)),
    )
    resolver = AsyncMock(return_value=CurrentUserData(user_id=session_user_id))
    monkeypatch.setattr("core.security.resolve_session_identity", resolver)

    identity = await resolve_session_provider_identity("session")

    assert identity is microsoft
    resolver.assert_awaited_once_with(microsoft)


@pytest.mark.anyio
async def test_session_candidate_loader_returns_all_valid_providers(monkeypatch):
    account = {"homeAccountId": "account", "username": "user@example.invalid"}
    session_values = {
        "$.microsoftAccount": account,
        "$.microsoftBackendAccessToken": {"accessToken": "microsoft-token"},
        "$.linkedinSubject": "linkedin-subject",
    }
    monkeypatch.setattr(
        "core.security.get_session_value",
        lambda session_id, path: session_values[path],
    )
    monkeypatch.setattr(
        "core.security.get_protected_cache_value",
        lambda key: {"idToken": "linkedin-token"},
    )
    microsoft_claims = AsyncMock(return_value={"oid": "microsoft-subject"})
    linkedin_claims = AsyncMock(return_value={"sub": "linkedin-subject"})
    monkeypatch.setattr("core.security.azure.get_azure_token_payload", microsoft_claims)
    monkeypatch.setattr(
        "core.security.linkedin.get_linkedin_token_payload", linkedin_claims
    )
    monkeypatch.setattr("core.security.config.LINKEDIN_CLIENT_ID", CLIENT_ID)

    candidates = await load_session_provider_candidates("session", ["api.read"])

    assert [candidate.provider for candidate in candidates] == [
        IdentityProvider.microsoft,
        IdentityProvider.linkedin,
    ]
    linkedin_claims.assert_awaited_once_with("linkedin-token", client_id=CLIENT_ID)


@pytest.mark.anyio
async def test_session_candidate_loader_treats_expired_linkedin_as_unavailable(
    monkeypatch,
):
    values = {
        "$.microsoftAccount": {"username": "user@example.invalid"},
        "$.microsoftBackendAccessToken": {"accessToken": "microsoft-token"},
        "$.linkedinSubject": "linkedin-subject",
    }
    monkeypatch.setattr("core.security.get_session_value", lambda _, path: values[path])
    monkeypatch.setattr(
        "core.security.get_protected_cache_value",
        lambda _: {"idToken": "expired-linkedin-token"},
    )
    monkeypatch.setattr(
        "core.security.azure.get_azure_token_payload",
        AsyncMock(return_value={"oid": "microsoft-subject"}),
    )
    monkeypatch.setattr(
        "core.security.linkedin.get_linkedin_token_payload",
        AsyncMock(side_effect=HTTPException(status_code=401)),
    )
    candidates = await load_session_provider_candidates("session")
    assert len(candidates) == 1
    assert candidates[0].provider == IdentityProvider.microsoft


@pytest.mark.anyio
async def test_session_candidate_loader_treats_invalid_microsoft_as_unavailable(
    monkeypatch,
):
    values = {
        "$.microsoftAccount": {"username": "user@example.invalid"},
        "$.microsoftBackendAccessToken": {"accessToken": "microsoft-token"},
        "$.linkedinSubject": "linkedin-subject",
    }
    monkeypatch.setattr("core.security.get_session_value", lambda _, path: values[path])
    monkeypatch.setattr(
        "core.security.get_protected_cache_value",
        lambda _: {"idToken": "linkedin-token"},
    )
    monkeypatch.setattr(
        "core.security.azure.get_azure_token_payload",
        AsyncMock(side_effect=jwt.InvalidSignatureError()),
    )
    monkeypatch.setattr(
        "core.security.linkedin.get_linkedin_token_payload",
        AsyncMock(return_value={"sub": "linkedin-subject"}),
    )
    candidates = await load_session_provider_candidates("session")
    assert [candidate.provider for candidate in candidates] == [
        IdentityProvider.linkedin
    ]


@pytest.mark.anyio
async def test_current_user_resolution_remains_outside_policy(monkeypatch):
    expected = CurrentUserData(user_id=uuid4(), azure_token_roles=["User"])
    resolver = AsyncMock(return_value=expected)
    monkeypatch.setattr(CurrentAccessToken, "provides_current_user", resolver)
    identity = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": "api.read", "roles": ["User"]}
    )
    actual = await check_token_against_guards(
        identity, Guards(MicrosoftGuard(scopes=["api.read"]))()
    )
    assert actual == expected
    resolver.assert_awaited_once()
    resolver.reset_mock()
    assert await check_token_against_guards(None, Guards(AllowAnonymous())()) is None
    resolver.assert_not_awaited()


@pytest.mark.anyio
async def test_scope_helper_does_not_accept_substring():
    token = CurrentAccessToken({"scp": "api.read.all"})
    assert await token.has_scope("api.read", require=False) is False


def namespace_with(policy):
    namespace = BaseNamespace(
        server=AsyncMock(), event_guards=[EventGuard(event="read", guards=policy)]
    )
    namespace._get_session_id = AsyncMock(return_value="session")
    return namespace


@pytest.mark.anyio
async def test_socket_explicit_anonymous_rejects_missing_cached_token():
    namespace = namespace_with(Guards(MicrosoftGuard(), AllowAnonymous())())
    namespace._get_token_payload_if_authenticated = AsyncMock(
        side_effect=ValueError("No cached token")
    )
    namespace._end_expired_socket = AsyncMock()

    with pytest.raises(SocketAuthenticationExpiredError):
        await namespace._get_current_user_and_check_guard("socket", "read")

    namespace._end_expired_socket.assert_not_awaited()


@pytest.mark.anyio
async def test_socket_protected_policy_rejects_missing_cached_token():
    namespace = namespace_with(Guards(MicrosoftGuard())())

    namespace._get_token_payload_if_authenticated = AsyncMock(
        side_effect=ValueError("No cached token")
    )
    namespace._end_expired_socket = AsyncMock()

    with pytest.raises(SocketAuthenticationExpiredError):
        await namespace._get_current_user_and_check_guard("socket", "read")

    namespace._end_expired_socket.assert_not_awaited()


async def test_socket_session_provider_selection_follows_event_guard_order(monkeypatch):
    microsoft = VerifiedIdentity(IdentityProvider.microsoft, {"oid": "ms"})
    linkedin = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "li"})
    user_id = uuid4()
    monkeypatch.setattr("core.security.require_session_user_id", lambda _: user_id)
    monkeypatch.setattr(
        "core.security.resolve_session_identity",
        AsyncMock(side_effect=lambda identity: CurrentUserData(user_id=user_id)),
    )
    namespace = namespace_with(Guards(LinkedInGuard(), MicrosoftGuard())())
    namespace._get_session_id = AsyncMock(return_value="session")
    monkeypatch.setattr(
        "routers.socketio.v1.base.load_session_provider_candidates",
        AsyncMock(return_value=(microsoft, linkedin)),
    )
    selected = await namespace._get_token_payload_if_authenticated(
        "session", Guards(LinkedInGuard(), MicrosoftGuard())()
    )
    assert selected is linkedin


@pytest.mark.anyio
async def test_socket_uses_anonymous_after_provider_requirements_fail():
    namespace = namespace_with(
        Guards(MicrosoftGuard(roles=["User"]), AllowAnonymous())()
    )
    namespace._get_token_payload_if_authenticated = AsyncMock(
        return_value={"roles": []}
    )
    namespace._emit_status = AsyncMock()

    assert await namespace._get_current_user_and_check_guard("socket", "read") is None
    namespace._emit_status.assert_not_awaited()


async def test_socket_event_error_handler_ends_expired_socket_once():
    namespace = namespace_with(Guards(MicrosoftGuard())())
    namespace._end_expired_socket = AsyncMock()
    namespace._emit_status = AsyncMock()

    await namespace._handle_event_error(
        "socket",
        SocketAuthenticationExpiredError("Authentication expired."),
        context="Failed event",
    )

    namespace._end_expired_socket.assert_awaited_once_with("socket")
    namespace._emit_status.assert_not_awaited()


async def test_socket_event_error_handler_emits_authorization_failure_once():
    namespace = namespace_with(Guards(MicrosoftGuard())())
    namespace._end_expired_socket = AsyncMock()
    namespace._emit_status = AsyncMock()

    await namespace._handle_event_error(
        "socket",
        SocketAuthorizationFailedError("Authorization failed."),
        context="Failed event",
    )

    namespace._end_expired_socket.assert_not_awaited()
    namespace._emit_status.assert_awaited_once_with(
        "socket", {"error": "access", "code": "authorization-failed"}
    )


async def test_socket_event_error_handler_emits_generic_detail_once():
    namespace = namespace_with(Guards(MicrosoftGuard())())
    namespace._end_expired_socket = AsyncMock()
    namespace._emit_status = AsyncMock()

    await namespace._handle_event_error(
        "socket", ValueError("Invalid payload."), context="Failed event"
    )

    namespace._end_expired_socket.assert_not_awaited()
    namespace._emit_status.assert_awaited_once_with(
        "socket", {"error": "other", "detail": "Invalid payload."}
    )


async def test_new_socket_policy_rejects_missing_event_declaration():
    namespace = namespace_with(Guards(MicrosoftGuard())())
    with pytest.raises(ConnectionRefusedError):
        namespace._get_event_guards("undeclared")
    with pytest.raises(ValidationError):
        EventGuard.model_validate({"event": "read", "guards": None})


async def test_direct_policy_calls_resolve_user(monkeypatch):
    expected = CurrentUserData(user_id=uuid4())
    monkeypatch.setattr(
        CurrentAccessToken, "provides_current_user", AsyncMock(return_value=expected)
    )
    assert (
        await check_token_against_guards(
            {"roles": ["User"]}, Guards(MicrosoftGuard(roles=["User"]))()
        )
        == expected
    )


async def test_valid_microsoft_socket_policy_resolves_user(monkeypatch):
    expected = CurrentUserData(user_id=uuid4())
    monkeypatch.setattr(
        CurrentAccessToken, "provides_current_user", AsyncMock(return_value=expected)
    )
    namespace = namespace_with(Guards(MicrosoftGuard(roles=["User"]))())
    namespace._get_token_payload_if_authenticated = AsyncMock(
        return_value={"roles": ["User"]}
    )
    assert (
        await namespace._get_current_user_and_check_guard("socket", "read") == expected
    )


async def test_linkedin_signup_never_uses_microsoft_signup(monkeypatch):
    resolver = AsyncMock()
    monkeypatch.setattr(CurrentAccessToken, "provides_current_user", resolver)
    user = await check_token_against_guards(
        VerifiedIdentity(
            IdentityProvider.linkedin,
            {"sub": "subject", "roles": ["Admin"], "groups": []},
        ),
        Guards(LinkedInGuard())(),
    )
    assert user is not None
    assert user.azure_token_roles == []
    assert user.azure_token_groups == []
    resolver.assert_not_awaited()


async def test_guard_typo_is_not_ignored():
    with pytest.raises(ValidationError):
        GuardTypes.model_validate(
            {"alternatives": (MicrosoftGuard(),), "role": ["Admin"]}
        )


async def test_unsupported_provider_never_falls_back_to_microsoft(monkeypatch):
    resolver = AsyncMock()
    monkeypatch.setattr(CurrentAccessToken, "provides_current_user", resolver)
    # Simulate a future provider admitted by a guard before its resolver exists.
    monkeypatch.setattr(
        "core.security.evaluate_guards",
        lambda identity, guards: GuardOutcome.AUTHENTICATED,
    )
    with pytest.raises(HTTPException) as error:
        await check_token_against_guards(
            VerifiedIdentity(cast(IdentityProvider, "future-provider"), {}),
            Guards(MicrosoftGuard())(),
        )
    assert error.value.status_code == 401
    assert error.value.detail == "Unsupported identity provider."
    resolver.assert_not_awaited()


@pytest.mark.anyio
async def test_http_extraction_preserves_verified_linkedin_provider(monkeypatch):
    expected = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member-sub"})
    verify = AsyncMock(return_value=expected)
    monkeypatch.setattr("core.security.verify_provider_token", verify)

    assert await provide_http_token_payload("signed-token") == expected
    verify.assert_awaited_once()


@pytest.mark.anyio
async def test_http_extraction_accepts_session_only_for_frontend_service(monkeypatch):
    verify = AsyncMock()
    monkeypatch.setattr("core.security._verify_frontend_service_token", verify)

    session_id = str(uuid4())
    credential = await provide_http_token_payload("service-token", session_id)

    assert credential == SessionReferenceCredential(session_id)
    verify.assert_awaited_once_with("service-token")


@pytest.mark.anyio
async def test_http_extraction_rejects_session_without_service_token():
    with pytest.raises(HTTPException) as error:
        await provide_http_token_payload(None, "session-reference")
    assert error.value.status_code == 401


@pytest.mark.anyio
async def test_frontend_service_token_requires_app_only_expected_client(monkeypatch):
    from core.security import _verify_frontend_service_token

    validator = AsyncMock(
        return_value={
            "azp": config.FRONTEND_SVELTE_CLIENT_ID,
            "idtyp": "app",
        }
    )
    monkeypatch.setattr("core.security._validate_azure_token", validator)
    await _verify_frontend_service_token("service-token")

    validator.return_value = {
        "appid": config.FRONTEND_SVELTE_CLIENT_ID,
        "oid": "frontend-object-id",
        "sub": "frontend-object-id",
    }
    await _verify_frontend_service_token("service-token")

    for claims in [
        {"azp": "another-client", "idtyp": "app"},
        {"azp": config.FRONTEND_SVELTE_CLIENT_ID, "idtyp": "user"},
        {
            "azp": config.FRONTEND_SVELTE_CLIENT_ID,
            "oid": "user-object-id",
            "sub": "pairwise-user-subject",
        },
    ]:
        validator.return_value = claims
        with pytest.raises(HTTPException) as error:
            await _verify_frontend_service_token("service-token")
        assert error.value.status_code == 401


def session_authentication_app(path: str = "/api/v1/user/me") -> FastAPI:
    app = FastAPI()
    router_guards = Guards(MicrosoftGuard(scopes=["api.read"]), LinkedInGuard())
    endpoint_guards = Guards(MicrosoftGuard(roles=["User"]), LinkedInGuard())

    @app.get(path, dependencies=[Depends(router_guards.check_http)])
    async def endpoint(
        token_payload=Depends(get_http_access_token_payload),
        guards: GuardTypes = Depends(endpoint_guards),
    ):
        current_user, status_code = await check_token_against_guards_with_status(
            token_payload, guards
        )
        return {
            "credential": type(token_payload).__name__,
            "user-id": str(current_user.user_id) if current_user else None,
            "status-code": status_code,
        }

    return app


async def test_http_session_request_reuses_candidate_load_and_user_binding(monkeypatch):
    session_id = str(uuid4())
    user_id = uuid4()
    candidate = VerifiedIdentity(
        IdentityProvider.microsoft,
        {"scp": "api.read", "roles": ["User"]},
    )
    monkeypatch.setattr(
        "core.security._validate_azure_token",
        AsyncMock(
            return_value={
                "azp": config.FRONTEND_SVELTE_CLIENT_ID,
                "idtyp": "app",
            }
        ),
    )
    monkeypatch.setattr(
        "core.security.get_session_value",
        lambda actual_session_id, path: {"id": str(user_id)},
    )
    loader = AsyncMock(return_value=(candidate,))
    resolver = AsyncMock(return_value=CurrentUserData(user_id=user_id))
    monkeypatch.setattr("core.security.load_session_provider_candidates", loader)
    monkeypatch.setattr("core.security.resolve_session_identity", resolver)

    async with AsyncClient(
        transport=ASGITransport(app=session_authentication_app()),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/user/me",
            headers={
                "Authorization": "Bearer frontend-service-token",
                "X-Application-Session": session_id,
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "credential": "SessionReferenceCredential",
        "user-id": str(user_id),
        "status-code": None,
    }
    loader.assert_awaited_once_with(session_id, [f"api://{config.API_SCOPE}/api.read"])
    resolver.assert_awaited_once_with(candidate)


async def test_http_user_me_bootstrap_reuses_candidate_load(monkeypatch):
    session_id = str(uuid4())
    user_id = uuid4()
    candidate = VerifiedIdentity(IdentityProvider.linkedin, {"sub": "member"})
    monkeypatch.setattr(
        "core.security._validate_azure_token",
        AsyncMock(
            return_value={
                "azp": config.FRONTEND_SVELTE_CLIENT_ID,
                "idtyp": "app",
            }
        ),
    )
    monkeypatch.setattr("core.security.get_session_value", lambda *args: None)
    loader = AsyncMock(return_value=(candidate,))
    signup = AsyncMock(return_value=(CurrentUserData(user_id=user_id), 201))
    monkeypatch.setattr("core.security.load_session_provider_candidates", loader)
    monkeypatch.setattr("core.security.resolve_verified_identity_with_status", signup)

    async with AsyncClient(
        transport=ASGITransport(app=session_authentication_app()),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/user/me",
            headers={
                "Authorization": "Bearer frontend-service-token",
                "X-Application-Session": session_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["status-code"] == 201
    loader.assert_awaited_once()
    signup.assert_awaited_once_with(candidate)


async def test_http_direct_provider_bearer_remains_compatible(monkeypatch):
    user_id = uuid4()
    identity = VerifiedIdentity(
        IdentityProvider.microsoft,
        {"scp": "api.read", "roles": ["User"]},
    )
    monkeypatch.setattr(
        "core.security.verify_provider_token", AsyncMock(return_value=identity)
    )
    monkeypatch.setattr(
        "core.security.resolve_verified_identity_with_status",
        AsyncMock(return_value=(CurrentUserData(user_id=user_id), None)),
    )

    async with AsyncClient(
        transport=ASGITransport(app=session_authentication_app()),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/user/me", headers={"Authorization": "Bearer provider-token"}
        )

    assert response.status_code == 200
    assert response.json()["credential"] == "VerifiedIdentity"


@pytest.mark.parametrize(
    "path,session_id",
    [
        ("/api/v1/user/me", "not-a-uuid"),
        ("/api/v1/resource", str(uuid4())),
    ],
)
async def test_http_invalid_session_never_falls_through_anonymous(
    monkeypatch, path, session_id
):
    monkeypatch.setattr(
        "core.security._validate_azure_token",
        AsyncMock(
            return_value={
                "azp": config.FRONTEND_SVELTE_CLIENT_ID,
                "idtyp": "app",
            }
        ),
    )
    monkeypatch.setattr("core.security.get_session_value", lambda *args: None)
    app = session_authentication_app(path)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            path,
            headers={
                "Authorization": "Bearer frontend-service-token",
                "X-Application-Session": session_id,
            },
        )

    assert response.status_code == 401


async def test_http_session_rejects_delegated_frontend_bearer(monkeypatch):
    monkeypatch.setattr(
        "core.security._validate_azure_token",
        AsyncMock(
            return_value={
                "azp": config.FRONTEND_SVELTE_CLIENT_ID,
                "idtyp": "user",
                "oid": "user-object-id",
                "sub": "user-subject",
            }
        ),
    )

    async with AsyncClient(
        transport=ASGITransport(app=session_authentication_app()),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/user/me",
            headers={
                "Authorization": "Bearer delegated-provider-token",
                "X-Application-Session": str(uuid4()),
            },
        )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_socket_cache_selects_linkedin_identity_token(monkeypatch):
    encrypted_tokens = encryption.encrypt(
        "linkedin:member-sub", "$", {"idToken": "identity-token"}
    )
    cache_json = Mock()
    cache_json.get.side_effect = lambda key, path=None: {
        ("session:session", "$.identityProvider"): ["linkedin"],
        ("session:session", "$.linkedinSubject"): ["member-sub"],
        ("linkedin:member-sub", None): encrypted_tokens,
    }.get((key, path), [])
    monkeypatch.setattr(
        "core.cache.redis_session_client.json", Mock(return_value=cache_json)
    )
    validate = AsyncMock(
        return_value={
            "iss": ISSUER,
            "aud": CLIENT_ID,
            "sub": "member-sub",
            "iat": 1,
            "exp": 2,
        }
    )
    monkeypatch.setattr("core.security.linkedin.get_linkedin_token_payload", validate)
    monkeypatch.setattr("core.security.config.LINKEDIN_CLIENT_ID", CLIENT_ID)

    identity = await get_token_payload_from_cache("session")

    assert identity.provider == IdentityProvider.linkedin
    assert identity.claims["sub"] == "member-sub"
    validate.assert_awaited_once_with("identity-token", client_id=CLIENT_ID)


@pytest.mark.anyio
async def test_socket_cache_defaults_a_missing_provider_path_to_microsoft(monkeypatch):
    account = {"homeAccountId": "account", "username": "user@example.invalid"}
    encrypted_account = encryption.encrypt(
        "session:session", "$.microsoftAccount", account
    )
    encrypted_token = encryption.encrypt(
        "session:session",
        "$.microsoftBackendAccessToken",
        {"accessToken": "access-token"},
    )
    cache_json = Mock()
    responses: dict[tuple[str, str], list[object]] = {
        ("session:session", "$.identityProvider"): [],
        ("session:session", "$.microsoftAccount"): [encrypted_account],
        ("session:session", "$.microsoftBackendAccessToken"): [encrypted_token],
    }

    def get_cached_value(key: str, path: str) -> list[object]:
        return responses.get((key, path), [])

    cache_json.get.side_effect = get_cached_value
    monkeypatch.setattr(
        "core.cache.redis_session_client.json", Mock(return_value=cache_json)
    )
    validate = AsyncMock(return_value={"oid": "member", "tid": "tenant"})
    monkeypatch.setattr("core.security.azure.get_azure_token_payload", validate)

    identity = await get_token_payload_from_cache("session")

    assert identity.provider == IdentityProvider.microsoft
    assert identity.claims == {"oid": "member", "tid": "tenant"}
    validate.assert_awaited_once_with("access-token")
