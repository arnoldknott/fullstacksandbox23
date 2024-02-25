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


async def get_azure_token_payload(request: Request) -> dict:
    """Validates the access token sent in the request header and returns the payload if valid"""
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
        raise HTTPException(status_code=401, detail="Invalid token")


# Use those classes as guards, e.g.:
# @app.get("/example_endpoint")
# def example(
#     current_user: bool = Depends(CurrentAzureTokenIsValid()),
# ):
#     """Returns the result of the guard."""
#     return current_user


class CurrentAzureTokenIsValid:
    """Checks if the current token is valid"""

    def __init__(self, require=True) -> None:
        self.require = require

    async def __call__(self, payload: dict = Depends(get_azure_token_payload)) -> bool:
        if payload:
            return True
        else:
            if self.require:
                raise HTTPException(status_code=401, detail="Invalid token")
            else:
                return False


class CurrentAzureTokenHasScope:
    """Checks if the current token includes a specific scope"""

    def __init__(self, scope, require=True) -> None:
        self.scope = scope
        self.require = require

    async def __call__(self, payload: dict = Depends(get_azure_token_payload)) -> bool:
        if ("scp" in payload) and (self.scope in payload["scp"]):
            return True
        else:
            if self.require:
                raise HTTPException(status_code=403, detail="Access denied")
            else:
                return False


class CurrentAzureTokenHasRole:
    """Checks if the current token includes a specific role"""

    def __init__(self, role, require=True) -> None:
        self.role = role
        self.require = require

    async def __call__(self, payload: dict = Depends(get_azure_token_payload)) -> bool:
        if ("roles" in payload) and (self.role in payload["roles"]):
            return True
        else:
            if self.require:
                raise HTTPException(status_code=403, detail="Access denied")
            else:
                return False


class CurrentAzureUserInDatabase:
    """Checks user in database, if not adds user (self-sign-up) and adds or updates the group membership of the user"""

    def __init__(self) -> None:
        pass

    # This is responsible for self-sign on: if a user has a token, the user is allowed
    # Who gets the tokens is controlled by the identity provider (Azure AD)
    # Can be through membership in a group, which has access to the application
    # -> in Azure portal under Enterprise applications,
    # -> turn of filter enterprise applications and
    # -> search for the backend application registration
    # -> under users and groups add the users or groups:
    # -> gives and revokes access for users and groups based on roles
    async def __call__(
        self, payload: dict = Depends(get_azure_token_payload)
    ) -> UserRead:
        groups = []
        try:
            if "groups" in payload:
                groups = payload["groups"]
            user_id = payload["oid"]
            tenant_id = payload["tid"]
            update_last_access = True
            if ("roles" in payload) and ("Admin" in payload["roles"]):
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


# class Guards:
#     """Guards for protecting routes"""

#     def __init__(self):
#         pass

#     # TBD: write tests for this - or remove?:
#     async def azure_token_is_valid(
#         self, payload: dict = Depends(get_azure_token_payload)
#     ):
#         """Checks if the token is valid"""
#         if payload:
#             return True
#         else:
#             raise HTTPException(status_code=401, detail="Invalid token")


# guards = Guards()
