import logging

from fastapi import HTTPException, Request

# import httpx


logger = logging.getLogger(__name__)


def get_jwks():
    """Fetches the JWKS from identity provider"""
    # try:
    #     jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    #     jwks = httpx.get(jwks_url)
    #     jwks.raise_for_status()
    #     return jwks.json()
    # except Exception as e:
    #     logger.error(f"Failed to fetch JWKS: ${e}")
    #     raise HTTPException(status_code=500, detail="Failed to fetch JWKS")


def validate_token(request: Request):
    """Validates the access token sent in the request header"""
    # get the token from the header:
    # print("=== request.headers ===")
    # print(request.headers)
    try:
        token = request.headers.get("Authorization").split("Bearer ")[1]
        # print("=== token ===")
        # print(token)
    except Exception as e:
        logger.error(f"Token validation failed: ${e}")
        raise HTTPException(status_code=401, detail="Invalid token")
