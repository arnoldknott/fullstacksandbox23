import json
import logging
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, List, Optional, cast

# from enum import Enum
# import asyncio
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from msal import ConfidentialClientApplication
from msal_extensions.persistence import BasePersistence
from msal_extensions.token_cache import PersistedTokenCache

from core.authentication import azure
from core.authentication.base import VerifiedIdentity
from core.cache import redis_session_client
from core.config import config
from core.types import (
    AllowAnonymous,  # noqa: F401 - public guard declaration interface
    CurrentUserData,
    GuardOutcome,
    GuardTypes,
    IdentityProvider,
    LinkedInGuard,  # noqa: F401 - public guard declaration interface
    MicrosoftGuard,  # noqa: F401 - public guard declaration interface
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


async def provide_http_token_payload(
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)],
) -> Optional[dict]:
    """Extract validated claims; the endpoint policy determines anonymous admission."""
    if token is None:
        return None
    try:
        return await azure.get_azure_token_payload(token)
    except Exception:
        logger.info("🔑 Token validation failed.")
        return None


async def get_http_access_token_payload(
    payload: dict = Depends(provide_http_token_payload),
) -> dict:
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
        result = redis_session_client.json().set(
            self.get_location(), ".", json.loads(content)
        )
        # print("===➡️ 🔑 token saved to cache in backend based on session_id ===")
        return json.dumps(result)

    def load(self):
        """Loads the token from the cache"""
        result = redis_session_client.json().get(self.get_location())
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
        List[Dict[str, Any]],
        redis_session_client.json().get(f"session:{session_id}", "$.microsoftAccount"),
    )
    if not user_account:
        raise ValueError("User account not found in session.")
    return user_account[0]


# TBD: write tests for this
async def get_azure_token_from_cache(
    user_account: Dict[str, Any], scopes: List[str] | None = None
) -> str | None:
    """Gets the azure token from the cache"""
    scopes = scopes or []
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
) -> dict:
    """Gets the azure token from the cache"""
    logger.info("🔑 Getting token from cache")
    user_account = await get_user_account_from_session_cache(session_id)

    # Can be extended to further identity service providers:
    token = await get_azure_token_from_cache(user_account, scopes)
    if not token:
        raise HTTPException(status_code=401, detail="No cached access token found.")
    payload = await azure.get_azure_token_payload(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token.")
    return payload

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


def evaluate_guards(
    identity: VerifiedIdentity | None, guards: GuardTypes
) -> GuardOutcome:
    """Return an explicit successful admission outcome; otherwise reject.

    Failed requirements on a verified provider never fall back to anonymous.
    Missing/invalid credentials may reach AllowAnonymous after extraction, retaining
    existing optional-authentication behavior without carrying unverified claims.
    """
    for guard in guards.alternatives:
        if isinstance(guard, AllowAnonymous):
            if identity is None:
                return GuardOutcome.ANONYMOUS
            continue
        if identity is None or guard.provider != identity.provider.value:
            continue
        if isinstance(guard, MicrosoftGuard) and not microsoft_requirements_match(
            identity.claims, guard
        ):
            continue
        return GuardOutcome.AUTHENTICATED
    raise HTTPException(status_code=401, detail="Invalid token.")


class Guards:
    """Callable endpoint policy; positional alternatives are combined with OR."""

    def __init__(self, *alternatives: ProviderGuard):
        self.policy = GuardTypes(alternatives=alternatives)

    def __call__(self) -> GuardTypes:
        """Return configuration, not a user or a validation result."""
        return self.policy

    async def check_http(
        self, payload: Optional[dict] = Depends(provide_http_token_payload)
    ) -> GuardOutcome:
        """Enforce router-wide admission without resolving a database user."""
        identity = (
            VerifiedIdentity(IdentityProvider.microsoft, payload) if payload else None
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
            tenant_id = self.payload["tid"]
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
        self, payload: dict = Depends(provide_http_token_payload)
    ) -> UserRead:
        super().__init__(payload)
        current_user, _ = await self.gets_or_signs_up_current_user()
        return current_user


async def check_token_against_guards(
    token_payload: Optional[dict] | VerifiedIdentity, guards: GuardTypes
) -> Optional[CurrentUserData]:
    """Evaluate outer admission, then resolve the user for existing CRUD checks."""
    if isinstance(token_payload, VerifiedIdentity):
        identity = token_payload
    elif token_payload:
        # Existing extraction functions already validate Microsoft tokens. This
        # adapter is for internal callers only; never pass undecoded request data.
        identity = VerifiedIdentity(IdentityProvider.microsoft, token_payload)
    else:
        identity = None

    admission = evaluate_guards(identity, guards)
    if admission is GuardOutcome.ANONYMOUS:
        return None
    assert identity is not None
    if identity.provider != IdentityProvider.microsoft:
        # Stage B supplies provider-specific signup. Until then no route enables
        # LinkedIn; fail closed if a premature caller declares it.
        raise HTTPException(status_code=503, detail="Provider signup is not enabled.")
    return await CurrentAccessToken(identity.claims).provides_current_user()


# endregion: Specific checks

# endregion: CHECKS
