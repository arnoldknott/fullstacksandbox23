import uuid
import pytest
from socketio.exceptions import ConnectionError
from datetime import datetime
from routers.socketio.v1.demo_namespace import DemoNamespace, demo_namespace_router
from tests.utils import (
    session_id_user1_read_write_socketio,
    session_id_user2_read_write_socketio,
    token_admin_read_write_socketio,
    token_user1_read_write_socketio,
    token_admin_read,
    token_admin_write,
    token_user1_read,
    token_user1_write,
    token_admin_socketio,
    token_user1_read_socketio,
    token_user1_write_socketio,
    token_user1_socketio,
    token_user2_socketio,
    token_user2_read_socketio,
    token_user2_write_socketio,
    token_user2_read_write_socketio,
    token_admin_read_socketio,
    token_admin_write_socketio,
    token_user2_read,
    token_user2_write,
)


# @pytest.fixture(scope="module", autouse=True)
# async def setup_namespace_server(provide_namespace_server):
#     # Call setup function here
#     socket_io_server = await provide_namespace_server(
#         [DemoNamespace("/demo-namespace")]
#     )
#     # Yield to allow tests to run
#     yield socket_io_server
#     # Optionally, add teardown logic here if needed
#     # print("=== Shutting down socket.io server...")
#     # socket_io_server.sleep(5)
#     # print("=== Shutting down socket.io server... done")
#     await socket_io_server.shutdown()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    ["invalid_token_payload"],  # needed for module-level fixture setup_namespace_server
    indirect=True,
)
async def test_on_connect_invalid_token(mock_token_payload):
    """Test the on_connect event for socket.io without mocking decoding function."""
    # Should run into an uncaught exception from the decoding algorithm, depending on its implementation

    try:
        await demo_namespace_router.on_connect(
            sid="123",
            environ={},
            auth={"session-id": "fake-session-id"},
        )
        raise Exception("This should have failed due to invalid token.")
    except ConnectionRefusedError as err:
        assert str(err) == "Authorization failed."


# TBD: Uses more generic fixture - ready to delete:
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mock_token_payload",
#     [
#         token_admin_read_write_socketio,
#         token_user1_read_write_socketio,
#         token_user2_read_write_socketio,
#         token_admin_read_socketio,
#         token_user1_read_socketio,
#         token_user2_read_socketio,
#     ],
#     indirect=True,
# )
# async def test_connect_with_test_server_demo_namespace(
#     mock_token_payload,
#     socketio_test_client,
# ):
#     """Test the demo socket.io connect event."""
#     mocked_token_payload = mock_token_payload

#     responses = []
#     async for client in socketio_test_client(["/demo-namespace"]):

#         @client.event(namespace="/demo-namespace")
#         async def demo_message(data):
#             nonlocal responses
#             responses.append(data)

#         await client.connect_to_test_client()

#     assert len(responses) == 2
#     assert responses[0] == f"Welcome {mocked_token_payload['name']} to /demo-namespace."
#     assert "Your session ID is " in responses[1]


