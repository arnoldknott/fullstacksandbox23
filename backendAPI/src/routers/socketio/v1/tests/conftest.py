import asyncio
import uuid
from datetime import datetime
from typing import List, Optional
from unittest.mock import patch

from core.security import CurrentAccessToken
from core.types import CurrentUserData
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


####### GENERIC TEST CLIENT FOR SOCKET.IO - working version #######


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
def current_token_payload(session_ids: List[uuid.UUID]):
    """Returns the current token payload based on the session id selector."""

    def _current_token_payload(index: int = 0):
        """Returns the current token payload based on the session id selector."""
        session_id = session_ids[index]
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
    session_ids: List[uuid.UUID],
    current_user_from_azure_token: callable,
    current_token_payload: callable,
):
    """Returns the current user from the session id selector."""

    async def _current_user_from_session_id(index: int = 0):
        """Returns the current user from the session id selector."""
        session_id = session_ids[index]
        if session_id:
            user_account = await current_user_from_azure_token(
                current_token_payload(index)
            )
            return user_account
        return None

    return _current_user_from_session_id


# TBD: consider refactoring into a class - and call instantiation with await ClassName()
# add connect, logging and so on as methods
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


####### GENERIC TEST CLIENT FOR SOCKET.IO - working version #######


####### classed based TEST CLIENT FOR SOCKET.IO - refactor into this #######


@pytest.fixture(scope="function")
def session_ids(request):
    """Returns the session id from an array of parameters based on the index."""

    if hasattr(request, "param"):
        return request.param


# Provides a class with a socket.io client for testing with a specific session ID.

# Args:
#     client_config (List[ClientConfig]): List of namespaces and their events,
#         where each namespace is a dictionary with keys
#         - "name" (string), for example "/demo-namespace"
#         - "events" (list of strings), ["submit", "transfer", "deleted"].
#     session_id (uuid.UUID): The session ID to use for the connection.
#     query_parameters (dict): Query parameters to include in the connection.
#         e.g. {"request-access-data": "true", "parent-id": "123e4567-e89b-12d3-a456-426614174000"}

# Yields:
#     AsyncClient: An instance of the socket.io client connected to the server.
#     dict: A dictionary containing responses for each namespace and event.
#     e.g. {"namespace": {"event": ["response_data"]}}
#
# Usage:
# TBD: document


