import json
from uuid import UUID

from fastapi import HTTPException
from redis.commands.json._util import JsonType

from core.authentication.base import VerifiedIdentity
from core.cache import (
    decrypt_session_value,
    get_protected_cache_value,
    redis_session_client,
)
from core.security import (
    SessionReferenceCredential,
    resolve_session_provider_identity,
    verify_access_token,
)
from core.socketio import disconnect_auth_sessions
from core.types import IdentityProvider


def _bearer_token(value: str) -> str:
    scheme, separator, token = value.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid link authorization.")
    return token


async def account_identity(
    credential: VerifiedIdentity | SessionReferenceCredential | dict,
    excluded_provider: IdentityProvider | None = None,
) -> VerifiedIdentity:
    if isinstance(credential, SessionReferenceCredential):
        return await resolve_session_provider_identity(
            credential.session_id, excluded_provider
        )
    if not isinstance(credential, VerifiedIdentity):
        raise HTTPException(
            status_code=401, detail="Verified provider identity required."
        )
    return credential


async def link_identities(
    token_payload: VerifiedIdentity | SessionReferenceCredential | dict,
    link_authorization: str,
) -> tuple[VerifiedIdentity, VerifiedIdentity]:
    survivor_identity = await account_identity(token_payload)
    linked_identity = await verify_access_token(_bearer_token(link_authorization))
    if linked_identity.provider == survivor_identity.provider:
        raise HTTPException(status_code=409, detail="A different provider is required.")
    return survivor_identity, linked_identity


async def invalidate_merged_user_sessions(user_ids: set[UUID], cleanup_id: str) -> None:
    user_id_strings = {str(user_id) for user_id in user_ids}
    session_ids: set[str] = set()
    for raw_key in redis_session_client.scan_iter(match="session:*"):
        key = raw_key.decode() if isinstance(raw_key, bytes) else str(raw_key)
        raw_session = redis_session_client.json().get(key)
        try:
            session = decrypt_session_value(key, "$", raw_session)
        except TypeError, ValueError:
            continue
        if not isinstance(session, dict):
            continue
        current_user = session.get("currentUser")
        if isinstance(current_user, dict) and current_user.get("id") in user_id_strings:
            session_ids.add(key.removeprefix("session:"))
    await complete_merge_cleanup(cleanup_id, session_ids)


async def complete_merge_cleanup(
    cleanup_id: str, session_ids: set[str] | None = None
) -> bool:
    """Persist cleanup intent until socket disconnect and session deletion succeed."""
    cleanup_key = f"session:merge-cleanup:{cleanup_id}"
    if session_ids is None:
        cleanup = redis_session_client.json().get(cleanup_key)
        if not isinstance(cleanup, dict):
            return False
        raw_session_ids = cleanup.get("sessionIds")
        if not isinstance(raw_session_ids, list):
            return False
        session_ids = {
            session_id for session_id in raw_session_ids if isinstance(session_id, str)
        }
    else:
        cleanup_session_ids: list[JsonType] = []
        cleanup_session_ids.extend(sorted(session_ids))
        cleanup_payload: dict[str, JsonType] = {"sessionIds": cleanup_session_ids}
        redis_session_client.json().set(cleanup_key, ".", cleanup_payload)
        redis_session_client.expire(cleanup_key, 3600)
    if session_ids:
        await disconnect_auth_sessions(session_ids)
        redis_session_client.delete(
            *(f"session:{session_id}" for session_id in session_ids)
        )
    redis_session_client.delete(cleanup_key)
    return True


def _contains_microsoft_identifier(value: object, identifier: str) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if (
                key in {"localAccountId", "local_account_id", "oid"}
                and str(item) == identifier
            ):
                return True
            if _contains_microsoft_identifier(item, identifier):
                return True
    elif isinstance(value, list):
        return any(_contains_microsoft_identifier(item, identifier) for item in value)
    elif isinstance(value, str):
        try:
            return _contains_microsoft_identifier(json.loads(value), identifier)
        except TypeError, ValueError:
            return False
    return False


def _provider_session_cleanup_targets(
    user_id: UUID, provider: IdentityProvider
) -> tuple[set[str], set[str], set[str]]:
    user_id_string = str(user_id)
    session_ids: set[str] = set()
    microsoft_cache_keys: set[str] = set()
    matching_session_keys: set[str] = set()
    for raw_key in redis_session_client.scan_iter(match="session:*"):
        key = raw_key.decode() if isinstance(raw_key, bytes) else str(raw_key)
        raw_session = redis_session_client.json().get(key)
        try:
            session = decrypt_session_value(key, "$", raw_session)
        except TypeError, ValueError:
            continue
        if not isinstance(session, dict):
            continue
        current_user = session.get("currentUser")
        if (
            not isinstance(current_user, dict)
            or current_user.get("id") != user_id_string
        ):
            continue
        matching_session_keys.add(key)
        if session.get("identityProvider") == provider.value:
            session_ids.add(key.removeprefix("session:"))
        microsoft_account = session.get("microsoftAccount")
        if isinstance(microsoft_account, dict):
            home_account_id = microsoft_account.get("homeAccountId")
            if isinstance(home_account_id, str) and home_account_id:
                microsoft_cache_keys.add(f"msal:{home_account_id}")
    return session_ids, matching_session_keys, microsoft_cache_keys


def _matching_microsoft_cache_keys(identifier: UUID | str) -> set[str]:
    cache_keys: set[str] = set()
    for raw_key in redis_session_client.scan_iter(match="msal:*"):
        key = raw_key.decode() if isinstance(raw_key, bytes) else str(raw_key)
        try:
            cached = get_protected_cache_value(key)
        except TypeError, ValueError:
            continue
        if _contains_microsoft_identifier(cached, str(identifier)):
            cache_keys.add(key)
    return cache_keys


async def cleanup_unlinked_provider(
    user_id: UUID,
    provider: IdentityProvider,
    identifier: UUID | str,
) -> None:
    """Remove provider credentials/metadata and invalidate provider sessions."""
    session_ids, matching_session_keys, microsoft_cache_keys = (
        _provider_session_cleanup_targets(user_id, provider)
    )
    if provider == IdentityProvider.microsoft:
        microsoft_cache_keys.update(_matching_microsoft_cache_keys(identifier))

    if session_ids:
        await disconnect_auth_sessions(session_ids)
        redis_session_client.delete(
            *(f"session:{session_id}" for session_id in session_ids)
        )
    retained_session_keys = matching_session_keys - {
        f"session:{session_id}" for session_id in session_ids
    }
    removed_path = (
        "$.microsoftAccount"
        if provider == IdentityProvider.microsoft
        else "$.linkedinSubject"
    )
    for key in retained_session_keys:
        redis_session_client.json().delete(key, removed_path)
    if provider == IdentityProvider.microsoft:
        if microsoft_cache_keys:
            redis_session_client.delete(*microsoft_cache_keys)
    else:
        redis_session_client.delete(f"linkedin:{identifier}")
