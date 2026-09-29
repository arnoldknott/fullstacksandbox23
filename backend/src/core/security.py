import json
import logging
import jwt
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, List, Optional, cast
from uuid import UUID

# from enum import Enum
# import asyncio
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from msal import ConfidentialClientApplication
from msal_extensions.persistence import BasePersistence
from msal_extensions.token_cache import PersistedTokenCache

from core.authentication import azure, linkedin
from core.authentication.base import (
    ProviderValidator,
    VerifiedIdentity,
    verify_provider_token,
)
from core.cache import (
    get_protected_cache_value,
    get_session_value,
    redis_session_client,
    set_protected_cache_value,
)
from core.config import config
from core.types import AllowAnonymous  # noqa: F401 - public guard declaration interface
from core.types import LinkedInGuard  # noqa: F401 - public guard declaration interface
from core.types import MicrosoftGuard  # noqa: F401 - public guard declaration interface
from core.types import (
    CurrentUserData,
    GuardOutcome,
    GuardTypes,
    IdentityProvider,
    ProviderGuard,
)
from crud.identity import UserCRUD
from models.identity import UserRead

logger = logging.getLogger(__name__)

# CurrentUserData = types.CurrentUserData

# To get the swagger UI to work, add the OAuth2AuthorizationCodeBearer to the securitySchemes section of the openapi.json file
# https://github.com/tiangolo/fastapi/pull/797
# make the relevant routers dependent on it!
# currently the redirect URI cannot be passed through Swagger UI,
# so therefore manual token acquisition is necessary and SwaggerUI does not work with protected routes


# swagger-ui per default uses /docs/oauth2-redirect
# @router.get("/docs/oauth2-redirect")
# async def oauth_callback(code: str):
#     """Callback for the OAuth2 Authorization Code flow"""
#     logger.info("OAuth2 Authorization Code flow callback")
#     try:
#         print("=== code ===")
#         print(code)
#         # TBD: implement MSAL handling of retrieving a token from the code.
#     except Exception as err:
#         logger.error("OAuth2 Authorization Code flow callback failed.")
#         raise err


oauth2_config = {
    "authorizationUrl": f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/v2.0/authorize",
    "tokenUrl": f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/v2.0/token",
    "scopes": {
        # 'User.Read' : "Read user profile",
        # "openid": "OpenID Connect scope",
        # "profile": "Read user profile",
        # f"api://{config.API_SCOPE}/.default": "Minimum scopes for backendAPI",
        f"api://{config.API_SCOPE}/api.read": "Read API",
        f"api://{config.API_SCOPE}/api.write": "Write API",
        # f"api://{config.API_SCOPE}/socketio": "Socket.io",
    },
    "scheme_name": "OAuth2 Authorization Code",
    "description": "OAuth2 Authorization Code Bearer implementation for Swagger UI - identity provider is Microsoft Azure AD",
}

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    **oauth2_config,
)

oauth2_scheme_optional = OAuth2AuthorizationCodeBearer(
    **oauth2_config,
    auto_error=False,
)


