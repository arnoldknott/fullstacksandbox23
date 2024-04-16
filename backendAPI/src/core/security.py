import json
import logging


# import asyncio
import httpx
import jwt

# from enum import Enum
from uuid import UUID

from typing import Optional, List
from core.types import CurrentUserData, GuardTypes
from core.cache import redis_jwks_client
from core.config import config
from models.identity import UserRead
from crud.identity import UserCRUD
from fastapi import Depends, HTTPException, Request
from jwt.algorithms import RSAAlgorithm

# from typing import List, Optional
# from uuid import UUID


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


# Helper function for get_token_payload:
async def get_azure_jwks(no_cache: bool = False):
    """Fetches the JWKs from identity provider"""
    logger.info("🔑 Fetching JWKs")
    try:
        if no_cache is False:
            # print("=== no_cache ===")
            # print(no_cache)
            jwks = redis_jwks_client.json().get("jwks")
            # print("=== jwks ===")
            # print(jwks)
            if jwks:
                # print("=== 🔑 JWKS fetched from cache ===")
                return json.loads(jwks)
            else:
                await get_azure_jwks(no_cache=True)
        else:
            logger.info("🔑 Getting JWKs from Azure")
            oidc_config = httpx.get(config.AZURE_OPENID_CONFIG_URL).json()
            print("=== 🔑 got JWKs from Azure ===")
            if oidc_config is False:
                raise HTTPException(
                    status_code=404, detail="Failed to fetch Open ID config."
                )
            try:
                jwks = httpx.get(oidc_config["jwks_uri"]).json()
            except Exception as err:
                raise HTTPException(
                    status_code=404, detail=f"Failed to fetch JWKS online ${err}"
                )
            try:
                # TBD: for real multi-tenant applications, the cache-key should be tenant specific
                redis_jwks_client.json().set("jwks", ".", json.dumps(jwks))
                logger.info("🔑 Setting JWKs in cache")
                print("=== 🔑 JWKS set in cache ===")
                return jwks
            except Exception as err:
                raise HTTPException(
                    status_code=404, detail=f"Failed to set JWKS in redis: ${err}"
                )
    except Exception as err:
        logger.error("🔑 Failed to get JWKS.")
        raise err


async def decode_token(token: str, jwks: dict) -> dict:
    """Decodes the token"""
    # Get the key that matches the kid:
    kid = jwt.get_unverified_header(token)["kid"]
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == kid:
            rsa_key = RSAAlgorithm.from_jwk(key)
    logger.info("Decoding token")
    # validate the token
    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience=config.API_SCOPE,
        issuer=config.AZURE_ISSUER_URL,
        options={
            "validate_iss": True,
            "validate_aud": True,
            "validate_exp": True,
            "validate_nbf": True,
            "validate_iat": True,
        },
    )
    logger.info("Token decoded successfully")
    return payload


async def get_azure_token_payload(request: Request) -> Optional[dict]:
    """Validates the Azure access token sent in the request header and returns the payload if valid"""
    logger.info("🔑 Validating token")
    try:
        auth_header = request.headers.get("Authorization")
        token = auth_header.split("Bearer ")[1]
        if token:
            try:
                jwks = await get_azure_jwks()
                payload = await decode_token(token, jwks)
                return payload
            except Exception:
                logger.info(
                    "🔑 Failed to validate token, fetching new JWKS and trying again."
                )
                jwks = await get_azure_jwks(no_cache=True)
                payload = await decode_token(token, jwks)
                return payload

    except Exception as e:
        logger.error(f"🔑 Token validation failed: ${e}")
        return None
        # raise HTTPException(status_code=401, detail="Invalid token")


# TBD: implement tests for this:
async def optional_get_access_token_payload(
    payload=Depends(get_azure_token_payload),
) -> Optional[dict]:
    """General function to get the access token payload optionally"""
    # can later be used for customizing different identity service providers
    return payload
    # try:
    #     return await get_azure_token_payload(request)
    # except HTTPException as err:
    #     if err.status_code == 401:
    #         return None
    #     else:
    #         raise err


async def get_access_token_payload(
    payload: dict = Depends(optional_get_access_token_payload),
) -> dict:
    """General function to get the access token payload"""
    # can later be used for customizing different identity service providers
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token.")
    return payload


# async def get_access_token_payload(
#     payload: dict = Depends(get_azure_token_payload),
# ) -> dict:
#     """General function to get the access token payload"""
#     # can later be used for customizing different identity service providers
#     return payload


