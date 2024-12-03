import pytest


@pytest.mark.anyio
async def test_public_message(socketio_simple_client):
    """Test the public socket.io message event."""
    # Emit a dummy event to ensure the connection is established
    await socketio_simple_client.emit("dummy_event", {})

    # Handle the initial connection message
    initial_message = await socketio_simple_client.receive()
    assert initial_message[0] == "message"
    assert initial_message[1].startswith("Hello new client with session id")

    # Send a public_message to the server and verify the response
    await socketio_simple_client.emit("public_message", "Hello, world!")
    response = await socketio_simple_client.receive(timeout=1)
    assert response == ["public_message", "Message received from client: Hello, world!"]