class SocketIOTestConnection:
    """Class to handle socket.io client connections and events."""

    def __init__(
        self,
        client_config: ClientConfig,
        session_id: uuid.UUID,
        query_parameters: dict = None,
    ):
        self.client_config = client_config
        self.session_id = session_id
        self.query_parameters = query_parameters or {}
        self.client = socketio.AsyncClient(logger=True, engineio_logger=True)
        self.responseData = {}

        # Attaching the event handlers for the client during initialization:
        def make_handler(event_name):
            async def handle_event(data):
                """Handles the event and appends data to responses."""
                nonlocal responses
                self.responseData[namespace][event_name].append(data)

            return handle_event

        responses = self.responseData
        for config in client_config:
            namespace = config["namespace"]
            responses[namespace] = {}
            if "events" in config:
                events = config["events"]
                for event in events:
                    responses[namespace][event] = []
                    self.client.on(
                        event, handler=make_handler(event), namespace=namespace
                    )

    async def __aenter__(self):
        """Connect the client when entering the context."""
        # await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Disconnect the client when exiting the context."""
        await self.client.disconnect()

    async def connect(self, query_parameters: dict = None):
        if query_parameters is not None:
            self.query_parameters = query_parameters
        """Connects to the socket.io server with the specified namespaces."""
        # server_url="http://127.0.0.1:8669" => test server from fixture socketio_test_server
        # server_host="http://127.0.0.1:80" => server from code
        server_url = "http://127.0.0.1:8669"
        if self.query_parameters:
            query_string = "&".join(
                f"{key}={value}" for key, value in self.query_parameters.items()
            )
            server_url += f"?{query_string}"
        all_namespaces = [namespace["namespace"] for namespace in self.client_config]
        await self.client.connect(
            server_url,
            socketio_path="socketio/v1",
            namespaces=all_namespaces,
            auth={"session-id": str(self.session_id)},
        )

    async def client(self):
        """Returns the socket.io client instance."""
        return self.client

    def responses(self, event: str | None = None, namespace: str | None = None):
        """Returns the responses for a specific namespace and event."""
        # print("=== self.responseData ===")
        # print(self.responseData, flush=True)
        if namespace is None:
            namespace = self.client_config[0]["namespace"]
        if event is None:
            index = next(
                i
                for i, obj in enumerate(self.client_config)
                if obj.get("namespace") == namespace
            )
            event = self.client_config[index]["events"][0]
        if namespace in self.responseData and event in self.responseData[namespace]:
            return self.responseData[namespace][event]
        else:
            raise ValueError(f"No responses found for {namespace} and {event}.")

    def token_payload(self):
        """Returns the current token payload for the user of this session."""
        token_payload = [
            session["token_payload"]
            for session in sessions
            if session["session_id"] == self.session_id
        ][0]
        return token_payload

    async def current_user(self) -> CurrentUserData:
        """Returns the current user for the user of this session."""
        current_user = None
        token = CurrentAccessToken(self.token_payload())
        current_user = await token.provides_current_user()
        return current_user

        # return await get_current_user_from_azure_token(self.token_payload())

        # async def _current_user():
        #     """Returns the current user for the user of this session."""
        #     user_account = await current_user_from_azure_token(self.token_payload())
        #     return user_account

        # return _current_user


@pytest.fixture(scope="function")
def socketio_test_client_class(request, session_ids):
    """Fixture to provide a class-based socket.io test client."""

    async def _socketio_test_client_class(
        client_config: ClientConfig,
        session_id: Optional[uuid.UUID] = None,
        query_parameters: Optional[dict] = None,
    ):
        """Creates an instance of SocketIOTestClient."""
        if not session_id:
            session_id = session_ids[0]

        connection = SocketIOTestConnection(
            client_config,
            session_id,
            query_parameters=query_parameters,
        )
        await connection.__aenter__()

        def cleanup():
            # Schedule disconnect for the event loop
            asyncio.get_event_loop().create_task(connection.__aexit__(None, None, None))

        request.addfinalizer(cleanup)

        return connection

    return _socketio_test_client_class


@pytest.fixture(scope="function")
def socketio_test_client_demo_namespace(socketio_test_client_class):
    """Fixture to provide a socket.io test client for the demo namespace."""

    async def _socketio_test_client_demo_namespace(
        session_id: Optional[uuid.UUID] = None,
        query_parameters: Optional[dict] = None,
    ):
        """Factory function for creating a socket.io test client for the demo namespace."""
        client_config = [
            {
                "namespace": "/demo-namespace",
                "events": ["demo_message"],
            }
        ]

        """Creates an instance of SocketIOTestClient for the demo namespace."""
        return await socketio_test_client_class(
            client_config, session_id, query_parameters
        )

    return _socketio_test_client_demo_namespace


@pytest.fixture(scope="function")
def socketio_test_client_demo_resource_namespace(socketio_test_client_class):
    """Fixture to provide a socket.io test client for the demo namespace."""

    async def _socketio_test_client_demo_resource_namespace(
        session_id: Optional[uuid.UUID] = None,
        query_parameters: Optional[dict] = None,
    ):
        """Factory function for creating a socket.io test client for the demo namespace."""
        client_config = [
            {
                "namespace": "/demo-resource",
                "events": [
                    "transfer",
                    "deleted",
                    "status",
                ],
            }
        ]

        """Creates an instance of SocketIOTestClient for the demo namespace."""
        return await socketio_test_client_class(
            client_config, session_id, query_parameters
        )

    return _socketio_test_client_demo_resource_namespace
