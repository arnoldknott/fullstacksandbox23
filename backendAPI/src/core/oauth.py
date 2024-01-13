import json
import logging

import httpx
import jwt
from core.cache import redis_jwks_client
from core.config import config
from fastapi import HTTPException, Request
from jwt.algorithms import RSAAlgorithm

## Use pyjwt to decode the tokens!

logger = logging.getLogger(__name__)


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
    # try:
    #     jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    #     jwks = httpx.get(jwks_url)
    #     jwks.raise_for_status()
    #     return jwks.json()
    # except Exception as e:
    #     logger.error(f"Failed to fetch JWKS: ${e}")
    #     raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
    #
    # Get the OpenID Connect metadata for the tenant:
    # oidc_config = requests.get(
    #     f"https://login.microsoftonline.com/{os.environ['AZ_TENANT_ID']}/v2.0/.well-known/openid-configuration"
    # ).json()

    # # Get the JSON Web Key Set (JWKS) from the OpenID Connect discovery endpoint:
    # jwks = requests.get(oidc_config["jwks_uri"]).json()
    # kid = jwt.get_unverified_header(token)["kid"]

    # # Get the key that matches the kid:
    # rsa_key = {}
    # for key in jwks["keys"]:
    #     if key["kid"] == kid:
    #         rsa_key = RSAAlgorithm.from_jwk(key)


def validate_token(request: Request, retries: int = 0):
    """Validates the access token sent in the request header"""
    # get the token from the header:
    # print("=== request.headers ===")
    # print(request.headers)
    logger.info("🔑 Validating token")
    try:
        # request.headers.get("Authorization").split("Bearer ")[1]
        authHeader = request.headers.get("Authorization")
        # print("=== authHeader ===")
        # print(authHeader)
        token = authHeader.split("Bearer ")[1]
        if token:
            jwks = get_jwks()

            # Get the key that matches the kid:
            kid = jwt.get_unverified_header(token)["kid"]
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    rsa_key = RSAAlgorithm.from_jwk(key)
            # print("=== rsa_key ===")
            # print(rsa_key)
            # print("=== token ===")
            # print(token)
            # # print("=== config.APP_REG_CLIENT_ID ===")
            # print(config.APP_REG_CLIENT_ID)
            # print("=== config.AZURE_ISSUER_URL ===")
            # print(config.AZURE_ISSUER_URL)
            logger.info("Decoding token")
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
            # Try validating token first with cached keys - if no success, fetch new keys, put them in the cache and try again!
            # print(token)
            # print("=== get_jwks() ===")
            # print(get_jwks())
        # jwt.decode(
        #         token,
        #         rsa_key,
        #         algorithms=["RS256"],
        #         audience=os.environ["AZ_CLIENT_ID"],
        #         issuer=f"https://login.microsoftonline.com/{os.environ['AZ_TENANT_ID']}/v2.0",
        #         options={
        #             "validate_iss": True,
        #             "validate_aud": True,
        #             "validate_exp": True,
        #         },
        #     )
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
