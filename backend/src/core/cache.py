import hashlib
import json
import secrets

import redis

from core.config import config, load_encryption_keyring
from core.encryption import Encryption

# print("=== cache.py started ===")

redis_session_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    username="session",
    password=config.REDIS_SESSION_PASSWORD,
    db=config.REDIS_SESSION_DB,
)

encryption = Encryption(load_encryption_keyring())

_WHOLE_PROTECTED_SESSION_ROOTS = {
    "microsoftAccount",
    "microsoftBackendAccessToken",
    "microsoftAuthorization",
    "linkedinAuthorization",
    "accountMerge",
}

SOCKETIO_TICKET_TTL_SECONDS = 30


def decrypt_session_value(redis_key: str, path: str, value):
    """Decrypt protected units while preserving the caller-facing session shape."""
    if path == "$":
        if not isinstance(value, dict):
            return value
        result = dict(value)
        for key, item in value.items():
            item_path = f"$.{key}"
            if key in _WHOLE_PROTECTED_SESSION_ROOTS:
                result[key] = encryption.decrypt(redis_key, item_path, item)
        return result
    root = path[2:].split(".", 1)[0].split("[", 1)[0] if path.startswith("$.") else None
    if root in _WHOLE_PROTECTED_SESSION_ROOTS:
        if path != f"$.{root}":
            raise ValueError(
                f"Protected session subdocument {root} only supports whole-value reads."
            )
        return encryption.decrypt(redis_key, path, value)
    return value


def get_session_value(session_id: str, path: str = "$"):
    redis_key = f"session:{session_id}"
    raw = redis_session_client.json().get(redis_key, path)
    if isinstance(raw, list):
        value = raw[0] if raw else None
    else:
        value = raw
    if value is None:
        return None
    return decrypt_session_value(redis_key, path, value)


def get_protected_cache_value(redis_key: str, purpose: str = "$"):
    value = redis_session_client.json().get(redis_key)
    if value is None:
        return None
    return encryption.decrypt(redis_key, purpose, value)


def set_protected_cache_value(redis_key: str, value, purpose: str = "$"):
    encrypted = encryption.encrypt(redis_key, purpose, value)
    return redis_session_client.json().set(redis_key, ".", encrypted)


def create_socketio_admission_ticket(session_id: str) -> str:
    """Create a short-lived, one-time reference to an existing application session."""
    if get_session_value(session_id) is None:
        raise ValueError("Application session not found.")
    ticket = secrets.token_urlsafe(32)
    redis_key = f"session:socketio-ticket:{hashlib.sha256(ticket.encode()).hexdigest()}"
    protected = encryption.encrypt(redis_key, "$", {"sessionId": session_id})
    redis_session_client.set(
        redis_key,
        json.dumps(protected),
        ex=SOCKETIO_TICKET_TTL_SECONDS,
    )
    return ticket


def consume_socketio_admission_ticket(ticket: str) -> str | None:
    """Redeem a ticket once and return its still-existing application session."""
    redis_key = f"session:socketio-ticket:{hashlib.sha256(ticket.encode()).hexdigest()}"
    raw = redis_session_client.getdel(redis_key)
    if raw is None:
        return None
    try:
        protected = json.loads(raw)
        value = encryption.decrypt(redis_key, "$", protected)
        session_id = value.get("sessionId") if isinstance(value, dict) else None
    except TypeError, ValueError, json.JSONDecodeError:
        return None
    if not isinstance(session_id, str) or get_session_value(session_id) is None:
        return None
    return session_id


# print("=== cache.py finished ===")
