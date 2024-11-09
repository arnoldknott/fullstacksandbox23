import pytest
import socketio
from typing import List


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

    async def _socketio_client(namespaces: List[str] = None):
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        @client.event
        def connect():
            """Connect event for socket.io."""
            pass

        await client.connect(
            "http://127.0.0.1:80",
            socketio_path="socketio/v1",
            namespaces=namespaces,
        )
        yield client
        await client.disconnect()

    return _socketio_client