async def _validate_azure_token(token: str) -> dict[str, Any]:
    payload = await azure.get_azure_token_payload(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid Microsoft token.")
    return cast(dict[str, Any], payload)


async def _validate_linkedin_token(token: str) -> dict[str, Any]:
    return await linkedin.get_linkedin_token_payload(
        token, client_id=cast(str, config.LINKEDIN_CLIENT_ID)
    )


def _provider_validators() -> dict[str, ProviderValidator]:
    return {
        cast(str, config.AZURE_ISSUER_URL): ProviderValidator(
            IdentityProvider.microsoft, _validate_azure_token
        ),
        linkedin.LINKEDIN_ISSUER: ProviderValidator(
            IdentityProvider.linkedin, _validate_linkedin_token
        ),
    }


SESSION_REFERENCE_HEADER = "X-Application-Session"


@dataclass
class SessionReferenceCredential:
    """An application session presented by the authenticated frontend service."""

    session_id: str
    candidates: tuple[VerifiedIdentity, ...] | None = field(
        default=None, repr=False, compare=False
    )
    loaded_scopes: frozenset[str] = field(
        default_factory=frozenset, repr=False, compare=False
    )
    expected_user_id: UUID | None = field(default=None, repr=False, compare=False)
    resolved_users: dict[IdentityProvider, CurrentUserData] = field(
        default_factory=dict, repr=False, compare=False
    )


async def _verify_frontend_service_token(token: str) -> None:
    """Require an app-only backend token issued specifically to the frontend app."""
    claims = await _validate_azure_token(token)
    caller = claims.get("azp") or claims.get("appid")
    app_only = claims.get("idtyp") == "app" or (
        claims.get("oid") is not None and claims.get("oid") == claims.get("sub")
    )
    if not app_only or caller != config.FRONTEND_SVELTE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Invalid frontend service token.")


async def provide_http_token_payload(
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)],
    x_application_session: Annotated[Optional[str], Header()] = None,
) -> Optional[VerifiedIdentity | SessionReferenceCredential]:
    """Extract and validate either a direct provider or trusted session credential."""
    if x_application_session is not None:
        if not x_application_session or token is None:
            raise HTTPException(status_code=401, detail="Invalid session credential.")
        try:
            session_id = str(UUID(x_application_session))
        except ValueError as error:
            raise HTTPException(
                status_code=401, detail="Invalid session credential."
            ) from error
        await _verify_frontend_service_token(token)
        return SessionReferenceCredential(session_id)
    if token is None:
        return None
    try:
        return await verify_provider_token(token, _provider_validators())
    except Exception:
        logger.info("🔑 Token validation failed.")
        return None


async def verify_access_token(token: str) -> VerifiedIdentity:
    """Validate an explicit bearer token through the configured provider allowlist."""
    return await verify_provider_token(token, _provider_validators())


async def get_http_access_token_payload(
    payload: VerifiedIdentity | SessionReferenceCredential | dict | None = Depends(
        provide_http_token_payload
    ),
) -> VerifiedIdentity | SessionReferenceCredential | dict:
    """General function to get the access token payload"""
    # can later be used for customizing different identity service providers
    if payload is None:
        # TBD: check if there is test for this to fire!
        raise HTTPException(status_code=401, detail="Invalid token.")
    return payload


# raise Exception("Backend does not support saving tokens")

# region: Token from Cache through Session


class RedisPersistence(BasePersistence):
    """Redis persistence class for the token cache"""

    def __init__(self, user_account):
        self.user_account = user_account

    def save(self, content):  # type: ignore[override]
        """Saves the token to the cache"""
        # raise Exception("Backend does not support saving tokens")
        result = set_protected_cache_value(self.get_location(), json.loads(content))
        # print("===➡️ 🔑 token saved to cache in backend based on session_id ===")
        return json.dumps(result)

    def load(self):
        """Loads the token from the cache"""
        result = get_protected_cache_value(self.get_location())
        # print("===⬅️ 🔑 token loaded from cache in backend based on session_id ===")
        return json.dumps(result)

    def get_location(self):
        """Returns the location in the cache"""
        location = f"msal:{self.user_account['homeAccountId']}"
        return location

    def time_last_modified(self):
        """Returns the time the cache was last modified"""
        try:
            # `redis_session_client` is the sync client; `.object()` is typed as a
            # `ResponseT` union to support the async client too. Narrow to int here.
            idle_time = cast(
                Optional[int],
                redis_session_client.object("idletime", self.get_location()),
            )
            if idle_time:
                last_accessed_time = datetime.now() - timedelta(seconds=idle_time)
                return last_accessed_time.timestamp()
            else:
                return datetime.now().timestamp()
        except Exception:
            logger.error("🔑 Failed to get last modified time for cached token")
            raise Exception("no modification time available")


def get_persistent_cache(user_account):
    """Returns the persistent cache for the user account"""
    persistence = RedisPersistence(user_account)
    persistedTokenCache = PersistedTokenCache(persistence)
    return persistedTokenCache


# TBD: write tests for this
async def get_user_account_from_session_cache(session_id: str) -> Dict[str, Any]:
    """Gets the user account from the cache"""
    logger.info("🔑 Getting user account from cache")
    user_account = cast(
        Optional[Dict[str, Any]], get_session_value(session_id, "$.microsoftAccount")
    )
    if not user_account:
        raise ValueError("User account not found in session.")
    return user_account


