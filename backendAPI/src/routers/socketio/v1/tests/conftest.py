import asyncio
import uuid
from datetime import datetime
from typing import List, Optional
from unittest.mock import patch

import pytest
import socketio
import uvicorn
from pydantic import BaseModel

from core.cache import redis_session_client
from routers.socketio.v1.demo_namespace import demo_namespace_router
from routers.socketio.v1.demo_resource import (
    demo_resource_router as demo_resource_namespace_router,
)
from routers.socketio.v1.interactive_documentation import (
    interactive_documentation_router,
)
from routers.socketio.v1.public_namespace import public_namespace_router
from tests.utils import sessions

# Mocking the sessions for testing purposes.


# === Structure of mocked sessions in redis ===
# That would include the cache, that means we need a fixture that puts session-ids
# in the cache and return the token_payloads directly from there. That means putting token payloads
# into the cache, which is not done yet.
# _________________________________________________
# | session-id     | token_payload                |
# |________________|______________________________|
# | admin-with-... | token_payload_admin-with-... |
# | user1-with-... | token_payload_user1-with-... |
# |________________|______________________________|
#
# means: get_azure_token_from_cache() gets the token content
# instead of the user_account, as input
# and simply returns that token content.
# no need to mock based on input any more.
# just make sure that parameterization is now done with the session-id
# and session-id matches the token_payload in the cache.


@pytest.fixture(scope="function")
async def mock_sessions(request):
    """Chooses the right token-payload based on which session should be mocked."""

    if hasattr(request, "param"):

        results = []

        def choose_token_payload(*args):
            """Chooses the right token-payload based on which session should be mocked."""
            # Compute the return value based on the arguments
            return_token = request.param[int(args[0])]
            results.append(return_token)
            return return_token

        with patch(
            "routers.socketio.v1.base.BaseNamespace._get_token_payload_if_authenticated"
        ) as mocked_sessions:
            mocked_sessions.side_effect = choose_token_payload
            yield {"mock": mocked_sessions, "mocked_results": results}


@pytest.fixture(scope="function")
async def mock_get_user_account_from_session_cache():
    """Returns a mocked token."""

    with patch("core.security.get_user_account_from_session_cache") as mock:
        mock.return_value = {
            "userName": "testuser",
            "homeAccountId": "testhometenantid.testhomeaccounid",
        }
        yield mock


# Setting up socketio server side for testing


@pytest.fixture(scope="package", autouse=True)
def load_test_sessions_into_redis():
    """Loads test sessions into Redis for testing purposes."""

    for session in sessions:
        # This is where the mock happens:
        # instead of linking the session_id with the microsoftAccount,
        # it links microsoftAccount with the token payload
        # This enables that the production code from get_user_account_from_session_cache
        # to accesses the cache - afterwards the get_azure_token_from_cache and
        # get_azure_token_payload functions are mocked to just pass the raw data through.
        redis_session_client.json().set(
            f"session:{session['session_id']}",
            ".",
            {"microsoftAccount": session["token_payload"]},
        )

    yield
    for session in sessions:
        redis_session_client.json().delete(f"session:{session['session_id']}")


@pytest.fixture(scope="package", autouse=True)
async def socketio_test_server(
    # mock_azure_token_in_redis,
    load_test_sessions_into_redis,
):
    """Provide a socket.io server for multiple patched users.
    This fixture skips Authorization but still checks Authentication."""
    # mock_azure_token_in_redis

    def return_input(*args):
        """Chooses the token associated with the session ID from redis."""
        # Compute the return value based on the arguments
        mocked_token = args[0]
        return mocked_token

    with patch("core.security.get_azure_token_from_cache") as mocked_user_account:
        mocked_user_account.side_effect = return_input
        with patch("core.security.get_azure_token_payload") as mocked_decode_token:
            mocked_decode_token.side_effect = return_input

            sio = socketio.AsyncServer(
                async_mode="asgi", logger=True, engineio_logger=True
            )
            app = socketio.ASGIApp(sio, socketio_path="socketio/v1")

            config = uvicorn.Config(app, host="127.0.0.1", port=8669, log_level="info")
            server = uvicorn.Server(config)

            asyncio.create_task(server.serve())
            sio.register_namespace(public_namespace_router)
            sio.register_namespace(demo_namespace_router)
            sio.register_namespace(demo_resource_namespace_router)
            sio.register_namespace(interactive_documentation_router)
            await asyncio.sleep(1)
            yield sio
            await server.shutdown()


