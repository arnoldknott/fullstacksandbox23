import json
import logging

import httpx
import jwt
from core.cache import redis_jwks_client
from core.config import config
from fastapi import HTTPException, Request
from jwt.algorithms import RSAAlgorithm

logger = logging.getLogger(__name__)

# To get the swagger UI to work, add the OAuth2AuthorizationCodeBearer to the securitySchemes section of the openapi.json file
# https://github.com/tiangolo/fastapi/pull/797
# make the relevant routers dependent on it!


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
        logger.error("🔥 Failed to get JWKS.")
        raise err


def validate_token(request: Request, retries: int = 0):
    """Validates the access token sent in the request header"""
    logger.info("🔑 Validating token")
    try:
        authHeader = request.headers.get("Authorization")
        token = authHeader.split("Bearer ")[1]
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
            jwt.decode(
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

            return True
    except Exception as e:
        # only one retry allowed: by now the tokens should be cached!
        if retries < 1:
            logger.info(
                "🔑 Failed to validate token, fetching new JWKS and trying again."
            )
            get_jwks(no_cache=True)
            return validate_token(request, retries + 1)
        logger.error(f"🔑 Token validation failed: ${e}")
        raise HTTPException(status_code=401, detail="Invalid token")