# TBD: write tests for this
async def get_azure_token_from_cache(
    user_account: Dict[str, Any], scopes: List[str] | None = None
) -> str | None:
    """Gets the azure token from the cache"""
    # A Microsoft guard without explicit scope requirements still needs an API
    # audience when asking MSAL for a silent access token.
    scopes = scopes or [f"api://{config.API_SCOPE}/api.read"]
    # Create the PersistentTokenCache
    cache = get_persistent_cache(user_account)
    msal_conf_client = ConfidentialClientApplication(
        client_id=config.FRONTEND_SVELTE_CLIENT_ID,
        client_credential=config.FRONTEND_SVELTE_CLIENT_SECRET,
        authority=config.AZURE_AUTHORITY,
        token_cache=cache,
    )

    accounts = msal_conf_client.get_accounts(user_account["username"])
    for account in accounts:
        # TBD: change into scopes:
        # result = msal_conf_client.acquire_token_silent(["User.Read"], account=account)
        result = msal_conf_client.acquire_token_silent(scopes, account=account)
        if result and "access_token" in result:
            # print("===🔑 azure access_token from cache - access-token ===")
            # print(result["access_token"])
            return result["access_token"]
    return None


async def get_token_payload_from_cache(
    session_id: str, scopes: List[str] | None = None
) -> VerifiedIdentity:
    """Load the preferred currently valid provider credential for a server session."""
    logger.info("🔑 Getting token from cache")
    candidates = await load_session_provider_candidates(session_id, scopes)
    if not candidates:
        raise HTTPException(status_code=401, detail="No cached provider token found.")
    return candidates[0]

    # # Create the PersistentTokenCache
    # cache = get_persistent_cache(user_account)
    # msal_conf_client = ConfidentialClientApplication(
    #     client_id=config.FRONTEND_SVELTE_CLIENT_ID,
    #     client_credential=config.FRONTEND_SVELTE_CLIENT_SECRET,
    #     authority=config.AZURE_AUTHORITY,
    #     token_cache=cache,
    # )

    # accounts = msal_conf_client.get_accounts(user_account["username"])
    # for account in accounts:
    #     # TBD: change into scopes:
    #     # result = msal_conf_client.acquire_token_silent(["User.Read"], account=account)
    #     result = msal_conf_client.acquire_token_silent(scopes, account=account)
    #     if "access_token" in result:
    #         print("===🔑 azure access_token from cache - access-token ===")
    #         # print(result["access_token"])
    #         return result["access_token"]
    # return None


# async def get_http_access_token_payload(
#     payload: dict = Depends(provide_http_token_payload),
# ) -> dict:
#     """General function to get the access token payload"""
#     # can later be used for customizing different identity service providers
#     return payload


# endregion: Token from Cache through Session

# region: GUARDS


async def load_session_provider_candidates(  # noqa: C901
    session_id: str, scopes: List[str] | None = None
) -> tuple[VerifiedIdentity, ...]:
    """Load every currently valid provider identity referenced by a session.

    An absent or expired provider credential is unavailable and does not prevent another
    linked provider from authenticating. Cache decryption and storage failures propagate:
    they are service failures, not evidence that a credential is merely unavailable.
    """
    candidates: list[VerifiedIdentity] = []

    user_account = get_session_value(session_id, "$.microsoftAccount")
    if isinstance(user_account, dict):
        cached_token = get_session_value(session_id, "$.microsoftBackendAccessToken")
        token = (
            cached_token.get("accessToken") if isinstance(cached_token, dict) else None
        )
        if isinstance(token, str):
            try:
                payload = await azure.get_azure_token_payload(token)
            except (HTTPException, jwt.PyJWTError) as error:
                if isinstance(error, HTTPException) and error.status_code != 401:
                    raise
                payload = None
            if payload is not None:
                candidates.append(VerifiedIdentity(IdentityProvider.microsoft, payload))

    subject = get_session_value(session_id, "$.linkedinSubject")
    if isinstance(subject, str) and subject:
        cached = get_protected_cache_value(f"linkedin:{subject}")
        token = cached.get("idToken") if isinstance(cached, dict) else None
        if isinstance(token, str):
            try:
                claims = await linkedin.get_linkedin_token_payload(
                    token,
                    client_id=cast(str, config.LINKEDIN_CLIENT_ID),
                )
            except HTTPException as error:
                if error.status_code != 401:
                    raise
            else:
                if claims.get("sub") != subject:
                    raise HTTPException(
                        status_code=401, detail="LinkedIn session subject mismatch."
                    )
                candidates.append(VerifiedIdentity(IdentityProvider.linkedin, claims))

    return tuple(candidates)


