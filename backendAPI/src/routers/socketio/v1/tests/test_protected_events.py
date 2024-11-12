import pytest

from tests.utils import (
    token_admin_read_write,
    token_user1_read_write,
)

from routers.socketio.v1.protected_events import protected_events_router


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_on_connect(mock_token_payload):
    """Test the on_connect event for socket.io."""
    mocked_token = await mock_token_payload()

    connect_response = await protected_events_router.on_connect(
        sid="123", environ="fake_environ", auth=mocked_token
    )

    print("=== test_on_connect - connect_response ===")
    print(connect_response)

    # assert 0


@pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write, token_user1_read_write],
#     indirect=True,
# )
# TBD: rewrite, so it doesn't use the client,
# but directly calls the server events with on_connect() in a fixture,
# where on_connect is mocked with the token payload
async def test_protected_message(socketio_client):
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