# region: GUARDS


class Guards:
    """Decorator to protect the routes with scopes, roles and groups."""

    def __init__(
        self, scopes: List[str] = [], roles: List[str] = [], groups: List[UUID] = []
    ):
        """Initializes the guards for the routes."""
        self.scopes = scopes
        self.roles = roles
        self.groups = groups

    def __call__(self):
        """Returns the guards for the routes."""
        protectors = GuardTypes(
            scopes=self.scopes, roles=self.roles, groups=self.groups
        )
        return protectors


# endregion: GUARDS

# region: CHECKS:
#
# region: Generic check usage:
#
# Use those classes directly as checks, e.g.:
#
# @router.post("/", status_code=201)
# async def post_user(
#     user: ProtectedResourceCreate,
#     token_payload=Depends(get_access_token_payload),
# ) -> ProtectedResource:
#     """Creates a new user."""
#     logger.info("POST user")
#     token = CurrentAccessToken(token_payload)
#     await token.has_scope("api.write")
#     await token.has_role("User")
#     async with ProtectedResourceCRUD() as crud:
#         created_user = await crud.create(user)
#     return created_user


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
        if ("scp" in payload) and (scope in payload["scp"]):
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
    async def gets_or_signs_up_current_user(self) -> UserRead:
        """Checks user in database, if not adds user (self-sign-up) and adds or updates the group membership of the user"""
        groups = []
        try:
            if "groups" in self.payload:
                groups = self.payload["groups"]
            user_id = self.payload["oid"]
            tenant_id = self.payload["tid"]
            # TBD move the crud operations to the base view class, which should have an instance of the checks class.
            # if the user information stored in this class is already valid - no need to make another database call
            # if the user information stored in this class is not valid: get or sign-up the user.
            async with UserCRUD() as crud:
                # TBD: this varialbe is misleading. The current_user here is not CurrentUserData, but a UserRead object!
                current_user = await crud.create_azure_user_and_groups_if_not_exist(
                    user_id, tenant_id, groups
                )
                if current_user:
                    # TBD: more important than returning: store the user in the class instance: attribute self.current_user
                    # print("=== current_user ===")
                    # print(current_user)
                    # TBD: no - don't do that - it's a security risk to store the user in the class instance!
                    # self.user_id = current_user.user_id
                    return current_user
                else:
                    raise HTTPException(status_code=404, detail="404 User not found")
        except Exception as err:
            logger.error(f"🔑 User not found in database: ${err}")
            raise HTTPException(status_code=401, detail="Invalid token.")

    # TBD: call get_or_sign_up_current_user from all checks that require a user
    # TBD: merge with gets_or_signs_up_current_user?
    async def provides_current_user(self) -> CurrentUserData:
        """Returns the current user"""
        roles = None
        groups = None
        if "roles" in self.payload:
            roles = self.payload["roles"]
        if "groups" in self.payload:
            groups = self.payload["groups"]
        user_in_database = await self.gets_or_signs_up_current_user()
        # TBD: use CurrentUserData class instead of dict for type safety!
        current_user = CurrentUserData(
            user_id=user_in_database.id,
            roles=roles,
            groups=groups,
        )
        # current_user = {
        #     # TBD: every check needs to call the gets_or_signs_up_current_user method
        #     # Then change azure_user_id to user_id here:
        #     # "azure_user_id": self.payload["oid"],
        #     "user_id": user_in_database.id,
        #     "roles": roles,
        #     "groups": groups,
        #     # "scopes": self.payload["scp"],
        # }
        # current_user = CurrentUserData()
        # current_user.azure_user_id = self.payload["oid"]
        # current_user.roles = self.payload["roles"]
        # current_user.groups = self.payload["groups"]
        # current_user.scopes = self.payload["scp"]
        # return CurrentUserData(**current_user)
        return current_user

    # Fine-grained access control is taking care of this!
    # If used, implement tests for this:
    # async def azure_self_or_admin(self, azure_user_id: UUID, require=True) -> bool:
    #     """Checks if the current user is the user_id or an admin"""
    #     payload = self.payload
    #     user_has_admin_role = await self.has_role("Admin", require=False)
    #     try:
    #         azure_user_id = UUID(azure_user_id)
    #     except ValueError:
    #         logger.error("ID is not a universal unique identifier (uuid).")
    #         raise HTTPException(status_code=400, detail="Invalid id.")
    #     if user_has_admin_role:
    #         return True
    #     elif payload["oid"] == azure_user_id:
    #         return True
    #     else:
    #         if require:
    #             raise HTTPException(status_code=403, detail="Access denied")
    #         else:
    #             return False

    # Fine-grained access control is taking care of this functionality!
    # If used, implement tests for this:
    # async def self_or_admin(self, user_id: UUID, require=True) -> bool:
    #     """Checks if the current user is the user_id or an admin"""
    #     try:
    #         user_id = UUID(user_id)
    #     except ValueError:
    #         logger.error("ID is not a universal unique identifier (uuid).")
    #         raise HTTPException(status_code=400, detail="Invalid id.")
    #     user_has_admin_role = await self.has_role("Admin", require=False)
    #     current_user = await self.provides_current_user()
    #     if user_has_admin_role:
    #         return True
    #     elif current_user.user_id == user_id:
    #         return True
    #     else:
    #         if require:
    #             raise HTTPException(status_code=403, detail="Access denied")
    #         else:
    #             return False


