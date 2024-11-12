from typing import List
from unittest.mock import patch

import pytest
import socketio


@pytest.fixture
async def socketio_simple_client():
    """Provide a simple socket.io client."""
    # TBD: change to AsyncClient
    client = socketio.AsyncSimpleClient()
    await client.connect(
        "http://127.0.0.1:80",
        socketio_path="socketio/v1",
    )
    yield client
    await client.disconnect()


@pytest.fixture
async def socketio_client():
    """Provides a socket.io client and connects to it."""
    # Note, this one can only make real connections without authentication
    # The server cannot be patched, as this client is running on a different machine

    async def _socketio_client(namespaces: List[str] = None):
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        @client.event
        def connect(namespace="/protected_events"):
            """Connect event for socket.io."""
            return "OK from client"
            # pass

        @client.event
        def protected_message(data, namespace="/protected_events"):
            print("=== protected_message - listening to server here ===")
            print("=== conftest - socketio_client - protected_message - data ===")
            print(data)
            pass

        await client.connect(
            "http://127.0.0.1:80",
            socketio_path="socketio/v1",
            namespaces=namespaces,
        )
        yield client
        await client.disconnect()

    return _socketio_client


@pytest.fixture(scope="function")
async def mock_token_payload(request):
    """Returns a mocked token payload."""

    print("=== mock_token_payload ===")
    print(request.param)

    with patch("core.security.decode_token") as mock:
        mock.return_value = request.param
        # mock.return_value = {
        #     "some": "payload"
        # }  # TBD: replace with parameterization for different payloads
        yield mock


@pytest.fixture(scope="function")
async def provide_socketio_connection(mock_token_payload):
    """Provide a socket.io connection with a mocked token payload."""
    pass
    # TBD: all server-side - no client!
    # TBD: implement: call on_connect() with mocked token payload
    # TBD: yield the connection
    # TBD: implement: call on_disconnect()