async def load_session_credential_candidates(
    credential: SessionReferenceCredential, scopes: List[str] | None = None
) -> tuple[VerifiedIdentity, ...]:
    """Load session candidates once per request and expand scopes only when required."""
    requested_scopes = frozenset(scopes or ())
    if (
        credential.candidates is not None
        and requested_scopes <= credential.loaded_scopes
    ):
        return credential.candidates

    combined_scopes = sorted(credential.loaded_scopes | requested_scopes)
    credential.candidates = await load_session_provider_candidates(
        credential.session_id, combined_scopes
    )
    credential.loaded_scopes = frozenset(combined_scopes)
    credential.resolved_users.clear()
    return credential.candidates


def microsoft_requirements_match(
    claims: Mapping[str, Any], guard: MicrosoftGuard
) -> bool:
    """Scope/role/group membership is exact; preserve the Microsoft Admin role override."""
    raw_scopes = claims.get("scp", "")
    scopes = raw_scopes.split() if isinstance(raw_scopes, str) else []
    roles = claims.get("roles", [])
    groups = claims.get("groups", [])
    roles = roles if isinstance(roles, list) else []
    groups = groups if isinstance(groups, list) else []
    return (
        all(scope in scopes for scope in guard.scopes)
        and all(role in roles or "Admin" in roles for role in guard.roles)
        and all(str(group) in groups for group in guard.groups)
    )


def select_provider_candidate(
    candidates: tuple[VerifiedIdentity, ...], guards: GuardTypes
) -> VerifiedIdentity | None:
    """Select one independently valid identity in guard declaration order."""
    by_provider = {candidate.provider: candidate for candidate in candidates}
    for guard in guards.alternatives:
        if isinstance(guard, AllowAnonymous):
            continue
        candidate = by_provider.get(IdentityProvider(guard.provider))
        if candidate is None:
            continue
        if isinstance(guard, MicrosoftGuard) and not microsoft_requirements_match(
            candidate.claims, guard
        ):
            continue
        return candidate
    if guards.allows_anonymous:
        return None
    raise HTTPException(status_code=401, detail="Invalid token.")


def microsoft_scopes_for_guards(guards: GuardTypes) -> list[str]:
    """Translate declared Microsoft guard scopes to the cached token audience."""
    scopes: list[str] = []
    for guard in guards.alternatives:
        if not isinstance(guard, MicrosoftGuard):
            continue
        for scope in guard.scopes:
            qualified = f"api://{config.API_SCOPE}/{scope}"
            if qualified not in scopes:
                scopes.append(qualified)
    return scopes


def evaluate_guards(
    identity: VerifiedIdentity | None, guards: GuardTypes
) -> GuardOutcome:
    """Return an explicit successful admission outcome; otherwise reject.

    Provider alternatives are evaluated in declaration order. AllowAnonymous is always
    the final fallback and never carries verified or unverified claims into user data.
    """
    for guard in guards.alternatives:
        if isinstance(guard, AllowAnonymous):
            continue
        if identity is None or guard.provider != identity.provider.value:
            continue
        if isinstance(guard, MicrosoftGuard) and not microsoft_requirements_match(
            identity.claims, guard
        ):
            continue
        return GuardOutcome.AUTHENTICATED
    if guards.allows_anonymous:
        return GuardOutcome.ANONYMOUS
    raise HTTPException(status_code=401, detail="Invalid token.")


