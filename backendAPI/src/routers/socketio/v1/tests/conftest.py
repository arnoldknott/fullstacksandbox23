from typing import List

# import core.security
# from routers.socketio.v1.base import BaseEvents
from unittest.mock import AsyncMock, patch

import pytest
import socketio
from fastapi import Request

from main import app
from routers.socketio.v1.base import (
    dummy_dependency,
    provide_dummy_dependency,
    resolve_dependency,
    SocketIOServer,
)

# from core.security import get_azure_token_payload


# @pytest.fixture(scope="function")
# def patch_socketio_app(monkeypatch, request):
#     """Patch the get_azure_token_payload function and remount the socketio_app."""

#     async def mock_get_azure_token_payload(token: str | None = None):
#         print("=== mock_get_azure_token_payload ===")
#         return request.param

#     # Unmount the socketio_app
#     app.router.routes = [
#         route for route in app.router.routes if route.path != "/socketio/v1"
#     ]

#     def mocker_function():
#         return request.param

#     monkeypatch.setattr("core.security.decode_token", mocker_function)

#     # Remount the socketio_app
#     app.mount("/socketio/v1", app=socketio_app)

#     yield

#     # # Apply the patch
#     # with patch(
#     #     "routers.socketio.v1.base.BaseEvents.authentication",
#     #     new=AsyncMock(side_effect=mock_get_azure_token_payload),
#     # ):
#     #     # Remount the socketio_app
#     #     app.mount("/socketio/v1", app=socketio_app)
#     #     yield

#     # Unmount the socketio_app after the test
#     app.router.routes = [
#         route for route in app.router.routes if route.path != "/socketio/v1"
#     ]


# @pytest.fixture(scope="function")
# def mocked_azure_token_payload(request, mocker):
#     """Mock the get_azure_token_payload function."""
#     print("=== tests - conftest - mocked_get_azure_token_payload ===")
#     # yield request.param
#     # with patch("core.security.get_azure_token_payload", new_callable=AsyncMock) as mock:
#     #     mock.return_value = request.param
#     #     yield mock
#     print("=== tests - conftest - mocked_get_azure_token_payload - request.param ===")
#     print(request.param)
#     mock = mocker.AsyncMock()
#     mock.return_value = request.param
#     mock.side_effect = lambda *args, **kwargs: mock.return_value
#     print(
#         "=== tests - conftest - mocked_get_azure_token_payload - mock.return_value ==="
#     )
#     print(mock.return_value)
#     return mock


# @pytest.fixture(scope="function")
# def mocked_azure_token_payload(request, mocker):
#     """Mock the get_azure_token_payload function."""
#     print("=== tests - conftest - mocked_get_azure_token_payload ===")
#     mock = mocker.AsyncMock()
#     mock.side_effect = lambda *args, **kwargs: request.param
#     mock.return_value = request.param
#     return mock
#     # with patch("core.security.get_azure_token_payload", new_callable=AsyncMock) as mock:
#     #     mock.return_value = request.param
#     #     yield mock


# @pytest.fixture(scope="function")
# def patch_get_azure_token_payload(monkeypatch, request):
#     """Patch the get_azure_token_payload function."""

#     def mocker_function():
#         return request.param

#     monkeypatch.setattr("core.security.get_azure_token_payload", mocker_function)


@pytest.fixture(scope="function")
def monkeypatch_get_azure_token_payload(monkeypatch, request):
    """Patch the get_azure_token_payload function."""

    async def mocker_function(string: str | None = None):
        print(
            "=== conftest - monkeypatch_get_azure_token_payload - mocker_function ==="
        )
        print(request.param)
        return request.param

    # monkeypatch.setattr(
    #     # "routers.socketio.v1.base.get_azure_token_payload", mocker_function
    #     # "core.security.get_azure_token_payload", mocker_function
    #     # "test_protected_events.get_azure_token_payload",
    #     # mocker_function,
    #     "routers.socketio.v1.base.get_azure_token_payload",
    #     # mocker_function,
    # )
    # monkeypatch.setattr(
    #     "routers.socketio.v1.base.token_decoder",
    #     mocker_function,
    # )
    # monkeypatch.setattr(
    #     main.src.core.security.get_azure_token_payload,
    #     mocker_function,
    #     request.param,
    # )
    # monkeypatch.setattr(core.security, "get_azure_token_payload", mocker_function)
    # monkeypatch.setattr(
    #     routers.socketio.v1.base, "get_azure_token_payload", lambda: mocker_function
    # )


