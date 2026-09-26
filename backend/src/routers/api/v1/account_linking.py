from uuid import UUID

from fastapi import HTTPException
from redis.commands.json._util import JsonType

from core.authentication.base import VerifiedIdentity
from core.cache import decrypt_session_value, redis_session_client
from core.security import verify_access_token
from core.socketio import disconnect_auth_sessions


def _bearer_token(value: str) -> str:
    scheme, separator, token = value.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid link authorization.")
    return token


async def _link_identities(
    token_payload: VerifiedIdentity | dict,
    link_authorization: str,
) -> tuple[VerifiedIdentity, VerifiedIdentity]:
    if not isinstance(token_payload, VerifiedIdentity):
        raise HTTPException(
            status_code=401, detail="Verified provider identity required."
        )
    linked_identity = await verify_access_token(_bearer_token(link_authorization))
    if linked_identity.provider == token_payload.provider:
        raise HTTPException(status_code=409, detail="A different provider is required.")
    return token_payload, linked_identity


async def _invalidate_merged_user_sessions(
    user_ids: set[UUID], cleanup_id: str
) -> None:
    user_id_strings = {str(user_id) for user_id in user_ids}
    session_ids: set[str] = set()
    for raw_key in redis_session_client.scan_iter(match="session:*"):
        key = raw_key.decode() if isinstance(raw_key, bytes) else str(raw_key)
        raw_session = redis_session_client.json().get(key)
        try:
            session = decrypt_session_value(key, "$", raw_session)
        except TypeError, ValueError:
            continue
        current_user = session.get("currentUser") if isinstance(session, dict) else None
        if isinstance(current_user, dict) and current_user.get("id") in user_id_strings:
            session_ids.add(key.removeprefix("session:"))
    await _complete_merge_cleanup(cleanup_id, session_ids)


async def _complete_merge_cleanup(
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