class Guards:
    """Callable endpoint policy; positional alternatives are combined with OR."""

    def __init__(self, *alternatives: ProviderGuard):
        self.policy = GuardTypes(alternatives=alternatives)

    def __call__(self) -> GuardTypes:
        """Return configuration, not a user or a validation result."""
        return self.policy

    async def check_http(
        self,
        request: Request,
        payload: VerifiedIdentity | SessionReferenceCredential | dict | None = Depends(
            provide_http_token_payload
        ),
    ) -> GuardOutcome:
        """Enforce router-wide admission without resolving a database user."""
        if isinstance(payload, SessionReferenceCredential):
            if get_session_value(payload.session_id, "$.currentUser") is None:
                if request.url.path.rstrip("/") != "/api/v1/user/me":
                    raise HTTPException(
                        status_code=401, detail="Session user not found."
                    )
                candidates = await load_session_credential_candidates(
                    payload, microsoft_scopes_for_guards(self.policy)
                )
                if len(candidates) != 1:
                    raise HTTPException(
                        status_code=401, detail="Invalid signup session."
                    )
                selected = select_provider_candidate(candidates, self.policy)
                return (
                    GuardOutcome.AUTHENTICATED
                    if selected is not None
                    else GuardOutcome.ANONYMOUS
                )
            selected, _ = await authorize_session_credential(
                payload,
                self.policy,
                microsoft_scopes_for_guards(self.policy),
            )
            return (
                GuardOutcome.AUTHENTICATED
                if selected is not None
                else GuardOutcome.ANONYMOUS
            )
        identity = (
            payload
            if isinstance(payload, VerifiedIdentity)
            else (
                VerifiedIdentity(IdentityProvider.microsoft, payload)
                if payload
                else None
            )
        )
        return evaluate_guards(identity, self.policy)


# endregion: GUARDS


# region: CHECKS:
#
# region: Generic check usage:
#
class CurrentAccessToken:
    """class for all checks related to the current access token"""

    def __init__(self, payload) -> None:
        self.payload = payload

    async def is_valid(self, require=True):
        """Checks if the current token is valid"""
        if self.payload:
            return True
        else:
            if require:
                raise HTTPException(status_code=401, detail="Invalid token.")
            else:
                return False

    async def has_scope(self, scope: str, require=True) -> bool:
        """Checks if the current token includes a specific scope"""
        payload = self.payload
        if (
            payload
            and isinstance(payload.get("scp"), str)
            and scope in payload["scp"].split()
        ):
            return True
        else:
            if require:
                raise HTTPException(status_code=401, detail="Invalid token.")
                # raise HTTPException(status_code=403, detail="Access denied")
            else:
                return False

    async def has_role(self, role: str, require=True) -> bool:
        """Checks if the current token includes a specific scope"""
        payload = self.payload
        # if ("roles" in payload) and (role in payload["roles"]):
        # TBD: add the "Admin" override: if the user has the Admin role, the user has access to everything
        if ("roles" in payload) and (
            (role in payload["roles"]) or ("Admin" in payload["roles"])
        ):
            return True
        else:
            if require:
                raise HTTPException(status_code=401, detail="Invalid token.")
                # raise HTTPException(status_code=403, detail="Access denied")
            else:
                return False

    # TBD: implement tests for this:
    async def has_group(self, group: str, require=True) -> bool:
        """Checks if the current token includes a group"""
        payload = self.payload
        if ("groups" in payload) and (group in payload["groups"]):
            return True
        else:
            if require:
                raise HTTPException(status_code=401, detail="Invalid token.")
                # raise HTTPException(status_code=403, detail="Access denied")
            else:
                return False

    # This is responsible for self-sign on: if a user has a token, the user is allowed
    # Who gets the tokens is controlled by the identity provider (Azure AD)
    # Can be through membership in a group, which has access to the application
    # -> in Azure portal under Enterprise applications,
    # -> turn of filter enterprise applications and
    # -> search for the backend application registration
    # -> under users and groups add the users or groups:
    # -> gives and revokes access for users and groups based on roles
    #
    # TBD: make sure this one get's triggered from all checks that require a user
    async def gets_or_signs_up_current_user(self) -> tuple[UserRead, int]:
        """Checks user in database, if not adds user (self-sign-up) and adds or updates the group membership of the user"""
        groups = []
        try:
            if "groups" in self.payload:
                groups = self.payload["groups"]
            user_id = self.payload["oid"]  # this is the azure_user_id!
            tenant_id = UUID(str(self.payload["tid"]))
            if tenant_id != UUID(config.AZURE_TENANT_ID):
                raise HTTPException(status_code=401, detail="Invalid Microsoft tenant.")
            # TBD move the crud operations to the base view class, which should have an instance of the checks class.
            # if the user information stored in this class is already valid - no need to make another database call
            # if the user information stored in this class is not valid: get or sign-up the user.
            async with UserCRUD() as crud:
                # TBD: this variable is misleading. The current_user here is not CurrentUserData, but a UserRead object!
                current_user, status_code = await crud.azure_user_self_sign_up(
                    user_id, tenant_id, groups
                )
                if current_user:
                    # TBD: more important than returning: store the user in the class instance: attribute self.current_user
                    # print("=== current_user ===")
                    # print(current_user)
                    # TBD: no - don't do that - it's a security risk to store the user in the class instance!
                    # self.user_id = current_user.user_id
                    return current_user, status_code
                else:
                    raise HTTPException(status_code=404, detail="404 User not found")
        except Exception as err:
            logger.error(f"🔑 User not found in database: ${err}")
            raise HTTPException(status_code=401, detail="Invalid token.")

    # call provide_current_user from all checks that require a user
    async def provides_current_user(self) -> CurrentUserData:
        """Returns the current user"""
        roles = None
        groups = None
        if "roles" in self.payload:
            roles = self.payload["roles"]
        if "groups" in self.payload:
            groups = self.payload["groups"]
        user_in_database, _ = await self.gets_or_signs_up_current_user()
        # TBD: use CurrentUserData class instead of dict for type safety!
        current_user = CurrentUserData(
            user_id=user_in_database.id,
            azure_token_roles=roles,
            azure_token_groups=groups,
        )
        # current_user = {
        #     # Then change azure_user_id to user_id here:
        #     # "azure_user_id": self.payload["oid"],
        #     "user_id": user_in_database.id,
        #     "roles": roles,
        #     "groups": groups,
        #     # "scopes": self.payload["scp"],
        # }
        # current_user = CurrentUserData()
        # current_user.azure_user_id = self.payload["oid"]
        # current_user.azure_token_roles = self.payload["roles"]
        # current_user.azure_token_groups = self.payload["groups"]
        # current_user.azure_token_scopes = self.payload["scp"]
        # return CurrentUserData(**current_user)
        return current_user


