import logging

# import jwt
from fastapi import HTTPException, Request

# import httpx
## Use pyjwt to decode the tokens!

logger = logging.getLogger(__name__)


def get_jwks():
    """Fetches the JWKs from identity provider"""
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


# @get_jwks
def validate_token(request: Request):
    """Validates the access token sent in the request header"""
    # get the token from the header:
    # print("=== request.headers ===")
    # print(request.headers)
    try:
        # request.headers.get("Authorization").split("Bearer ")[1]
        token = request.headers.get("Authorization").split("Bearer ")[1]
        if token:
            print("=== token exists ===")
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
        logger.error(f"Token validation failed: ${e}")
        raise HTTPException(status_code=401, detail="Invalid token")
