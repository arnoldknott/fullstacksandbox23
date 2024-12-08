import pytest
from socketio.exceptions import ConnectionError

from src.routers.socketio.v1.demo_namespace import DemoNamespace, demo_namespace_router
from tests.utils import token_admin_read_write, token_user1_read_write

# # This one does not really make sense any more!
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mock_token_payload",
#     [token_admin_read_write, token_user1_read_write],
#     indirect=True,
# )
# async def test_on_connect(
#     mock_token_payload,
#     mock_get_azure_token_from_cache,
#     mock_get_user_account_from_session_cache,
# ):
#     """Test the on_connect event for socket.io."""
#     await mock_token_payload()

#     connect_response = await demo_namespace_router.on_connect(
#         sid="123",
#         environ="fake_environ",
#         auth={"session_id": "fake_session_id"},
#     )

#     print("=== test_on_connect - connect_response ===")
#     print(connect_response)

#     assert connect_response == "OK from server"


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


# and still the client and sever are not called from the same test
@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_demo_message_with_test_server(
    socketio_server,
    socketio_patched_client,
):
    """Test the demo socket.io message event."""

    sio = socketio_server

    sio.register_namespace(DemoNamespace("/demo_namespace"))

    async for client in socketio_patched_client(["/demo_namespace"]):
        await client.emit("demo_message", "Something", namespace="/demo_namespace")

        response = ""

        @client.event(namespace="/demo_namespace")
        async def demo_message(data):

            nonlocal response
            response = data

        # Wait for the response to be set
        await client.sleep(1)

        assert response == "Demo message received from client: Something"

        await client.disconnect()


@pytest.mark.anyio
async def test_demo_message_with_production_server_fails_without_token(socketio_client):
    """Test the demo socket.io message event."""

    try:
        async for client in socketio_client(["/demo_namespace"]):
            response = None

            @client.on("demo_message", namespace="/demo_namespace")
            async def handler(data):
                nonlocal response
                response = data

            emit_response = await client.emit(
                "demo_message", "Hello, world!", namespace="/demo_namespace"
            )
            print("=== test_demo_message - emit_response ===")
            print(emit_response)

            await client.sleep(1)

            assert response == "Demo message received from client: Hello, world!"

            raise Exception(
                "This should have failed due to missing authentication in on_connect."
            )

    except ConnectionError as err:
        print("=== test_demo_message - Exception ===")
        print(err)

        assert str(err) == "One or more namespaces failed to connect"
