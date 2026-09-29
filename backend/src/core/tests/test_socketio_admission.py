from uuid import uuid4
import hashlib

import pytest

from core.cache import (
    consume_socketio_admission_ticket,
    create_socketio_admission_ticket,
    redis_session_client,
)


@pytest.mark.anyio
async def test_socketio_admission_ticket_is_one_time():
    session_id = str(uuid4())
    redis_session_client.json().set(f"session:{session_id}", ".", {"loggedIn": True})
    try:
        ticket = create_socketio_admission_ticket(session_id)
        ticket_key = (
            f"session:socketio-ticket:{hashlib.sha256(ticket.encode()).hexdigest()}"
        )

        assert 0 < redis_session_client.ttl(ticket_key) <= 30
        assert consume_socketio_admission_ticket(ticket) == session_id
        assert consume_socketio_admission_ticket(ticket) is None
    finally:
        redis_session_client.delete(f"session:{session_id}")


@pytest.mark.anyio
async def test_socketio_admission_ticket_is_invalid_after_session_deletion():
    session_id = str(uuid4())
    redis_session_client.json().set(f"session:{session_id}", ".", {"loggedIn": True})
    ticket = create_socketio_admission_ticket(session_id)

    redis_session_client.delete(f"session:{session_id}")

    assert consume_socketio_admission_ticket(ticket) is None
