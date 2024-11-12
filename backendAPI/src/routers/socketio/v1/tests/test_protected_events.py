import pytest

from core.security import get_azure_token_payload


@pytest.mark.anyio
# @pytest.mark.parametrize(
#     "patch_socketio_app",
#     [token_admin_read_write, token_user1_read_write],
#     indirect=True,
# )
# @patch("core.security.get_azure_token_payload", token_admin_read_write)
async def test_protected_message(socketio_client):
    """Test the protected socket.io message event."""
    # socketio_client = socketio_client

    # def mocker_function():
    #     return token_admin_read_write

    # monkeypatch.setattr("core.security.get_azure_token_payload", mocker_function)

    print(
        "=== routers - socketio - v1 - tests - test_protected_events - get_azure_token_payload() ==="
    )
    token_payload = await get_azure_token_payload("somestring")
    print(
        "=== routers - socketio - v1 - tests - test_protected_events - token_payload ==="
    )
    print(token_payload)

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

    assert 0


# @pytest.mark.anyio
# async def test_token_payload(mock_token_payload):
#     """Test the token payload."""
#     token_payload = await get_azure_token_payload("somestring")
#     print(
#         "=== routers - socketio - v1 - tests - test_protected_events - test_token_payload - token_payload ==="
#     )
#     print(token_payload)
#     assert 0
