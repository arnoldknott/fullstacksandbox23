"""Microsoft Azure access-token validation and public signing-key retrieval."""

import logging
from typing import Any, Dict, Optional, cast

import jwt
from jwt.algorithms import RSAAlgorithm

from core.config import config

from .base import get_cached_jwks

logger = logging.getLogger(__name__)


async def get_azure_jwks(no_cache: bool = False) -> Dict[str, Any]:
    """Fetch Microsoft public signing keys through the shared Redis cache."""
    # TBD: a future multi-tenant implementation needs tenant-specific cache keys.
    return await get_cached_jwks(
        "jwks:microsoft",
        discovery_url=config.AZURE_OPENID_CONFIG_URL,
        no_cache=no_cache,
    )


async def decode_token(token: str, jwks: Dict[str, Any]) -> dict:
    """Decodes the token"""
    # Get the key that matches the kid:
    kid = jwt.get_unverified_header(token)["kid"]
    rsa_key = {}
    for key in jwks.get("keys", []):
        if key["kid"] == kid:
            rsa_key = RSAAlgorithm.from_jwk(key)
    logger.info("Decoding token")
    # validate the token. `RSAAlgorithm.from_jwk` may return a private or public
    # key type; the JWKS endpoint only publishes public keys, so we view it as
    # `Any` to satisfy PyJWT's typed `decode()` overloads.
    payload = jwt.decode(
        token,
        cast(Any, rsa_key),
        algorithms=["RS256"],
        audience=config.API_SCOPE,
        issuer=config.AZURE_ISSUER_URL,
        options=cast(
            Any,
            {
                "validate_iss": True,
                "validate_aud": True,
                "validate_exp": True,
                "validate_nbf": True,
                "validate_iat": True,
            },
        ),
    )
    # print("=== decode_token - payload ===")
    # print(payload)
    logger.info("Token decoded successfully")
    return payload


async def get_azure_token_payload(token: str) -> Optional[dict]:
    """Validates the Azure access token sent in the request header and returns the payload if valid"""
    # print("=== get_azure_token_payload - called  ===")
    logger.info("🔑 Validating token")
    try:
        jwks = await get_azure_jwks()
        payload = await decode_token(token, jwks)
        return payload
    except Exception:
        logger.info("🔑 Failed to validate token, fetching new JWKS and trying again.")
        jwks = await get_azure_jwks(no_cache=True)
        payload = await decode_token(token, jwks)
        # print("=== get_azure_token_payload - payload ===")
        # print(payload)
        return payload
