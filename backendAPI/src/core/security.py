import json
import logging
from typing import Annotated, List, Optional

import httpx
import jwt
from core.cache import redis_jwks_client
from core.config import config
from fastapi import Depends, HTTPException, Request
from jwt.algorithms import RSAAlgorithm

logger = logging.getLogger(__name__)

# To get the swagger UI to work, add the OAuth2AuthorizationCodeBearer to the securitySchemes section of the openapi.json file
# https://github.com/tiangolo/fastapi/pull/797
# make the relevant routers dependent on it!
# currently the redirect URI cannot be passed through Swagger UI,
# so therefore manual token acquisition is necessary and SwaggerUI does not work with protected routes


def get_jwks(no_cache: bool = False):
    """Fetches the JWKs from identity provider"""
    logger.info("🔑 Fetching JWKS")
    try:
        if not no_cache:
            jwks = redis_jwks_client.json().get("jwks")
            if jwks:
                return json.loads(jwks)
            else:
                get_jwks(no_cache=True)
        else:
            oidc_config = httpx.get(config.AZURE_OPENID_CONFIG_URL).json()
            if not oidc_config:
                raise HTTPException(
                    status_code=404, detail="Failed to fetch Open ID config."
                )
            jwks = httpx.get(oidc_config["jwks_uri"]).json()
            if not jwks:
                raise HTTPException(status_code=404, detail="Failed to fetch JWKS.")
            redis_jwks_client.json().set("jwks", ".", json.dumps(jwks))
        return jwks
    except Exception as err:
        logger.error("🔑 Failed to get JWKS.")
        raise err


def get_token_from_header(auth_header: str):
    """Returns the access token sent in the request header"""


# TBD: move the retries information to somewhere else - maybe add as a header?
def get_current_user(request: Request, retries: Optional[int] = 0):
    """Validates the access token sent in the request header and returns the payload if valid"""
    logger.info("🔑 Validating token")
    if retries > 1:
        raise HTTPException(status_code=401, detail="Invalid retry attempt.")
    try:
        auth_header = request.headers.get("Authorization")
        token = auth_header.split("Bearer ")[1]
        # print("=== token ===")
        # print(token)
        if token:
            jwks = get_jwks()

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
            # print("=== payload ===")
            # print(payload)
            return payload
            # return True
    except Exception as e:
        # only one retry allowed: by now the tokens should be cached!
        if retries < 1:
            logger.info(
                "🔑 Failed to validate token, fetching new JWKS and trying again."
            )
            get_jwks(no_cache=True)
            return get_current_user(request, retries + 1)
        logger.error(f"🔑 Token validation failed: ${e}")
        raise HTTPException(status_code=401, detail="Invalid token")


# remove after reafctoring:


# Following three dependency functions can be used for restricting the access to the API:
# - validate_token: authorization check if the token is valid
# - validate_scope: adds checking for the required scope on top of token validation
#   - get_required_scopes: a decorator function to be used as a dependency in routers and endpoints, to pass the relevant scopes
# - validate_roles: adds checking for the required roles on top of token validation
#   - get_required_roles: a decorator function to be used as a dependency in routers and endpoints, to pass the relevant roles


def get_token(request: Request):
    """Returns the access token sent in the request header"""
    authHeader = request.headers.get("Authorization")
    token = authHeader.split("Bearer ")[1]
    return token


def validate_token(current_user: dict = Depends(get_current_user)):
    """Turns the existence of a validated user into a dependency (just by retuning a bool)"""
    logger.info("🔑 User access to protected route")
    if current_user:
        return True


class ScopeChecker:
    """Checks if the required scope is present in the access token"""

    def __init__(self, scopes: List[str]):
        self.required_scopes = scopes

    def __call__(
        self,
        current_user: Annotated[str, Depends(get_current_user)],
        # scopes: List[str] = ["api.read"],
    ):
        # All required scopes must be present in the access token!
        logger.info("🔑 User access to protected route with scope requirement")
        if not set(self.required_scopes).issubset(set(current_user["scp"].split(" "))):
            raise HTTPException(status_code=403, detail="🔑 Token misses required scope")


class GroupChecker:
    """Checks if the user is a member of one of the allowed groups"""

    def __init__(self, groups: List[str]):
        self.allowed_groups = groups

    def __call__(
        self,
        current_user: Annotated[str, Depends(get_current_user)],
        access_token: Annotated[str, Depends(get_token)],
    ):
        # The user must be member of at least one of the allowed groups!
        logger.info("🔑 Accessing protected route with group requirement")
        try:
            """Search for the allowed groups in the groups the user is member of from Microsoft Graph API"""
            # TBD: add caching here!
            # TBD: use search parameter on Microsoft Graph API to reduce the number of requests
            response = httpx.get(
                "https://graph.microsoft.com/v1.0/me/transitiveMemberOf"
            )
            groups = response.json()
            print("=== groups ===")
            print(groups)
            # if not set(self.allowed_groups).issubset(set(current_user["groups"])):
            #     raise HTTPException(status_code=403, detail="🔑 User not member of allowed groups")
        except Exception as err:
            logger.error("🔑 Failed to fetch user groups from Microsoft Graph.")
            raise err


# # declaration of decorator function to be used as a dependency in routers and endpoints
# def get_required_scopes(scopes: List[str]):
#     """Returns a list of required scopes"""

#     def _inner():
#         return scopes

#     return _inner


# def validate_scope(
#     required_scopes: List[str] = Depends(get_required_scopes(["api.read"])),
#     get_current_user: dict = Depends(validate_token),
# ):
#     """Validates the scope of the access token sent in the request header - minimum required scope is api.read"""
#     if not set(required_scopes).issubset(set(get_current_user["scp"].split(" "))):
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
#     get_current_user: dict = Depends(validate_token),
# ):
#     """Validates the roles of the access token sent in the request header"""
#     if not set(required_roles).issubset(set(get_current_user["roles"].split(" "))):
#         raise HTTPException(status_code=403, detail="Forbidden")
#     pass
