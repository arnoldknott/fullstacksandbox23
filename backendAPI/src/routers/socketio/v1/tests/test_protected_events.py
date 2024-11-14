import pytest
from jwt import DecodeError
from socketio.exceptions import ConnectionError

from routers.socketio.v1.protected_events import protected_events_router
from tests.utils import token_admin_read_write, token_user1_read_write


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
        sid="123",
        environ="fake_environ",
        auth=mocked_token,
    )

    print("=== test_on_connect - connect_response ===")
    print(connect_response)

    assert connect_response == "OK from server"


@pytest.mark.anyio
async def test_on_connect_invalid_token():
    """Test the on_connect event for socket.io without mocking decoding function."""
    # Should run into an uncaught exception from the decoding algorithm, depending on its implementation

    try:
        await protected_events_router.on_connect(
            sid="123",
            environ="fake_environ",
            auth="invalid_token",
        )
        raise Exception("This should have failed due to invalid token.")
    except DecodeError as err:
        print("=== test_on_connect_invalid_token - Exception ===")
        print(err)

        assert str(err) == "Not enough segments"


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

    try:
        async for client in socketio_client(["/protected_events"]):
            response = None

            @client.on("protected_message", namespace="/protected_events")
            async def handler(data):
                nonlocal response
                response = data

            emit_response = await client.emit(
                "protected_message", "Hello, world!", namespace="/protected_events"
            )
            print("=== test_protected_message - emit_response ===")
            print(emit_response)

            await client.sleep(1)

            assert response == "Protected message received from client: Hello, world!"

            raise Exception(
                "This should have failed due to missing authentication in on_connect."
            )

    except ConnectionError as err:
        print("=== test_protected_message - Exception ===")
        print(err)

        assert str(err) == "One or more namespaces failed to connect"