class CurrentAzureUserInDatabase(CurrentAccessToken):
    """Checks user in database, if not adds user (self-sign-up) and adds or updates the group membership of the user"""

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        payload: VerifiedIdentity | dict | None = Depends(provide_http_token_payload),
    ) -> UserRead:
        if isinstance(payload, VerifiedIdentity):
            if payload.provider != IdentityProvider.microsoft:
                raise HTTPException(
                    status_code=401, detail="Microsoft identity required."
                )
            claims = payload.claims
        elif isinstance(payload, dict):
            claims = payload
        else:
            raise HTTPException(status_code=401, detail="Invalid token.")
        super().__init__(claims)
        current_user, _ = await self.gets_or_signs_up_current_user()
        return current_user


async def resolve_verified_identity_with_status(
    identity: VerifiedIdentity,
) -> tuple[CurrentUserData, int]:
    """Resolve one verified provider identity to its internal active user."""
    if identity.provider == IdentityProvider.linkedin:
        subject = identity.claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise HTTPException(status_code=401, detail="Invalid LinkedIn subject.")
        async with UserCRUD() as crud:
            user, status_code = await crud.linkedin_user_self_sign_up(subject)
        return (
            CurrentUserData(
                user_id=user.id, azure_token_roles=[], azure_token_groups=[]
            ),
            status_code,
        )
    if identity.provider == IdentityProvider.microsoft:
        token = CurrentAccessToken(identity.claims)
        user, status_code = await token.gets_or_signs_up_current_user()
        roles = identity.claims.get("roles")
        groups = identity.claims.get("groups")
        return (
            CurrentUserData(
                user_id=user.id,
                azure_token_roles=roles if isinstance(roles, list) else None,
                azure_token_groups=groups if isinstance(groups, list) else None,
            ),
            status_code,
        )
    raise HTTPException(status_code=401, detail="Unsupported identity provider.")


