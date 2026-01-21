import asyncio
import uuid
from typing import List, Optional
from unittest.mock import patch

import pytest
import socketio
import uvicorn
from pydantic import BaseModel

from core.cache import redis_session_client
from core.security import CurrentAccessToken
from core.types import CurrentUserData
from routers.socketio.v1.demo_namespace import DemoNamespace
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from routers.socketio.v1.identities import (
    GroupNamespace,
    SubGroupNamespace,
    SubSubGroupNamespace,
    UeberGroupNamespace,
    UserNamespace,
)
from routers.socketio.v1.interactive_documentation import InteractiveDocumentation
from routers.socketio.v1.public_namespace import PublicNamespace
from routers.socketio.v1.quiz_namespace import (
    QuestionNamespace,
    MessageNamespace,
    NumericalNamespace,
)
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
            sio.register_namespace(PublicNamespace(server=sio))
            sio.register_namespace(DemoNamespace(server=sio))
            sio.register_namespace(DemoResourceNamespace(server=sio))
            sio.register_namespace(UserNamespace(server=sio))
            sio.register_namespace(UeberGroupNamespace(server=sio))
            sio.register_namespace(GroupNamespace(server=sio))
            sio.register_namespace(SubGroupNamespace(server=sio))
            sio.register_namespace(SubSubGroupNamespace(server=sio))
            sio.register_namespace(InteractiveDocumentation(server=sio))
            sio.register_namespace(QuestionNamespace(server=sio))
            sio.register_namespace(MessageNamespace(server=sio))
            sio.register_namespace(NumericalNamespace(server=sio))
            await asyncio.sleep(1)
            yield sio
            await server.shutdown()


# Setting up socketio client side for testing:


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
#         - "events" (list of strings), ["submit", "transferred", "deleted"].
#     session_id (uuid.UUID): The session ID to use for the connection.
#     query_parameters (dict): Query parameters to include in the connection.
#         e.g. {"request-access-data": "true", "parent-id": "123e4567-e89b-12d3-a456-426614174000"}


class ClientConfig(BaseModel):
    """Model to hold a namespace."""

    namespace: str
    events: List[str] = []


class SocketIOTestConnection:
    """Class to handle socket.io client connections and events."""

    def __init__(
        self,
        client_config: ClientConfig,
        session_id: Optional[uuid.UUID] = None,
    ):
        self.client_config = client_config
        self.session_id = session_id
        self.query_parameters = {}
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
        token_payload = None
        try:
            token_payload = [
                session["token_payload"]
                for session in sessions
                if session["session_id"] == self.session_id
            ][0]
        except IndexError:
            print(
                f"=== Session ID {self.session_id} not found in sessions for token payload. ===",
                flush=True,
            )
        return token_payload

    async def current_user(self) -> CurrentUserData:
        """Returns the current user for the user of this session."""
        current_user = None
        token = CurrentAccessToken(self.token_payload())
        current_user = await token.provides_current_user()
        return current_user


@pytest.fixture(scope="function")
def socketio_test_client(request, session_ids):
    """Fixture to provide a class-based socket.io test client."""

    async def _socketio_test_client(
        client_config: ClientConfig,
        session_id: Optional[uuid.UUID] = None,
    ):
        """Creates an instance of SocketIOTestClient."""
        if session_ids is None:
            connection = SocketIOTestConnection(
                client_config,
            )
            await connection.__aenter__()
        else:
            if not session_id:
                session_id = session_ids[0]

            connection = SocketIOTestConnection(
                client_config,
                session_id,
            )
            await connection.__aenter__()

        def cleanup():
            # Schedule disconnect for the event loop
            asyncio.get_event_loop().create_task(connection.__aexit__(None, None, None))

        request.addfinalizer(cleanup)

        return connection

    return _socketio_test_client


@pytest.fixture(scope="function")
def socketio_test_client_demo_namespace(socketio_test_client):
    """Fixture to provide a socket.io test client for the demo namespace."""

    async def _socketio_test_client_demo_namespace(
        session_id: Optional[uuid.UUID] = None,
    ):
        """Factory function for creating a socket.io test client for the demo namespace."""
        client_config = [
            {
                "namespace": "/demo-namespace",
                "events": ["demo_message"],
            }
        ]

        """Creates an instance of SocketIOTestClient for the demo namespace."""
        return await socketio_test_client(client_config, session_id)

    return _socketio_test_client_demo_namespace


@pytest.fixture(scope="function")
def socketio_test_client_demo_resource_namespace(socketio_test_client):
    """Fixture to provide a socket.io test client for the demo resource namespace."""

    async def _socketio_test_client_demo_resource_namespace(
        session_id: Optional[uuid.UUID] = None,
    ):
        """Factory function for creating a socket.io test client for the demo resource namespace."""
        client_config = [
            {
                "namespace": "/demo-resource",
                "events": [
                    "transferred",
                    "deleted",
                    "status",
                ],
            }
        ]

        """Creates an instance of SocketIOTestClient for the demo namespace."""
        return await socketio_test_client(client_config, session_id)

    return _socketio_test_client_demo_resource_namespace


@pytest.fixture(scope="function")
def socketio_test_client_user_namespace(socketio_test_client):
    """Fixture to provide a socket.io test client for the user namespace."""

    async def _socketio_test_client_user_namespace(
        session_id: Optional[uuid.UUID] = None,
    ):
        """Factory function for creating a socket.io test client for the user namespace."""
        client_config = [
            {
                "namespace": "/user",
                "events": [
                    "transferred",
                    "deleted",
                    "status",
                ],
            }
        ]

        """Creates an instance of SocketIOTestClient for the user namespace."""
        return await socketio_test_client(client_config, session_id)

    return _socketio_test_client_user_namespace


@pytest.fixture(scope="function")
def socketio_test_client_ueber_group_namespace(socketio_test_client):
    """Fixture to provide a socket.io test client for the ueber group namespace."""

    async def _socketio_test_client_ueber_group_namespace(
        session_id: Optional[uuid.UUID] = None,
    ):
        """Factory function for creating a socket.io test client for the ueber group namespace."""
        client_config = [
            {
                "namespace": "/ueber-group",
                "events": [
                    "transferred",
                    "deleted",
                    "status",
                ],
            }
        ]

        """Creates an instance of SocketIOTestClient for the demo namespace."""
        return await socketio_test_client(client_config, session_id)

    return _socketio_test_client_ueber_group_namespace
