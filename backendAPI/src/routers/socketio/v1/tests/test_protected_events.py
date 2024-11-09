import pytest

from fastapi import FastAPI
from tests.utils import (
    token_admin_read_write,
    token_user1_read_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
@pytest.mark.anyio
async def test_protected_message(
    socketio_client, app_override_get_azure_payload_dependency: FastAPI
):
    app_override_get_azure_payload_dependency
    # async def test_protected_message():
    """Test the protected socket.io message event."""

    async for client in socketio_client(["/protected_events"]):
        response = None

        @client.on("protected_message", namespace="/protected_events")
        async def handler(data):
            nonlocal response
            response = data

        await client.emit(
            "protected_message", "Hello, world!", namespace="/protected_events"
        )

        await client.sleep(1)

        assert response == "Protected message received from client: Hello, world!"