async def resolve_session_identity(identity: VerifiedIdentity) -> CurrentUserData:
    """Resolve an established-session identity without performing any writes."""
    async with UserCRUD() as crud:
        if identity.provider == IdentityProvider.linkedin:
            subject = identity.claims.get("sub")
            if not isinstance(subject, str) or not subject:
                raise HTTPException(status_code=401, detail="Invalid LinkedIn subject.")
            user = await crud.resolve_existing_provider_user(linkedin_user_id=subject)
            return CurrentUserData(
                user_id=user.id, azure_token_roles=[], azure_token_groups=[]
            )
        if identity.provider == IdentityProvider.microsoft:
            oid = identity.claims.get("oid")
            tenant = identity.claims.get("tid")
            try:
                azure_user_id = UUID(str(oid))
                azure_tenant_id = UUID(str(tenant))
            except (TypeError, ValueError) as error:
                raise HTTPException(
                    status_code=401, detail="Invalid Microsoft identity."
                ) from error
            if azure_tenant_id != UUID(cast(str, config.AZURE_TENANT_ID)):
                raise HTTPException(status_code=401, detail="Invalid Microsoft tenant.")
            user = await crud.resolve_existing_provider_user(
                azure_user_id=azure_user_id,
                azure_tenant_id=azure_tenant_id,
            )
            roles = identity.claims.get("roles")
            groups = identity.claims.get("groups")
            return CurrentUserData(
                user_id=user.id,
                azure_token_roles=roles if isinstance(roles, list) else None,
                azure_token_groups=groups if isinstance(groups, list) else None,
            )
    raise HTTPException(status_code=401, detail="Unsupported identity provider.")


def require_session_user_id(session_id: str) -> UUID:
    """Validate session integrity before any authenticated or anonymous admission."""
    session_user = get_session_value(session_id, "$.currentUser")
    session_user_id = session_user.get("id") if isinstance(session_user, dict) else None
    try:
        return UUID(str(session_user_id))
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=401, detail="Session user not found."
        ) from error


async def authorize_session_candidates(
    session_id: str,
    candidates: tuple[VerifiedIdentity, ...],
    guards: GuardTypes,
) -> tuple[VerifiedIdentity | None, CurrentUserData | None]:
    """Bind all valid session credentials to one user and select one for a policy."""
    expected_user_id = require_session_user_id(session_id)

    resolved: dict[IdentityProvider, CurrentUserData] = {}
    for candidate in candidates:
        current_user = await resolve_session_identity(candidate)
        if current_user.user_id != expected_user_id:
            raise HTTPException(
                status_code=401, detail="Session provider identity mismatch."
            )
        resolved[candidate.provider] = current_user

    try:
        selected = select_provider_candidate(candidates, guards)
    except HTTPException as error:
        available = {candidate.provider.value for candidate in candidates}
        missing_provider = next(
            (
                guard.provider
                for guard in guards.alternatives
                if not isinstance(guard, AllowAnonymous)
                and guard.provider not in available
            ),
            None,
        )
        if error.status_code != 401 or missing_provider is None:
            raise
        raise HTTPException(
            status_code=401,
            detail={
                "error": "authentication",
                "code": "provider-token-required",
                "provider": missing_provider,
            },
        ) from error
    return selected, resolved[selected.provider] if selected is not None else None


async def authorize_session_credential(
    credential: SessionReferenceCredential,
    guards: GuardTypes,
    scopes: List[str] | None = None,
) -> tuple[VerifiedIdentity | None, CurrentUserData | None]:
    """Bind and select session credentials using request-scoped cached validation."""
    if credential.expected_user_id is None:
        credential.expected_user_id = require_session_user_id(credential.session_id)
    candidates = await load_session_credential_candidates(credential, scopes)

    for candidate in candidates:
        if candidate.provider in credential.resolved_users:
            continue
        current_user = await resolve_session_identity(candidate)
        if current_user.user_id != credential.expected_user_id:
            raise HTTPException(
                status_code=401, detail="Session provider identity mismatch."
            )
        credential.resolved_users[candidate.provider] = current_user

    selected = select_provider_candidate(candidates, guards)
    return (
        selected,
        credential.resolved_users[selected.provider] if selected is not None else None,
    )


async def authorize_session(
    session_id: str, guards: GuardTypes, scopes: List[str] | None = None
) -> tuple[VerifiedIdentity | None, CurrentUserData | None]:
    """Load, bind, and select session credentials for one guarded operation."""
    return await authorize_session_credential(
        SessionReferenceCredential(session_id), guards, scopes
    )


