"""Identity-provider token validation helpers, without application admission policy."""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

import httpx2
import jwt
from fastapi import HTTPException

from core.cache import redis_session_client
from core.types import IdentityProvider


@dataclass(frozen=True)
class VerifiedIdentity:
    """Provider selected by a configured validator, never by a claim named provider."""

    provider: IdentityProvider
    claims: dict[str, Any]


@dataclass(frozen=True)
class ProviderValidator:
    provider: IdentityProvider
    validate: Callable[[str], Awaitable[dict[str, Any]]]


async def verify_provider_token(
    token: str, validators: Mapping[str, ProviderValidator]
) -> VerifiedIdentity:
    """Use unverified issuer only to select an allowlisted validator."""
    try:
        hint = jwt.decode(token, options={"verify_signature": False})
        issuer = hint.get("iss")
        validator = validators.get(issuer) if isinstance(issuer, str) else None
        if validator is None:
            raise HTTPException(status_code=401, detail="Unsupported token issuer.")
        claims = await validator.validate(token)
        # The selected validator must still verify the issuer cryptographically.
        if claims.get("iss") != issuer:
            raise HTTPException(status_code=401, detail="Invalid token issuer.")
        return VerifiedIdentity(validator.provider, claims)
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=401, detail="Invalid token.") from error


async def get_cached_jwks(
    cache_key: str,
    *,
    jwks_url: str | None = None,
    discovery_url: str | None = None,
    no_cache: bool = False,
) -> dict[str, Any]:
    """Read public JSON Web Key Sets from Redis, fetching on a miss or refresh.

    URLs and cache keys come from provider modules/configuration, never token claims.
    Retain the existing Microsoft cache lifetime and synchronous client behavior.
    """
    if not no_cache:
        cached = redis_session_client.json().get(cache_key)
        if isinstance(cached, dict) and isinstance(cached.get("keys"), list):
            return cached
    if discovery_url:
        discovery = httpx2.get(discovery_url)
        discovery.raise_for_status()
        jwks_url = discovery.json()["jwks_uri"]
    if not isinstance(jwks_url, str) or not jwks_url:
        raise HTTPException(
            status_code=500, detail="Signing-key endpoint not configured."
        )
    response = httpx2.get(jwks_url)
    response.raise_for_status()
    jwks = response.json()
    if not isinstance(jwks, dict) or not isinstance(jwks.get("keys"), list):
        raise HTTPException(status_code=502, detail="Invalid signing-key response.")
    redis_session_client.json().set(cache_key, ".", jwks)
    return jwks
