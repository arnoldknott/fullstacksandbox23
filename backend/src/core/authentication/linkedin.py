"""LinkedIn identity-token validation and public signing-key retrieval."""

from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import HTTPException
from jwt.algorithms import RSAAlgorithm

from .base import get_cached_jwks

# Public protocol endpoint published by LinkedIn; never derived from token claims.
LINKEDIN_JWKS_URL = "https://www.linkedin.com/oauth/openid/jwks"


async def get_linkedin_jwks(no_cache: bool = False) -> dict[str, Any]:
    """Fetch LinkedIn public signing keys through the shared Redis cache."""
    return await get_cached_jwks(
        "jwks:linkedin", jwks_url=LINKEDIN_JWKS_URL, no_cache=no_cache
    )


def validate_linkedin_identity_token(
    token: str, jwks: dict[str, Any], *, issuer: str, client_id: str
) -> dict[str, Any]:
    """Verify the identity token for the explicitly configured login application."""
    if not issuer or not client_id:
        raise HTTPException(
            status_code=503, detail="LinkedIn authentication is not configured."
        )
    header = jwt.get_unverified_header(token)
    if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
        raise jwt.InvalidTokenError("Invalid signing algorithm or key identifier.")
    keys = [key for key in jwks.get("keys", []) if key.get("kid") == header["kid"]]
    if len(keys) != 1:
        raise jwt.InvalidTokenError("Unknown or ambiguous signing key.")
    key = keys[0]
    if (
        key.get("kty") != "RSA"
        or key.get("use", "sig") != "sig"
        or key.get("alg", "RS256") != "RS256"
    ):
        raise jwt.InvalidTokenError("Invalid signing key.")
    public_key = RSAAlgorithm.from_jwk(key)
    if not isinstance(public_key, RSAPublicKey):
        raise jwt.InvalidTokenError("Expected a public signing key.")
    claims = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=issuer,
        audience=client_id,
        options={"require": ["iss", "aud", "sub", "iat", "exp"]},
    )
    if not isinstance(claims["sub"], str) or not claims["sub"].strip():
        raise jwt.InvalidTokenError("Missing subject.")
    # Numeric dates must not be booleans or coercible strings.
    if any(type(claims[name]) not in (int, float) for name in ("iat", "exp")):
        raise jwt.InvalidTokenError("Invalid token time.")
    if claims["exp"] <= claims["iat"]:
        raise jwt.InvalidTokenError("Invalid token lifetime.")
    audience = claims["aud"]
    if (
        isinstance(audience, list)
        and len(audience) > 1
        and claims.get("azp") != client_id
    ) or ("azp" in claims and claims["azp"] != client_id):
        raise jwt.InvalidTokenError("Invalid authorized party.")
    return claims


async def get_linkedin_token_payload(
    token: str, *, issuer: str, client_id: str
) -> dict[str, Any]:
    """Validate with cached keys and retry once with fresh keys on token failure."""
    if not issuer or not client_id:
        raise HTTPException(
            status_code=503, detail="LinkedIn authentication is not configured."
        )
    jwks = await get_linkedin_jwks()
    try:
        return validate_linkedin_identity_token(
            token, jwks, issuer=issuer, client_id=client_id
        )
    except jwt.PyJWTError:
        jwks = await get_linkedin_jwks(no_cache=True)
        return validate_linkedin_identity_token(
            token, jwks, issuer=issuer, client_id=client_id
        )
