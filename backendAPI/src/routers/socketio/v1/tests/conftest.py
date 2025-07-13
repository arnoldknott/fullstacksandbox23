import asyncio
from datetime import datetime
from typing import List, Optional
from unittest.mock import patch

from routers.socketio.v1.demo_namespace import DemoNamespace
from pydantic import BaseModel
import pytest
import socketio
import uvicorn


# Mocking the token payload for testing purposes.


@pytest.fixture(scope="module")
async def mock_token_payload(request):
    """Returns a mocked token payload."""

    if hasattr(request, "param"):
        with patch("core.security.decode_token") as mock:
            mock.return_value = request.param
            yield request.param


@pytest.fixture(scope="module")
async def mock_get_user_account_from_session_cache():
    """Returns a mocked token."""

    with patch("core.security.get_user_account_from_session_cache") as mock:
        mock.return_value = {
            "userName": "testuser",
            "homeAccountId": "testhometenantid.testhomeaccounid",
        }
        yield mock


@pytest.fixture(scope="module")
async def mock_get_azure_token_from_cache():
    """Returns a mocked token."""

    with patch("core.security.get_azure_token_from_cache") as mock:
        mock.return_value = "a-fake-token-from_cache"
        yield mock


# Setting up socketio server side for testing


@pytest.fixture(scope="module")
async def socketio_test_server(
    mock_token_payload,
    mock_get_azure_token_from_cache,
    mock_get_user_account_from_session_cache,
):
    """Provide a socket.io server."""
    mock_token_payload

    sio = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)
    app = socketio.ASGIApp(sio, socketio_path="socketio/v1")

    config = uvicorn.Config(app, host="127.0.0.1", port=8669, log_level="info")
    server = uvicorn.Server(config)

    asyncio.create_task(server.serve())
    await asyncio.sleep(1)
    yield sio
    await server.shutdown()


@pytest.fixture(scope="module")
async def provide_namespace_server(
    socketio_test_server: socketio.AsyncServer,
):
    """Provides a socket.io server with a specific namespace."""

    async def _provide_namespace_server(namespaces: List[socketio.AsyncNamespace]):
        sio = socketio_test_server
        for namespace in namespaces:
            sio.register_namespace(namespace)

        return sio

    return _provide_namespace_server


# @pytest.fixture(scope="module")
# async def mock_token_payloads(request):
#     """Returns multiple mocked token payload."""

#     if hasattr(request, "param"):
#         with patch("core.security.decode_token") as mock:
#             mock.return_value = request.param
#             yield request.param


@pytest.fixture(scope="module")
async def mock_session(request):
    """Chooses the right token-payload based on which session should be mocked."""

    # TBD: consider moving the mock deeper into decode token from security, as this short-cuts the security layers above
    # or rename into "no authentication checked" or so.

    if hasattr(request, "param"):

        def choose_token_payload(*args, **kwargs):
            """Chooses the right token-payload based on which session should be mocked."""
            # args/kwargs are the arguments passed by the production code
            print("=== chose_token_payload - called with:", args, kwargs)
            print(
                "=== chose_token_payload - request.param is:", request.param, flush=True
            )
            # Compute the return value based on the arguments
            return_token = request.param[int(args[0])]
            print("=== return this token content ===")
            print(return_token, flush=True)
            return return_token

        with patch(
            "routers.socketio.v1.base.BaseNamespace._get_token_payload_if_authenticated"
        ) as mocked_session:
            await mocked_session("abcd")
            print("=== mock_session - request.param ===")
            print(request.param, flush=True)
            print("=== mock_session - mocked_session.call_args ===")
            print(mocked_session.call_args, flush=True)
            print("=== mock_session - mocked_session.called ===")
            print(mocked_session.called, flush=True)
            print("=== mock_session - mocked_session.call_count ===")
            print(mocked_session.call_count, flush=True)
            print("=== mock_session - mocked_session.call_args_list ===")
            print(mocked_session.call_args_list, flush=True)
            print("=== mock_session - mocked_session.mock_calls ===")
            print(mocked_session.mock_calls, flush=True)
            print("=== mock_session[0] - request.param ===")
            print(request.param[0], flush=True)
            # selected_token = int(mocked_session.call_args)
            mocked_session.side_effect = choose_token_payload
            print("=== mock_session - mocked_session.side_effect ===")
            print(mocked_session.side_effect, flush=True)
            mocked_session.return_value = request.param[0]
            # yield request.param[0]
            yield mocked_session