# TBD: rework to new client fixture with events:
@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [
        token_admin_read_write_socketio,
        token_user1_read_write_socketio,
        token_user2_read_write_socketio,
        token_admin_read_socketio,
        token_user1_read_socketio,
        token_user2_read_socketio,
    ],
    indirect=True,
)
async def test_connect_with_test_server_demo_namespace(
    mock_token_payload, socketio_client_for_demo_namespace
):
    """Test the demo socket.io connect event."""
    mocked_token_payload = mock_token_payload

    demo_messages = []
    async for client, response in socketio_client_for_demo_namespace():
        demo_messages = response["/demo-namespace"]["demo_message"]

    assert len(demo_messages) == 2
    assert (
        demo_messages[0]
        == f"Welcome {mocked_token_payload['name']} to /demo-namespace."
    )
    assert "Your session ID is " in demo_messages[1]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [
        token_admin_read,
        token_admin_write,
        token_admin_socketio,
        token_admin_write_socketio,
        token_user1_read,
        token_user1_write,
        token_user1_socketio,
        token_user1_write_socketio,
        token_user2_socketio,
        token_user2_read,
        token_user2_write,
        token_user2_write_socketio,
    ],
    indirect=True,
)
async def test_connect_with_test_server_demo_namespace_missing_scopes_fails(
    mock_token_payload, socketio_test_client, provide_namespace_server
):
    """Test the demo socket.io connect event."""
    mock_token_payload

    ## TBD: refactor back into module wide fixture, when multiple clients is merged with deep security:
    async for server in provide_namespace_server([DemoNamespace("/demo-namespace")]):

        async for client in socketio_test_client(["/demo-namespace"]):

            try:
                await client.connect_to_test_client()
                raise Exception("This should have failed due to invalid token.")
            except ConnectionError as err:
                assert str(err) == "One or more namespaces failed to connect"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_demo_message_with_test_server(
    mock_token_payload, socketio_client_for_demo_namespace
):
    """Test the demo socket.io message event."""
    mocked_token_payload = mock_token_payload

    demo_messages = []
    async for client, response in socketio_client_for_demo_namespace():

        await client.emit("demo_message", "Something", namespace="/demo-namespace")

        # Wait for the response to be set
        await client.sleep(1)

        demo_messages = response["/demo-namespace"]["demo_message"]

        await client.disconnect()

    assert len(demo_messages) == 3
    assert (
        demo_messages[0]
        == f"Welcome {mocked_token_payload['name']} to /demo-namespace."
    )
    assert "Your session ID is " in demo_messages[1]
    assert demo_messages[2] == f"{mocked_token_payload["name"]}: Something"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_sessions",
    [
        [token_user1_read_write_socketio, token_user2_read_write_socketio],
        [token_admin_read_write_socketio, token_user1_read_write_socketio],
        [token_user2_read_write_socketio, token_admin_read_write_socketio],
    ],
    indirect=True,
)
async def test_demo_message_with_test_server_and_multiple_users_connected(
    mock_sessions,
    socketio_test_client_with_multiple_mocked_users_on_server,
    # request,
):
    """Test the demo socket.io message event, with two users communicating."""
    # check that both users can connect  and one can send messages to the other
    # as well as disconnect events.
    # This is also testing the mocking of the sessions fixture

    demo_namespace_with_events = [
        {
            "name": "/demo-namespace",
            "events": ["demo_message"],
        }
    ]
    demo_messages_user1 = []
    demo_messages_user2 = []
    log_user1 = []
    log_user2 = []
    async for (
        connection_user1
    ) in socketio_test_client_with_multiple_mocked_users_on_server(
        demo_namespace_with_events,
        logs=log_user1,
    ):
        async for (
            connection_user2
        ) in socketio_test_client_with_multiple_mocked_users_on_server(
            demo_namespace_with_events,
            mocked_token_number=1,
            logs=log_user2,
        ):
            # Connect user 2 to the demo namespace
            client_user2 = connection_user2["client"]
            responses_user2 = connection_user2["responses"]
            logs_user2 = connection_user2["logs"]  # noqa F841

            # Wait for the response to be set
            await client_user2.sleep(1)

            demo_messages_user2 = responses_user2["/demo-namespace"]["demo_message"]

            # Emit a message from user 1
            client_user1 = connection_user1["client"]
            await client_user1.emit(
                "demo_message", "Hello from User 1", namespace="/demo-namespace"
            )
            await client_user2.sleep(1)
            await client_user2.disconnect()

        client_user1 = connection_user1["client"]
        responses_user1 = connection_user1["responses"]
        logs_user1 = connection_user1["logs"]  # noqa F841
        # Wait for the response to be set
        await client_user1.sleep(1)

        demo_messages_user1 = responses_user1["/demo-namespace"]["demo_message"]

        await client_user1.disconnect()

    # Asserting messages receivbed by user 1:
    assert len(demo_messages_user1) == 5
    assert (
        demo_messages_user1[0]
        == f"Welcome {mock_sessions['mocked_results'][0]['name']} to /demo-namespace."
    )
    assert "Your session ID is " in demo_messages_user1[1]
    assert (
        demo_messages_user1[2]
        == f"Welcome {mock_sessions['mocked_results'][1]['name']} to /demo-namespace."
    )
    assert (
        demo_messages_user1[3]
        == f"{mock_sessions['mocked_results'][0]['name']}: Hello from User 1"
    )
    assert (
        demo_messages_user1[4]
        == f"{mock_sessions['mocked_results'][1]['name']} has disconnected from /demo-namespace. Goodbye!"
    )

    # Asserting logs for user 1:
    assert len(log_user1) == 5
    for log in log_user1:
        assert log["event"] == "demo_message"

    assert log_user1[0]["data"] == (
        f"Welcome {mock_sessions['mocked_results'][0]['name']} to /demo-namespace."
    )
    assert log_user1[1]["data"].startswith("Your session ID is ")
    assert log_user1[2]["data"] == (
        f"Welcome {mock_sessions['mocked_results'][1]['name']} to /demo-namespace."
    )
    assert log_user1[3]["data"] == (
        f"{mock_sessions['mocked_results'][0]['name']}: Hello from User 1"
    )
    assert log_user1[4]["data"] == (
        f"{mock_sessions['mocked_results'][1]['name']} has disconnected from /demo-namespace. Goodbye!"
    )

    # Asserting messages received by user 2:
    assert len(demo_messages_user2) == 3
    assert (
        demo_messages_user2[0]
        == f"Welcome {mock_sessions['mocked_results'][1]['name']} to /demo-namespace."
    )
    assert demo_messages_user2[1].startswith("Your session ID is ")
    assert (
        demo_messages_user2[2]
        == f"{mock_sessions['mocked_results'][0]['name']}: Hello from User 1"
    )

    # Asserting logs for user 2:
    assert len(log_user2) == 3
    for log in log_user2:
        assert log["event"] == "demo_message"

    assert log_user2[0]["data"] == (
        f"Welcome {mock_sessions['mocked_results'][1]['name']} to /demo-namespace."
    )
    assert log_user2[1]["data"].startswith("Your session ID is ")
    assert log_user2[2]["data"] == (
        f"{mock_sessions['mocked_results'][0]['name']}: Hello from User 1"
    )

    # Asserting the mock sessions:
    assert mock_sessions["mock"].call_count == 2
    # User 1 token selected first:
    assert mock_sessions["mock"].call_args_list[0].args == ("0",)
    # User 2 token selected second:
    assert mock_sessions["mock"].call_args_list[1].args == ("1",)


