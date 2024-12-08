import pytest


@pytest.mark.anyio
async def test_public_message_event_in_public_namespace(socketio_test_client):
    """Test the public message event in socket.io's public namespace."""

    async for client in socketio_test_client(
        ["/public-namespace"], "http://127.0.0.1:80"
    ):
        response = None

        @client.on("public_message", namespace="/public-namespace")
        async def handler(data):
            nonlocal response
            response = data

        await client.emit(
            "public_message", "Hello, world!", namespace="/public-namespace"
        )

        await client.sleep(1)

        assert (
            response
            == "Message received in public namespace from client: Hello, world!"
        )

        await client.disconnect()
