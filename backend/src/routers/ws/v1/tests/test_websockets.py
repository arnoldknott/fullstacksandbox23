import pytest
from httpx import AsyncClient
from websockets.asyncio.client import connect


@pytest.mark.anyio
async def test_public_websocket(
    async_client: AsyncClient,
):
    """Test the public websocket."""
    async with connect("ws://127.0.0.1:80/ws/v1/public_web_socket") as websocket:
        await websocket.send("Hello, world!")
        response = await websocket.recv()
        assert response == "Message received from client: Hello, world!"