# Define one reusable client per namespace as a fixture!
client_config = [
    {
        "namespace": "/demo-namespace",
        "events": ["demo_message"],
    }
]


# This is testing the test setup!
@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_write_socketio, session_id_user2_read_write_socketio]],
    indirect=True,
)
async def test_generic_test_client_and_server(
    session_id_selector,
    socketio_test_client_generic,
):
    """Test the generic client and generic server interaction."""

    session_id_default = session_id_selector()
    assert session_id_default == session_id_user1_read_write_socketio
    print("=== session_id_default ===")
    print(session_id_default, flush=True)
    session_id1 = session_id_selector(0)
    assert session_id1 == session_id_user1_read_write_socketio
    session_id2 = session_id_selector(1)
    assert session_id2 == session_id_user2_read_write_socketio

    logs1 = []
    responses1 = []
    # TBD: add one client for each namespace, hardcoding the client_config.
    async for connection1 in socketio_test_client_generic(
        client_config, 0, query_parameters={"request-access-data": "true"}, logs=logs1
    ):
        client1 = connection1["client"]
        responses1 = connection1["responses"]["/demo-namespace"]["demo_message"]
        logs1 = connection1["logs"]
        logs1.append(
            {
                "event": "demo_message",
                "timestamp": datetime.now(),
                # TBD: replace session_id_selector with mock_azure_token_in_redis(session_id_selector(0))["name"]
                # TBD: replace session_id_selector with mock_azure_token_in_redis[0].mocked_token["name"]
                # TBD: just use a fixture to select the token by session_id form sessions in tests.utils
                "data": f"{session_id_selector(0)}: sends message to server",
            }
        )
        # TBD: replace "User 1" with mock_azure_token_in_redis(session_id_selector(0))["name"]
        client1.emit("demo_message", "Hello from User 1", namespace="/demo-namespace")
        await client1.sleep(1)
        client1.disconnect()

    # Check the responses for user 1
    assert len(responses1) == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    ["invalid_token_payload"],  # needed for module-level fixture setup_namespace_server
    indirect=True,
)
async def test_demo_message_with_production_server_fails_without_token(
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo socket.io message event."""

    try:
        async for client in socketio_test_client(
            ["/demo-namespace"], "http://127.0.0.1:80"
        ):
            await client.connect_to_test_client()
            response = None

            @client.on("demo_message", namespace="/demo-namespace")
            async def handler(data):
                nonlocal response
                response = data

            await client.emit(
                "demo_message", "Hello, world!", namespace="/demo-namespace"
            )

            await client.sleep(1)

            raise Exception(
                "This should have failed due to missing authentication in on_connect."
            )

    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mock_token_payload",
#     [token_admin_read_write_socketio, token_user1_read_write_socketio],
#     indirect=True,
# )
# async def test_client_disconnects_from_demo_namespace_and_gets_goodbye_message(
#     mock_token_payload,
#     socketio_client_for_demo_namespace,
#     setup_namespace_server,
# ):
#     """Test the demo socket.io message event."""
#     mocked_token_payload = mock_token_payload

#     demo_messages = []
#     async for client, response in socketio_client_for_demo_namespace():

#         await client.emit("demo_message", "Something", namespace="/demo-namespace")

#         # Wait for the response to be set
#         await client.sleep(1)

#         await client.disconnect()
#         # server = setup_namespace_server
#         # await server.disconnect(client.sid)

#         await client.sleep(1)  # Give time for the disconnect to be processed

#         demo_messages = response["/demo-namespace"]["demo_message"]

#         print("=== demo_messages ===")
#         pprint(demo_messages)

#         # assert len(demo_messages) == 3
#         assert (
#             demo_messages[0]
#             == f"Welcome {mocked_token_payload['name']} to /demo-namespace."
#         )
#         assert "Your session ID is " in demo_messages[1]
#         assert demo_messages[2] == f"{mocked_token_payload['name']}: Something"

#         assert (
#             demo_messages[3]
#             == f"{mocked_token_payload['name']} has disconnected from /demo-namespace. Goodbye!"
#         )
#         assert demo_messages[4] == f"Your session with ID {client.sid} is ending."
#     # The disconnect message is sent after a delay, so we need to wait for it
