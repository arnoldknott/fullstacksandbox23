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
from core.security import (
    AllowAnonymous,
    CurrentAccessToken,
    Guards,
    LinkedInGuard,
    MicrosoftGuard,
    check_token_against_guards,
    evaluate_guards,
    get_token_payload_from_cache,
    provide_http_token_payload,
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
    with pytest.raises(HTTPException):
        evaluate_guards(
            identity, Guards(MicrosoftGuard(roles=["Admin"]), AllowAnonymous())()
        )
    assert (
        evaluate_guards(
            identity, Guards(MicrosoftGuard(roles=["Admin"]), LinkedInGuard())()
        )
        is GuardOutcome.AUTHENTICATED
    )


async def test_anonymous_requires_explicit_branch_and_never_keeps_failed_claims():
    assert (
        evaluate_guards(None, Guards(MicrosoftGuard(), AllowAnonymous())())
        is GuardOutcome.ANONYMOUS
    )
    with pytest.raises(HTTPException):
        evaluate_guards(None, Guards(MicrosoftGuard(), LinkedInGuard())())
    identity = VerifiedIdentity(
        IdentityProvider.microsoft, {"scp": "api.read", "roles": []}
    )
    with pytest.raises(HTTPException):
        evaluate_guards(
            identity, Guards(MicrosoftGuard(roles=["User"]), AllowAnonymous())()
        )


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

    namespace._end_expired_socket.assert_awaited_once_with("socket")


@pytest.mark.anyio
async def test_socket_protected_policy_rejects_missing_cached_token():
    namespace = namespace_with(Guards(MicrosoftGuard())())
    namespace._get_token_payload_if_authenticated = AsyncMock(
        side_effect=ValueError("No cached token")
    )
    namespace._end_expired_socket = AsyncMock()

    with pytest.raises(SocketAuthenticationExpiredError):
        await namespace._get_current_user_and_check_guard("socket", "read")

    namespace._end_expired_socket.assert_awaited_once_with("socket")


@pytest.mark.anyio
async def test_socket_does_not_downgrade_failed_provider_requirements():
    namespace = namespace_with(
        Guards(MicrosoftGuard(roles=["User"]), AllowAnonymous())()
    )
    namespace._get_token_payload_if_authenticated = AsyncMock(
        return_value={"roles": []}
    )
    namespace._emit_status = AsyncMock()

    with pytest.raises(SocketAuthorizationFailedError):
        await namespace._get_current_user_and_check_guard("socket", "read")

    namespace._emit_status.assert_awaited_once_with(
        "socket", {"error": "access", "code": "authorization-failed"}
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
async def test_socket_cache_selects_linkedin_identity_token(monkeypatch):
    cache_json = Mock()
    cache_json.get.side_effect = lambda key, path=None: {
        ("session:session", "$.identityProvider"): ["linkedin"],
        ("session:session", "$.linkedinSubject"): ["member-sub"],
        ("linkedin:member-sub", None): {"idToken": "identity-token"},
    }[(key, path)]
    monkeypatch.setattr(
        "core.security.redis_session_client.json", Mock(return_value=cache_json)
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
