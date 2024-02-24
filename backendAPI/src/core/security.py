import json
import logging

import httpx
import jwt
from core.cache import redis_jwks_client
from core.config import config
from models.user import UserRead
from crud.user import UserCRUD
from fastapi import Depends, HTTPException, Request
from jwt.algorithms import RSAAlgorithm

logger = logging.getLogger(__name__)
# router = APIRouter()

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
# TBD: write tests for this:
async def get_azure_jwks(no_cache: bool = False):
    """Fetches the JWKs from identity provider"""
    logger.info("🔑 Fetching JWKS")
    try:
        if no_cache is False:
            # print("=== no_cache ===")
            # print(no_cache)
            jwks = redis_jwks_client.json().get("jwks")
            print("=== jwks ===")
            print(jwks)
            if jwks:
                return json.loads(jwks)
            else:
                await get_azure_jwks(no_cache=True)
        else:
            # print("=== config.AZURE_OPENID_CONFIG_URL ===")
            # print(config.AZURE_OPENID_CONFIG_URL)
            oidc_config = httpx.get(config.AZURE_OPENID_CONFIG_URL).json()
            # print("=== oidc_config ===")
            # print(oidc_config)
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
                redis_jwks_client.json().set("jwks", ".", json.dumps(jwks))
            except Exception as err:
                raise HTTPException(
                    status_code=404, detail=f"Failed to set JWKS in redis: ${err}"
                )
        return jwks
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
    print("=== payload ===")
    print(payload)
    return payload


# TBD: move the retries information to somewhere else - maybe add as a header?
# async def get_azure_token_payload(request: Request, retries: Optional[int] = 0) -> dict:
async def get_azure_token_payload(request: Request) -> dict:
    """Validates the access token sent in the request header and returns the payload if valid"""
    logger.info("🔑 Validating token")
    # if retries > 1:
    #     raise HTTPException(status_code=401, detail="Invalid retry attempt.")
    try:
        auth_header = request.headers.get("Authorization")
        token = auth_header.split("Bearer ")[1]
        # print("=== token ===")
        # print(token)
        if token:
            try:
                jwks = await get_azure_jwks()
                payload = await decode_token(token, jwks)
                print("=== 🔑 Token verified in with cached jwks ===")
                return payload
            except Exception:
                logger.info(
                    "🔑 Failed to validate token, fetching new JWKS and trying again."
                )
                jwks = await get_azure_jwks(no_cache=True)
                payload = await decode_token(token, jwks)
                print("=== 🔑 Token verified after fetching and caching new JWKS ===")
                return payload

    except Exception as e:
        # only one retry allowed: by now the tokens should be cached!
        # if retries < 1:
        #     logger.info(
        #         "🔑 Failed to validate token, fetching new JWKS and trying again."
        #     )
        #     await get_azure_jwks(no_cache=True)
        #     return await get_azure_token_payload(request, retries + 1)
        logger.error(f"🔑 Token validation failed: ${e}")
        raise HTTPException(status_code=401, detail="Invalid token")


class Guards:
    """Guards for protecting routes"""

    def __init__(self):
        pass

    # TBD: write tests for this:
    async def current_azure_user_is_admin(
        self, payload: dict = Depends(get_azure_token_payload)
    ):
        """Checks if the current user is admin"""
        # print(type(payload["roles"]))
        # if isinstance(payload["roles"], list):
        #     if "Admin" in payload["roles"]:
        #         return True
        # elif isinstance(payload["roles"], str):
        #     if payload["roles"] == "Admin":
        #         return True
        # return False
        # print("=== payload[roles] ===")
        # print(payload["roles"])
        try:
            if "Admin" in payload["roles"]:
                return True
            else:
                return False
        except Exception as err:
            logger.error(f"🔑 Role not found in token: ${err}")
            raise HTTPException(status_code=401, detail="Invalid token")
            # raise HTTPException(
            #     status_code=403, detail="Access forbidden: missing admin role"
            # )

    # TBD: Refactor: merge api.read and api.write into one scope api.access!
    # TBD: pass scope as argument - check if it shows up again in the docs!
    # async def current_azure_token_has_scope(
    #     self, scope: str, payload: dict = Depends(get_azure_token_payload)
    # ):
    #     """Checks if the current token has the api.read scope"""
    #     print("=== scope ===")
    #     print(scope)
    #     print("=== payload ===")
    #     print(payload)
    #     if scope in payload["scp"].split(" "):
    #         return True
    #     else:
    #         raise HTTPException(status_code=403, detail="Access forbidden")

    # TBD: write tests for this:
    async def current_azure_token_has_scope_api_read(
        self, payload: dict = Depends(get_azure_token_payload)
    ):
        """Checks if the current token has the api.read scope"""
        try:
            if "api.read" in payload["scp"].split(" "):
                return True
            else:
                raise HTTPException(status_code=403, detail="Access forbidden")
        except Exception as err:
            logger.error(f"🔑 Scope not found in token: ${err}")
            raise HTTPException(status_code=401, detail="Invalid token")

    async def current_azure_token_has_scope_api_write(
        self, payload: dict = Depends(get_azure_token_payload)
    ):
        """Checks if the current token has the api.write scope"""
        try:
            if "api.write" in payload["scp"].split(" "):
                return True
            else:
                raise HTTPException(status_code=403, detail="Access forbidden")
        except Exception as err:
            logger.error(f"🔑 Scope not found in token: ${err}")
            raise HTTPException(status_code=401, detail="Invalid token")

    # TBD: write tests for this:
    async def current_azure_user_in_database(
        self,
        payload: dict = Depends(get_azure_token_payload),
    ) -> UserRead:
        """Checks user in database, potentially adds user (self-sign-up) and adds or updates the group membership of the user"""
        print("=== payload ===")
        print(payload)
        groups = []
        try:
            if "groups" in payload:
                groups = payload["groups"]
            user_id = payload["oid"]
            # roles = payload["roles"]
            tenant_id = payload["tid"]
            # This is responsible for self-sign on: if a user has a token, the user is allowed
            # Who gets the tokens is controlled by the identity provider (Azure AD)
            # Can be through membership in a group, which has access to the application
            # -> in Azure portal under Enterprise applications,
            # -> turn of filter enterprise applications and
            # -> search for the backend application registration
            # -> under users and groups add the users or groups:
            # -> gives and revokes access for users and groups based on roles
            update_last_access = True
            if "roles" in payload and "Admin" in payload["roles"]:
                update_last_access = False
            async with UserCRUD() as crud:
                current_user = await crud.create_azure_user_and_groups_if_not_exist(
                    user_id, tenant_id, groups, update_last_access
                )
                if current_user:
                    return current_user
                else:
                    raise HTTPException(status_code=404, detail="404 User not found")
        except Exception as err:
            logger.error(f"🔑 User not found in database: ${err}")
            raise HTTPException(status_code=401, detail="Invalid token")

    # TBD: write tests for this:
    async def azure_token_is_valid(
        self, payload: dict = Depends(get_azure_token_payload)
    ):
        """Checks if the token is valid"""
        if payload:
            return True
        else:
            raise HTTPException(status_code=401, detail="Invalid token")