@pytest.fixture(scope="function")
def mock_authentication(request):
    """Mock the authentication method in BaseEvents."""

    def mock_authentication_method(self, auth: str | None = None):
        print("=== mock_authentication_method ===")
        return request.param

    with patch(
        "routers.socketio.v1.base.BaseEvents.authentication",
        new_callable=lambda: AsyncMock(side_effect=mock_authentication_method),
        # new_callable=AsyncMock(
        #     side_effect=lambda mock_authentication_method: request.param
        # ),
        # new=AsyncMock(side_effect=mock_authentication_method),
    ):
        yield


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


@pytest.fixture(scope="function")
async def mock_dummy_dependency_function():
    """Returns a mocked token payload."""

    with patch("routers.socketio.v1.base.dummy_dependency") as mock:
        mock.return_value = "mock_output_dummy_function"
        yield mock


# Mock dependency
@pytest.fixture(scope="function")
async def mock_dummy_dependency(request, input: str | None = None):
    return "mock_output_dummy"


@pytest.fixture(scope="function")
def app_override_dummy_dependency(mock_dummy_dependency):
    """Returns the FastAPI app with dependency override for provide_http_token_payload."""
    app.dependency_overrides[dummy_dependency] = lambda: mock_dummy_dependency
    yield app
    app.dependency_overrides = {}


@pytest.fixture
# @patch("core.security.get_azure_token_payload", mocked_azure_token_payload)
# @patch("routers.socketio.v1.base.BaseEvents.authentication", autospec=True)
async def socketio_client(
    app_override_dummy_dependency,
    mock_dummy_dependency_function,
    mock_dummy_dependency,
    mock_token_payload,
):
    """Provides a socket.io client and connects to it."""
    # mock_get_azure_token_payload.return_value = {"sub": "test"}

    async def _socketio_client(namespaces: List[str] = None):
        # client = socketio.AsyncClient(logger=True, engineio_logger=True)
        client = socketio.AsyncClient()

        # with patch("core.security.decode_token") as mock:
        #     mock.return_value = {"some": "payload"}
        #     yield mock

        # app.dependency_overrides[dummy_dependency] = lambda: mock_dummy_dependency

        scope = {
            "type": "http",
            "query_string": b"some_query_string_from_fixture_socketio_client",
            # "headers": [{"Authorization": "input_dummy_header"}],
            # "headers": [],
            "headers": [
                [b"Authorization", b"Bearer scope_dummy_token"],
                [b"content-type", b"application/json"],
            ],
            "path": "/",
            "method": "GET",
        }
        request = Request(scope=scope)
        dummy_dependency_response = await resolve_dependency(
            provide_dummy_dependency, request
        )
        print("=== tests - conftest - socketio_client - dummy_dependency_response ===")
        print(dummy_dependency_response)

        test_server = SocketIOServer(app_override_dummy_dependency)
        dummy_dependency_response_socketio_server = (
            await test_server.resolve_dependency_socketio_server(
                provide_dummy_dependency,
                request,
            )
        )
        print(
            "=== tests - conftest - socketio_client - dummy_dependency_response_socketio_server ==="
        )
        print(dummy_dependency_response_socketio_server)

        @client.event
        def connect():
            """Connect event for socket.io."""
            pass

        # async with mocker.patch(
        #     "core.security.get_azure_token_payloads", new=mocked_azure_token_payload
        # ):

        # async def mocker_function(string: str | None = None):
        #     return {"some": "value"}

        # monkeypatch.setattr("conftest.get_azure_token_payload", mocker_function)

        # print("=== tests - conftest - socketio_client - mocked_azure_token_payload ===")
        # token_payload = await get_azure_token_payload(None)
        # print("=== tests - conftest - socketio_client - token_payload ===")
        # print(token_payload)

        # with patch.object(
        #     routers.socketio.v1.base.BaseEvents.authentication, "get_azure_token_payload", lambda: {"sub": "test"}
        # ):

        # mocked_authentication.return_value = {"sub": "test"}

        # mock = AsyncMock()
        # mock.side_effect = lambda value: {"sub": "test"}
        # # mock.return_value = {"sub": "test"}

        # patcher = patch("routers.socketio.v1.base.BaseEvents.authentication", mock)
        # patcher.start()
        # with patch.object(
        #     routers.socketio.v1.base.BaseEvents, "authentication", mocker_function
        # ):
        await client.connect(
            "http://127.0.0.1:80",
            socketio_path="socketio/v1",
            namespaces=namespaces,
            auth="dummy",
        )
        yield client
        await client.disconnect()
        # patcher.stop()
        # app.dependency_overrides = {}

    return _socketio_client