# This patches different users and allows therefore clients from different users to talk to each other.
@pytest.fixture(scope="module")
async def socketio_test_server_with_multiple_patched_token_payloads(
    mock_session,
    # mock_get_azure_token_from_cache,
    # mock_get_user_account_from_session_cache,
):
    """Provide a socket.io server."""
    mock_session
    print(
        "=== socketio_test_server_with_multiple_patched_token_payloads - mock_session ==="
    )
    print(mock_session.call_args, flush=True)

    sio = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)
    app = socketio.ASGIApp(sio, socketio_path="socketio/v1")

    config = uvicorn.Config(app, host="127.0.0.1", port=8670, log_level="info")
    server = uvicorn.Server(config)

    asyncio.create_task(server.serve())
    sio.register_namespace(DemoNamespace("/demo-namespace"))
    await asyncio.sleep(1)
    yield sio
    await server.shutdown()


# Setting up socketio client side for testing:


@pytest.fixture
async def socketio_test_client_with_multiple_mocked_users_on_server(
    socketio_test_server_with_multiple_patched_token_payloads, mock_session
):
    """Provides a socket.io client and connects to it."""
    socketio_test_server_with_multiple_patched_token_payloads

    async def _socketio_test_client_with_multiple_mocked_users_on_server(
        namespaces: List[str] = None, query_parameters: dict = None, token_number=1
    ):
        socketio_test_server_with_multiple_patched_token_payloads
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        server_url = "http://127.0.0.1:8670"
        if query_parameters:
            query_string = "&".join(
                f"{key}={value}" for key, value in query_parameters.items()
            )
            server_url += f"?{query_string}"
        # await client.sleep(1)
        print(
            "=== socketio_test_client_with_multiple_mocked_users_on_server - mock_session.call_args.args - before connect ==="
        )
        print(mock_session.call_args.args, flush=True)
        await client.connect(
            # server_url,
            "http://127.0.0.1:8670",
            socketio_path="socketio/v1",
            namespaces=namespaces,
            auth={"session-id": str(token_number)},
        )
        # await client.sleep(1)
        print(
            "=== socketio_test_client_with_multiple_mocked_users_on_server - mock_session.call_args.args - after connect ==="
        )
        print(mock_session.call_args.args, flush=True)

        yield client
        # client.sleep(1)  # Give time for the disconnect to be processed
        await client.disconnect()

    return _socketio_test_client_with_multiple_mocked_users_on_server


# This one connects to a socketio server in FastAPI:
# host="http://127.0.0.1:80" => production server
# host="http://127.0.0.1:8669" => test server from fixture socketio_test_server
@pytest.fixture
async def socketio_test_client():
    """Provides a socket.io client and connects to it."""

    async def _socketio_test_client(
        namespaces: List[str] = None,
        server_host: str = "http://127.0.0.1:8669",
        auto_connect: bool = False,
    ):
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        if server_host == "http://127.0.0.1:8669":
            socketio_test_server

        async def connect_to_test_client(
            query_parameters: dict = None,
        ):
            """Connects to the socket.io client and yields it."""

            server_url = server_host
            if query_parameters:
                query_string = "&".join(
                    f"{key}={value}" for key, value in query_parameters.items()
                )
                server_url += f"?{query_string}"

            await client.connect(
                server_url,
                socketio_path="socketio/v1",
                namespaces=namespaces,
                auth={"session-id": "testsessionid"},
            )
            # await client.sleep(1)

        client.connect_to_test_client = connect_to_test_client

        if auto_connect:
            await connect_to_test_client()

        yield client
        # client.sleep(1)  # Give time for the disconnect to be processed
        await client.disconnect()

    return _socketio_test_client