guards = Guards()

# remove after refactoring:


# Following three dependency functions can be used for restricting the access to the API:
# - validate_token: authorization check if the token is valid
# - validate_scope: adds checking for the required scope on top of token validation
#   - get_required_scopes: a decorator function to be used as a dependency in routers and endpoints, to pass the relevant scopes
# - validate_roles: adds checking for the required roles on top of token validation
#   - get_required_roles: a decorator function to be used as a dependency in routers and endpoints, to pass the relevant roles


# def get_token(request: Request):
#     """Returns the access token sent in the request header"""
#     authHeader = request.headers.get("Authorization")
#     token = authHeader.split("Bearer ")[1]
#     return token


# def validate_azure_token(current_azure_user: dict = Depends(get_azure_token_payload)):
#     """Turns the existence of a validated user into a dependency (just by retuning a bool)"""
#     logger.info("🔑 User access to protected route")
#     if current_azure_user:
#         return True


# class ScopeChecker:
#     """Checks if the required scope is present in the access token"""

#     def __init__(self, scopes: List[str]):
#         self.required_scopes = scopes

#     def __call__(
#         self,
#         current_user: Annotated[str, Depends(get_token_payload)],
#         # scopes: List[str] = ["api.read"],
#     ):
#         # All required scopes must be present in the access token!
#         logger.info("🔑 User access to protected route with scope requirement")
#         if not set(self.required_scopes).issubset(set(current_user["scp"].split(" "))):
#             raise HTTPException(status_code=403, detail="🔑 Token misses required scope")


# class GroupChecker:
#     """Checks if the user is a member of one of the allowed groups"""

#     def __init__(self, groups: List[str]):
#         self.allowed_groups = groups

#     def __call__(
#         self,
#         current_user: Annotated[str, Depends(get_token_payload)],
#         access_token: Annotated[str, Depends(get_token)],
#     ):
#         # The user must be member of at least one of the allowed groups!
#         logger.info("🔑 Accessing protected route with group requirement")
#         try:
#             """Search for the allowed groups in the groups the user is member of from Microsoft Graph API"""
#             # TBD: add caching here!
#             # TBD: use search parameter on Microsoft Graph API to reduce the number of requests
#             response = httpx.get(
#                 "https://graph.microsoft.com/v1.0/me/transitiveMemberOf"
#             )
#             groups = response.json()
#             print("=== groups ===")
#             print(groups)
#             # if not set(self.allowed_groups).issubset(set(current_user["groups"])):
#             #     raise HTTPException(status_code=403, detail="🔑 User not member of allowed groups")
#         except Exception as err:
#             logger.error("🔑 Failed to fetch user groups from Microsoft Graph.")
#             raise err


# # declaration of decorator function to be used as a dependency in routers and endpoints
# def get_required_scopes(scopes: List[str]):
#     """Returns a list of required scopes"""

#     def _inner():
#         return scopes

#     return _inner


# def validate_scope(
#     required_scopes: List[str] = Depends(get_required_scopes(["api.read"])),
#     get_token_payload: dict = Depends(validate_token),
# ):
#     """Validates the scope of the access token sent in the request header - minimum required scope is api.read"""
#     if not set(required_scopes).issubset(set(get_token_payload["scp"].split(" "))):
#         raise HTTPException(status_code=403, detail="Forbidden")
#     pass


# # Factory function to create a dependency
# def require_scopes(scopes: List[str]):
#     """Returns a dependency that checks for the required scopes"""
#     return Depends(validate_scope(Depends(get_required_scopes(scopes))))


# declaration of decorator function to be used as a dependency in routers and endpoints
# def get_required_roles(roles: List[str]):
#     """Returns a list of required scopes"""

#     def _inner():
#         return roles

#     return _inner


# def validate_roles(
#     required_roles: List[str] = Depends(get_required_roles(["Guest Student"])),
#     get_token_payload: dict = Depends(validate_token),
# ):
#     """Validates the roles of the access token sent in the request header"""
#     if not set(required_roles).issubset(set(get_token_payload["roles"].split(" "))):
#         raise HTTPException(status_code=403, detail="Forbidden")
#     pass
