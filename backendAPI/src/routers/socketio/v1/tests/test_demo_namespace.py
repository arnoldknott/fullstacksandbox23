import pytest
import socketio
from socketio.exceptions import ConnectionError

from src.routers.socketio.v1.demo_namespace import DemoNamespace, demo_namespace_router
from tests.utils import token_admin_read_write_socketio, token_user1_read_write_socketio


@pytest.mark.anyio
async def test_on_connect_invalid_token():
    """Test the on_connect event for socket.io without mocking decoding function."""
    # Should run into an uncaught exception from the decoding algorithm, depending on its implementation

    try:
        await demo_namespace_router.on_connect(
            sid="123",
            environ="fake_environ",
            auth={"session_id": "fake_session_id"},
        )
        raise Exception("This should have failed due to invalid token.")
    except ConnectionRefusedError as err:
        print("=== test_on_connect_invalid_token - Exception ===")
        print(err)

        assert str(err) == "Authorization failed"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_connect_with_test_server_demo_namespace(
    mock_token_payload,
    # socketio_test_server,
    provide_namespace_server,
):
    """Test the demo socket.io message event."""
    mocked_token_payload = mock_token_payload

    # sio = socketio_test_server
    # sio.register_namespace(DemoNamespace("/demo-namespace"))
    await provide_namespace_server([DemoNamespace("/demo-namespace")])

    client = socketio.AsyncClient(logger=True, engineio_logger=True)

    responses = []

    @client.event(namespace="/demo-namespace")
    async def demo_message(data):
        nonlocal responses
        responses.append(data)

    await client.connect(
        "http://127.0.0.1:8669",
        socketio_path="socketio/v1",
        namespaces=["/demo-namespace"],
        auth={"session_id": "testsessionid"},
    )
    await client.sleep(3)

    assert len(responses) == 2
    assert responses[0] == f"Welcome {mocked_token_payload['name']} to /demo-namespace."
    assert "Your session ID is " in responses[1]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_demo_message_with_test_server(
    mock_token_payload,
    # socketio_test_server,
    provide_namespace_server,
    socketio_test_client,
):
    """Test the demo socket.io message event."""
    mocked_token_payload = mock_token_payload

    # sio = socketio_test_server
    # sio.register_namespace(DemoNamespace("/demo-namespace"))
    await provide_namespace_server([DemoNamespace("/demo-namespace")])

    async for client in socketio_test_client(["/demo-namespace"]):
        await client.emit("demo_message", "Something", namespace="/demo-namespace")

        response = ""

        @client.event(namespace="/demo-namespace")
        async def demo_message(data):

            nonlocal response
            response = data

        # Wait for the response to be set
        await client.sleep(1)

        assert response == f"{mocked_token_payload["name"]}: Something"

        await client.disconnect()


@pytest.mark.anyio
async def test_demo_message_with_production_server_fails_without_token(
    socketio_test_client,
):
    """Test the demo socket.io message event."""

    try:
        async for client in socketio_test_client(
            ["/demo-namespace"], "http://127.0.0.1:80"
        ):
            response = None

            @client.on("demo_message", namespace="/demo-namespace")
            async def handler(data):
                nonlocal response
                response = data

            await client.emit(
                "demo_message", "Hello, world!", namespace="/demo-namespace"
            )

            await client.sleep(1)

            raise Exception(
                "This should have failed due to missing authentication in on_connect."
            )

    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"