class Namespaces(BaseModel):
    """Model to hold a namespace."""

    name: str
    events: List[str] = []


@pytest.fixture(scope="function")
async def socketio_test_client_with_events(socketio_test_client):
    """Provides a socket.io client with event handlers.

    Args:
        namespaces_and_events (List[Namespaces]): List of namespaces and their events,
            where each namespace is a dictionary with "name" and "events" keys.
        server_host (str): The server host to connect to.
            server_host="http://127.0.0.1:80" => server from code
            server_host="http://127.0.0.1:8669" => test server from fixture socketio_test_server
        query_parameters (dict): Query parameters to include in the connection.
            e.g. {"request-access-data": "true", "parent-id": "123e4567-e89b-12d3-a456-426614174000"}

    Yields:
        AsyncClient: An instance of the socket.io client connected to the server.
        dict: A dictionary containing responses for each namespace and event.
        e.g. {"namespace": {"event": ["response_data"]}}
    """

    async def _socketio_test_client_with_events(
        namespaces_and_events: List[Namespaces],
        server_host: str = "http://127.0.0.1:8669",
        query_parameters: dict = None,
        logs: Optional[List[dict]] = None,
    ):

        namespaces = [namespace["name"] for namespace in namespaces_and_events]
        async for client in socketio_test_client(namespaces, server_host):

            def make_handler(event_name):
                async def handle_event(data):
                    """Handles the event and appends data to responses."""
                    # print(f"=== Received event '{event_name}': {data} ===", flush=True)
                    nonlocal responses
                    if logs is not None:
                        logs.append(
                            {
                                "event": event_name,
                                "timestamp": datetime.now(),
                                "data": data,
                            }
                        )
                    responses[namespace][event_name].append(data)

                return handle_event

            responses = {}
            for namespace_event in namespaces_and_events:
                namespace = namespace_event["name"]
                events = namespace_event["events"]
                responses[namespace] = {}
                for event in events:
                    responses[namespace][event] = []

                    client.on(event, handler=make_handler(event), namespace=namespace)

            await client.connect_to_test_client(query_parameters)

            if logs is None:
                yield client, responses
            else:
                yield client, responses, logs

    return _socketio_test_client_with_events


@pytest.fixture(scope="function")
async def socketio_client_for_demo_namespace(
    socketio_test_client_with_events,
):
    """Provides a socket.io client for the demo namespace with event handlers."""

    async def _socketio_client_for_demo_namespace(
        query_parameters: dict = None,
        logs: List[dict] = None,
    ):

        demo_namespace_with_events = [
            {
                "name": "/demo-namespace",
                "events": ["demo_message"],
            }
        ]

        async for socketio_test_client in socketio_test_client_with_events(
            demo_namespace_with_events, query_parameters=query_parameters, logs=logs
        ):
            yield socketio_test_client

    return _socketio_client_for_demo_namespace


@pytest.fixture(scope="function")
async def socketio_client_for_demo_resource_namespace(
    socketio_test_client_with_events,
):
    """Provides a socket.io client for the demo namespace with event handlers."""

    async def _socketio_client_for_demo_resource_namespace(
        query_parameters: dict = None,
        logs: List[dict] = None,
    ):

        demo_namespace_with_events = [
            {
                "name": "/demo-resource",
                "events": [
                    "transfer",
                    "deleted",
                    "status",
                ],
            }
        ]

        async for socketio_test_client in socketio_test_client_with_events(
            demo_namespace_with_events, query_parameters=query_parameters, logs=logs
        ):
            yield socketio_test_client

    return _socketio_client_for_demo_resource_namespace
