import pytest


@pytest.mark.anyio
async def test_demo_message(socketio_simple_client):
    """Test the demo socket.io message event."""
    # Emit a dummy event to ensure the connection is established
    await socketio_simple_client.emit("dummy_event", {})

    # Handle the initial connection message
    initial_message = await socketio_simple_client.receive()
    assert initial_message[0] == "message"
    assert initial_message[1].startswith("Hello new client with session id")

    # Send a demo_message to the server and verify the response
    await socketio_simple_client.emit("demo_message", "Hello, world!")
    response = await socketio_simple_client.receive(timeout=1)
    assert response == ["demo_message", "Message received from client: Hello, world!"]


@pytest.mark.anyio
async def test_protected_message(socketio_client):
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

    ### WORKS: ###

    # client = socketio.AsyncClient(logger=True, engineio_logger=True)

    # @client.event
    # def connect(sid, environ, auth):
    #     """Connect event for socket.io."""
    #     print("=== connect - sid ===", flush=True)
    #     print(sid, flush=True)
    #     print("=== connect - environ ===", flush=True)
    #     print(environ, flush=True)
    #     print("=== connect - auth ===", flush=True)
    #     print(auth, flush=True)
    #     pass

    # response = None

    # @client.on("protected_message", namespace="/protected_events")
    # async def protected_message(data):
    #     """Protected message event for socket.io. client"""
    #     print("=== protected_message - data ===")
    #     print(data, flush=True)
    #     nonlocal response
    #     response = data
    #     # assert data == "Protected messages received from client: Hello, world!"

    # await client.connect(
    #     "http://127.0.0.1:80",
    #     socketio_path="socketio/v1",
    #     namespaces=["/protected_events"],
    # )

    # response = await client.emit(
    #     "protected_message", "Hello, world!", namespace="/protected_events"
    # )
    # await client.sleep(1)
    # assert response == "Protected message received from client: Hello, world!"
    # await client.disconnect()