async def resolve_session_provider_identity(
    credential: SessionReferenceCredential | str,
    excluded_provider: IdentityProvider | None = None,
) -> VerifiedIdentity:
    """Select an explicit provider proof for account link or unlink operations."""
    if isinstance(credential, str):
        credential = SessionReferenceCredential(credential)
    session_id = credential.session_id
    active_provider = get_session_value(session_id, "$.identityProvider")
    scopes = [f"api://{config.API_SCOPE}/api.read"]
    if excluded_provider is None:
        try:
            provider = IdentityProvider(str(active_provider))
        except ValueError as error:
            raise HTTPException(
                status_code=401, detail="Session identity provider not found."
            ) from error
        expected_user_id = require_session_user_id(session_id)
        candidates = await load_session_credential_candidates(credential, scopes)
        identity = next(
            (candidate for candidate in candidates if candidate.provider == provider),
            None,
        )
        if identity is None:
            raise HTTPException(status_code=401, detail="Provider identity required.")
        current_user = await resolve_session_identity(identity)
        if current_user.user_id != expected_user_id:
            raise HTTPException(
                status_code=401, detail="Session provider identity mismatch."
            )
        return identity

    provider_order = [
        provider
        for provider in [IdentityProvider.microsoft, IdentityProvider.linkedin]
        if provider != excluded_provider
    ]
    alternatives: list[ProviderGuard] = [
        MicrosoftGuard() if provider == IdentityProvider.microsoft else LinkedInGuard()
        for provider in provider_order
    ]
    guards = GuardTypes(alternatives=tuple(alternatives))
    identity, _ = await authorize_session_credential(credential, guards, scopes)
    if identity is None:
        raise HTTPException(status_code=401, detail="Provider identity required.")
    return identity


async def check_token_against_guards_with_status(
    token_payload: Optional[dict] | VerifiedIdentity | SessionReferenceCredential,
    guards: GuardTypes,
) -> tuple[Optional[CurrentUserData], Optional[int]]:
    """Evaluate outer admission and resolve the user with signup status."""
    if isinstance(token_payload, SessionReferenceCredential):
        session_user = get_session_value(token_payload.session_id, "$.currentUser")
        if session_user is not None:
            _, current_user = await authorize_session_credential(
                token_payload, guards, microsoft_scopes_for_guards(guards)
            )
            return current_user, None
        candidates = await load_session_credential_candidates(
            token_payload, microsoft_scopes_for_guards(guards)
        )
        if len(candidates) != 1:
            raise HTTPException(status_code=401, detail="Invalid signup session.")
        identity = select_provider_candidate(candidates, guards)
        if identity is None:
            return None, None
        return await resolve_verified_identity_with_status(identity)
    if isinstance(token_payload, VerifiedIdentity):
        identity = token_payload
    elif token_payload:
        identity = VerifiedIdentity(IdentityProvider.microsoft, token_payload)
    else:
        identity = None

    admission = evaluate_guards(identity, guards)
    if admission is GuardOutcome.ANONYMOUS:
        return None, None
    assert identity is not None
    return await resolve_verified_identity_with_status(identity)


async def check_token_against_guards(
    token_payload: Optional[dict] | VerifiedIdentity | SessionReferenceCredential,
    guards: GuardTypes,
) -> Optional[CurrentUserData]:
    """Evaluate outer admission, then resolve the user for existing CRUD checks."""
    if isinstance(token_payload, SessionReferenceCredential):
        _, current_user = await authorize_session_credential(
            token_payload, guards, microsoft_scopes_for_guards(guards)
        )
        return current_user
    if isinstance(token_payload, VerifiedIdentity):
        identity = token_payload
    elif token_payload:
        identity = VerifiedIdentity(IdentityProvider.microsoft, token_payload)
    else:
        identity = None

    admission = evaluate_guards(identity, guards)
    if admission is GuardOutcome.ANONYMOUS:
        return None
    assert identity is not None
    if identity.provider == IdentityProvider.linkedin:
        subject = identity.claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise HTTPException(status_code=401, detail="Invalid LinkedIn subject.")
        async with UserCRUD() as crud:
            user, _ = await crud.linkedin_user_self_sign_up(subject)
        return CurrentUserData(
            user_id=user.id, azure_token_roles=[], azure_token_groups=[]
        )
    if identity.provider == IdentityProvider.microsoft:
        return await CurrentAccessToken(identity.claims).provides_current_user()
    raise HTTPException(status_code=401, detail="Unsupported identity provider.")


# endregion: Specific checks

# endregion: CHECKS
