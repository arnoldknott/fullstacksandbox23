import pytest
import socketio


@pytest.fixture
async def socketio_client():
    client = socketio.AsyncSimpleClient()
    await client.connect("http://127.0.0.1:80", socketio_path="socketio/v1")
    yield client
    await client.disconnect()
