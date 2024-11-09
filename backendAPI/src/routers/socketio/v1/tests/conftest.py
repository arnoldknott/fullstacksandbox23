import pytest
import socketio
from typing import List


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


# @pytest.fixture
# async def client_with_event_handler(socketio_client):
#     """Provide a client event handler for a specific event and the first namespace in the passed list."""

#     async def _client_event_handler(event_name, namespaces):
#         async for client in socketio_client(namespaces):
#             # response = None
#             # response_event = asyncio.Event()

#             # @client.on(event_name, namespace=namespaces[0])
#             # async def handler(data):
#             #     nonlocal response
#             #     response = data
#             #     response_event.set()

#             #     print("=== client_with_event_handler - handler - data ===")
#             #     print(data)
#             #     print("=== client_with_event_handler - handler - response ===")
#             #     print(response)

#             # await client.sleep(1)

#             # print("=== client_with_event_handler - response ===")
#             # print(response)

#             # yield client, response, response_event
#             yield client
#             await client.disconnect()

#     return _client_event_handler
