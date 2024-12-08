import asyncio
from typing import List
from unittest.mock import patch

import pytest
import socketio
import uvicorn


@pytest.fixture(scope="function")
async def mock_token_payload(request):
    """Returns a mocked token payload."""

    # print("=== mock_token_payload ===")
    # print(request.param)

    with patch("core.security.decode_token") as mock:
        mock.return_value = request.param
        yield mock


@pytest.fixture(scope="function")
async def mock_get_user_account_from_session_cache():
    """Returns a mocked token."""

    with patch("core.security.get_user_account_from_session_cache") as mock:
        mock.return_value = {
            "userName": "testuser",
            "homeAccountId": "testhometenantid.testhomeaccounid",
        }
        yield mock


@pytest.fixture(scope="function")
async def mock_get_azure_token_from_cache():
    """Returns a mocked token."""

    with patch("core.security.get_azure_token_from_cache") as mock:
        mock.return_value = "ey-fake-token-from_cache"
        yield mock


@pytest.fixture()
async def socketio_server(
    mock_token_payload,
    mock_get_azure_token_from_cache,
    mock_get_user_account_from_session_cache,
):
    """Provide a socket.io server."""

    sio = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)
    app = socketio.ASGIApp(sio, socketio_path="socketio/v1")

    # @sio.event
    # def connect(sid, environ):
    #     print("connect ", sid, flush=True)

    # @sio.event
    # async def chat_message(sid, data):
    #     await sio.emit("chat_message", f"You are connected to test server with {sid}")
    #     print("=== chat_message - data ===")
    #     print(data)

    # @sio.event
    # def disconnect(sid):
    #     print("disconnect ", sid)

    config = uvicorn.Config(app, host="127.0.0.1", port=8669, log_level="info")
    server = uvicorn.Server(config)

    ### Works with aiohttp, too:

    # sio = socketio.AsyncServer()
    # app = web.Application()# add the path "/socketio/v1" here?
    # sio.attach(app)

    # @sio.event
    # def connect(sid, environ):
    #     print("connect ", sid, flush=True)

    # @sio.event
    # async def chat_message(sid, data):
    #     await sio.emit("chat_message", f"You are connected to test server with {sid}")
    #     print("=== chat_message - data ===")
    #     print(data)

    # @sio.event
    # def disconnect(sid):
    #     print("disconnect ", sid)

    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, "localhost", 8669)
    # await site.start()

    ### end WORKS with aiohttp

    asyncio.create_task(server.serve())
    await asyncio.sleep(1)
    yield sio
    await server.shutdown()


# This one connects to the socketio server in the main FastAPI application:
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


# This one connects to the production socketio server in FastAPI:
@pytest.fixture
async def socketio_client():
    """Provides a socket.io client and connects to it."""
    # Note, this one can only make real connections without authentication

    async def _socketio_client(namespaces: List[str] = None):
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        # @client.event
        # def connect(namespace=namespaces[0]):
        #     """Connect event for socket.io."""
        #     return "OK from client"
        #     # pass

        # @client.event
        # def demo_message(data, namespace=namespaces[0]):
        #     print("=== demo_message - listening to server here ===")
        #     print("=== conftest - socketio_client - protected_message - data ===")
        #     print(data)
        #     pass

        await client.connect(
            "http://127.0.0.1:80",
            socketio_path="socketio/v1",
            namespaces=namespaces,
            # auth={"session_id": "testsessionid"},
        )
        yield client
        await client.disconnect()

    return _socketio_client


# This one connects to the mocked test socketio server from the fixture socketio_server:
@pytest.fixture
async def socketio_patched_client():
    """Provides a socket.io client and connects to it."""

    async def _socketio_client(namespaces: List[str] = None):
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        await client.connect(
            "http://127.0.0.1:8669",
            socketio_path="socketio/v1",
            namespaces=namespaces,
            auth={"session_id": "testsessionid"},
        )
        yield client
        await client.disconnect()

    return _socketio_client