# Setting up socketio client side for testing:


####### GENERIC TEST CLIENT FOR SOCKET.IO - WORKS: keep! (start) #######


@pytest.fixture(scope="function")
def session_id_selector(request):
    """Returns the session id from an array of parameters based on the index."""

    print(f"session_id_selector: {request}")  # Debugging output

    def _session_id_selector(index: int = 0):
        """Selects the session id based on the index."""
        if hasattr(request, "param"):
            return request.param[index]
        return None

    return _session_id_selector


class ClientConfig(BaseModel):
    """Model to hold a namespace."""

    namespace: str
    events: List[str] = []


@pytest.fixture(scope="function")
def current_token_payload(session_id_selector: callable):
    """Returns the current token payload based on the session id selector."""

    def _current_token_payload(index: int = 0):
        """Returns the current token payload based on the session id selector."""
        session_id = session_id_selector(index)
        if session_id:
            token_payload = [
                session["token_payload"]
                for session in sessions
                if session["session_id"] == session_id
            ][0]

            return token_payload
        return None

    return _current_token_payload


@pytest.fixture(scope="function")
async def current_user_from_session_id(
    session_id_selector: callable,
    current_user_from_azure_token: callable,
    current_token_payload: callable,
):
    """Returns the current user from the session id selector."""

    async def _current_user_from_session_id(index: int = 0):
        """Returns the current user from the session id selector."""
        session_id = session_id_selector(index)
        if session_id:
            user_account = await current_user_from_azure_token(
                current_token_payload(index)
            )
            return user_account
        return None

    return _current_user_from_session_id


# TBD: consider refactoring into a class - and call instantiation with await ClassName()
# add connect, logging and so on as methods
# connect automatically, if not auto_connect = false in instance creation
# pass query parameters in instantiation
#
# This one connects to a socketio server in FastAPI:
# host="http://127.0.0.1:80" => production server
# host="http://127.0.0.1:8669" => test server from fixture socketio_test_server
@pytest.fixture(scope="function")
async def socketio_test_client(session_id_selector: uuid.UUID):
    """Provides a socket.io client for testing with a specific session ID.

        Args:
        client_config (List[ClientConfig]): List of namespaces and their events,
            where each namespace is a dictionary with keys
            - "name" (string), for example "/demo-namespace"
            - "events" (list of strings), ["submit", "transfer", "deleted"].
        query_parameters (dict): Query parameters to include in the connection.
            e.g. {"request-access-data": "true", "parent-id": "123e4567-e89b-12d3-a456-426614174000"}

    Yields:
        AsyncClient: An instance of the socket.io client connected to the server.
        dict: A dictionary containing responses for each namespace and event.
        e.g. {"namespace": {"event": ["response_data"]}}
    """

    async def _socketio_test_client(
        client_config: ClientConfig,
        index_of_session_id_parameter: int = 0,
        query_parameters: dict = None,
        logs: Optional[List[dict]] = None,
    ):
        client = socketio.AsyncClient(logger=True, engineio_logger=True)
        session_id = session_id_selector(index_of_session_id_parameter)

        def make_handler(event_name):
            async def handle_event(data):
                """Handles the event and appends data to responses."""
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
        for config in client_config:
            namespace = config["namespace"]
            responses[namespace] = {}
            if "events" in config:
                events = config["events"]
                for event in events:
                    responses[namespace][event] = []

                    client.on(event, handler=make_handler(event), namespace=namespace)

        # server_url="http://127.0.0.1:8669" => test server from fixture socketio_test_server
        # server_host="http://127.0.0.1:80" => server from code
        server_url = "http://127.0.0.1:8669"
        if query_parameters:
            query_string = "&".join(
                f"{key}={value}" for key, value in query_parameters.items()
            )
            server_url += f"?{query_string}"
        all_namespaces = [namespace["namespace"] for namespace in client_config]
        await client.connect(
            server_url,
            socketio_path="socketio/v1",
            namespaces=all_namespaces,
            auth={"session-id": str(session_id)},
        )
        connection = {
            "client": client,
            "responses": responses,
            "logs": logs if logs is not None else None,
        }
        yield connection
        await client.disconnect()

    return _socketio_test_client


####### GENERIC TEST CLIENT FOR SOCKET.IO - WORKS: keep! (end) #######
