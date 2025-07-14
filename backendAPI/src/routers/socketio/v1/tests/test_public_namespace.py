import pytest
import socketio


@pytest.mark.anyio
async def test_public_message_event_in_public_namespace(socketio_test_client):
    """Test the public message event in socket.io's public namespace."""

    client = socketio.AsyncClient(logger=True, engineio_logger=True)

    await client.connect(
        "http://127.0.0.1:80",
        socketio_path="socketio/v1",
        namespaces=["/public-namespace"],
    )

    response = None

    @client.on("public_message", namespace="/public-namespace")
    async def handler(data):
        nonlocal response
        response = data

    await client.emit("public_message", "Hello, world!", namespace="/public-namespace")

    await client.sleep(1)

    assert response == "Message received in public namespace from client: Hello, world!"

    await client.disconnect()