# endregion: Generic check

# region: Specific checks


# Use those classes directly as checks, e.g.:
# @app.get("/example_endpoint")
# def example(
#     token: bool = Depends(CurrentAccessTokenIsValid()),
# ):
#     """Returns the result of the check."""
#     return token
#
#   options: require
#            - if set to False, the check will not raise an exception if the condition is not met but return False
#            - if set to True, the check will raise an exception if the condition is not met
#            - default is True
#
#
#   examples:
#   - token_valid: bool = Depends(CurrentAccessTokenIsValid())


class CurrentAccessTokenIsValid(CurrentAccessToken):
    """Checks if the current token is valid"""

    def __init__(self, require=True) -> None:
        self.require = require

    async def __call__(self, payload: dict = Depends(get_access_token_payload)) -> bool:
        super().__init__(payload)
        return await self.is_valid(self.require)


class CurrentAccessTokenHasScope(CurrentAccessToken):
    """Checks if the current token includes a specific scope"""

    def __init__(self, scope, require=True) -> None:
        self.scope = scope
        self.require = require

    async def __call__(self, payload: dict = Depends(get_access_token_payload)) -> bool:
        super().__init__(payload)
        return await self.has_scope(self.scope, self.require)


class CurrentAccessTokenHasRole(CurrentAccessToken):
    """Checks if the current token includes a specific scope"""

    def __init__(self, role, require=True) -> None:
        self.role = role
        self.require = require

    async def __call__(self, payload: dict = Depends(get_access_token_payload)) -> bool:
        super().__init__(payload)
        return await self.has_role(self.role, self.require)


class CurrentAccessTokenHasGroup(CurrentAccessToken):
    """Checks if the current token includes a specific scope"""

    def __init__(self, group, require=True) -> None:
        self.group = group
        self.require = require

    async def __call__(self, payload: dict = Depends(get_access_token_payload)) -> bool:
        super().__init__(payload)
        return await self.has_group(self.group, self.require)


class CurrentAzureUserInDatabase(CurrentAccessToken):
    """Checks user in database, if not adds user (self-sign-up) and adds or updates the group membership of the user"""

    def __init__(self) -> None:
        pass

    async def __call__(
        self, payload: dict = Depends(get_azure_token_payload)
    ) -> UserRead:
        super().__init__(payload)
        return await self.gets_or_signs_up_current_user()


# endregion: Specific checks

# endregion: CHECKS


# region: Access control


# class AccessControl:
#     def __init__(self) -> None:
#         pass

#     async def permits(
#         user: "CurrentUserData", resource_id: UUID, action: Action
#     ) -> bool:
#         """Checks if the user has permission to perform the action on the resource"""
#         pass


# delete later:

# snippet for preventing admin to change last_accessed_at:
# TBD: remove - functionality replaced by access-log-table)
# TBD: this will fail some tests - so they need to be rewritten

# def updates_last_access(
# self, admin: bool, current_user: UserRead, owner_id: UUID
# ) -> None:
# logger.info("POST updated_last_access")
# if (admin is True) and (str(current_user.user_id) != str(owner_id)):
#     self.__update_last_access = False
# return self.__update_last_access

# snippet to allow only admins to write all and users to write their own data:
# should be replaced by
# if (str(current_user.user_id) != str(user_id)) and (check_admin_role is False):
#     raise HTTPException(status_code=403, detail="Access denied")

# endregion: Access control
