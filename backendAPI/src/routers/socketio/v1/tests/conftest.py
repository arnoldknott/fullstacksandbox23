
import pytest
import socketio


@pytest.fixture
async def socketio_simple_client():
    """Provide a simple socket.io client."""
    # TBD: change to AsyncClient
    client = socketio.AsyncSimpleClient()
    await client.connect("http://127.0.0.1:80", socketio_path="socketio/v1")
    yield client
    await client.disconnect()


@pytest.fixture
async def socketio_client():
    """Provide a socket.io client."""
    client = socketio.AsyncClient()
    await client.connect(
        "http://127.0.0.1:80",
        socketio_path="socketio/v1",
        namespaces=["/protected_events"],
    )
    yield client
    await client.disconnect()


@pytest.fixture
async def client_event_handler(socketio_client):
    """Provide a client event handler for a specific event and namespace."""

    async def _client_event_handler(event_name, namespace):
        response = None

        @socketio_client.on(event_name, namespace=namespace)
        async def handler(data):
            nonlocal response
            response = data

        async def emit(data):
            print("=== client_event_handler - emit - data ===")
            print(data, flush=True)
            print("=== client_event_handler - emit - response ===")
            print(response, flush=True)
            await socketio_client.emit(event_name, data, namespace=namespace)
            return response

        return emit

    return _client_event_handler
