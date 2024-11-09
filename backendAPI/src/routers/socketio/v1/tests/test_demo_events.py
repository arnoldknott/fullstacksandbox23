import pytest


@pytest.mark.anyio
async def test_demo_socket(socketio_client):
    """Test the public websocket."""
    # Emit a dummy event to ensure the connection is established
    await socketio_client.emit("dummy_event", {})

    # Handle the initial connection message
    initial_message = await socketio_client.receive()
    assert initial_message[0] == "message"
    assert initial_message[1].startswith("Hello new client with session id")

    # Send a demo_message to the server and verify the response
    await socketio_client.emit("demo_message", "Hello, world!")
    response = await socketio_client.receive(timeout=1)
    print("=== test_demo_socket - after Hello world receive ===")
    assert response == ["message", "Message received from client: Hello, world!"]
