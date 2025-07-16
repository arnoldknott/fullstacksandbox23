from datetime import datetime
from pprint import pprint

import pytest
import socketio
from socketio.exceptions import ConnectionError

from routers.socketio.v1.demo_namespace import demo_namespace_router
from tests.utils import (
    session_id_admin_read,
    session_id_admin_read_socketio,
    session_id_admin_read_write_socketio,
    session_id_admin_socketio,
    session_id_admin_write,
    session_id_admin_write_socketio,
    session_id_invalid_token1,
    session_id_invalid_token2,
    session_id_user1_read,
    session_id_user1_read_socketio,
    session_id_user1_read_write_socketio,
    session_id_user1_socketio,
    session_id_user1_write,
    session_id_user2_read,
    session_id_user2_read_socketio,
    session_id_user2_read_write_socketio,
    session_id_user2_socketio,
    session_id_user2_write,
    session_id_user2_write_socketio,
    token_admin_read_write_socketio,
    token_user1_read_write_socketio,
    token_user2_read_write_socketio,
)

# Default setup for client to use in all tests that use the demo namespace.
client_config_demo_namespace = [
    {
        "namespace": "/demo-namespace",
        "events": ["demo_message"],
    }
]


@pytest.mark.anyio
async def test_on_connect_to_production_on_server_side_fails_unpatched_server():
    """Test the on_connect event for socket.io without mocking decoding function."""
    # Should run into an uncaught exception from the decoding algorithm, depending on its implementation

    try:
        await demo_namespace_router.on_connect(
            sid="123",
            environ={},
            auth={"session-id": "fake-session-id"},
        )
        raise Exception("This should have failed due unpatched server.")
    except ConnectionRefusedError as err:
        assert str(err) == "Authorization failed."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [session_id_admin_read_write_socketio],
        [session_id_user1_read_write_socketio],
        [session_id_user2_read_write_socketio],
        [session_id_admin_read_socketio],
        [session_id_user1_read_socketio],
        [session_id_user2_read_socketio],
    ],
    indirect=True,
)
async def test_connect_to_demo_namespace(current_token_payload, socketio_test_client):
    """Test the demo socket.io connect event."""

    demo_messages = []
    async for connection in socketio_test_client(client_config_demo_namespace):
        demo_messages = connection["responses"]["/demo-namespace"]["demo_message"]

    assert len(demo_messages) == 2
    assert (
        demo_messages[0]
        == f"Welcome {current_token_payload()['name']} to /demo-namespace."
    )
    assert "Your session ID is " in demo_messages[1]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [session_id_admin_read],
        [session_id_admin_write],
        [session_id_admin_socketio],
        [session_id_admin_write_socketio],
        [session_id_user1_read],
        [session_id_user1_write],
        [session_id_user1_socketio],
        [session_id_admin_write_socketio],
        [session_id_user2_socketio],
        [session_id_user2_read],
        [session_id_user2_write],
        [session_id_user2_write_socketio],
        [session_id_invalid_token1],
        [session_id_invalid_token2],
    ],
    indirect=True,
)
async def test_connect_to_demo_namespace_missing_scopes_fails(
    socketio_test_client,
):
    """Test the demo socket.io connect event."""

    ## TBD: refactor back into module wide fixture, when multiple clients is merged with deep security:

    try:
        async for _client in socketio_test_client(client_config_demo_namespace):
            pass
        raise Exception("This should have failed due to invalid token.")
    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_send_demo_message(current_token_payload, socketio_test_client):
    """Test the demo socket.io message event."""

    demo_messages = []
    async for connection in socketio_test_client(client_config_demo_namespace):

        await connection["client"].emit(
            "demo_message", "Something", namespace="/demo-namespace"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        demo_messages = connection["responses"]["/demo-namespace"]["demo_message"]

        await connection["client"].disconnect()

    assert len(demo_messages) == 3
    assert (
        demo_messages[0]
        == f"Welcome {current_token_payload()['name']} to /demo-namespace."
    )
    assert "Your session ID is " in demo_messages[1]
    assert demo_messages[2] == f"{current_token_payload()['name']}: Something"


# This is testing the test setup!
@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_write_socketio, session_id_user2_read_write_socketio]],
    indirect=True,
)
async def test_demo_resource_chat_between_two_users(
    session_id_selector,
    socketio_test_client,
    current_token_payload,
):
    """Test the generic client and generic server interaction."""

    session_id_default = session_id_selector()
    assert session_id_default == session_id_user1_read_write_socketio
    session_id1 = session_id_selector(0)
    assert session_id1 == session_id_user1_read_write_socketio
    session_id2 = session_id_selector(1)
    assert session_id2 == session_id_user2_read_write_socketio

    token_payload_default = current_token_payload()
    assert token_payload_default == token_user1_read_write_socketio
    token_payload1 = current_token_payload(0)
    assert token_payload1 == token_user1_read_write_socketio
    token_payload2 = current_token_payload(1)
    assert token_payload2 == token_user2_read_write_socketio

    logs1 = []
    logs2 = []
    responses1 = []
    responses2 = []
    # TBD: add one client for each namespace, hardcoding the client_config.
    async for connection1 in socketio_test_client(
        client_config_demo_namespace,
        0,
        query_parameters={"request-access-data": "true"},
        logs=logs1,
    ):
        client1 = connection1["client"]
        responses1 = connection1["responses"]["/demo-namespace"]["demo_message"]
        logs1 = connection1["logs"]
        async for connection2 in socketio_test_client(
            client_config_demo_namespace,
            1,
            query_parameters={"request-access-data": "true"},
            logs=logs2,
        ):
            client2 = connection2["client"]
            responses2 = connection2["responses"]["/demo-namespace"]["demo_message"]
            logs2 = connection2["logs"]

            # Wait for the response to be set
            await client2.sleep(1)
            logs1.append(
                {
                    "event": "demo_message",
                    "timestamp": datetime.now(),
                    "data": f"{current_token_payload(0)['name']}: sends message to server.",
                }
            )
            await client1.emit(
                "demo_message",
                f"Hello from {current_token_payload(0)['name']}",
                namespace="/demo-namespace",
            )
            await client2.sleep(1)
            await client2.disconnect()

        await client1.sleep(1)
        await client1.disconnect()

    # Asserting responses for user 1
    assert len(responses1) == 5

    assert (
        responses1[0]
        == f"Welcome {current_token_payload()['name']} to /demo-namespace."
    )
    assert "Your session ID is " in responses1[1]
    assert (
        responses1[2]
        == f"Welcome {current_token_payload(1)['name']} to /demo-namespace."
    )
    assert (
        responses1[3]
        == f"{current_token_payload(0)['name']}: Hello from {current_token_payload(0)['name']}"
    )
    assert (
        responses1[4]
        == f"{current_token_payload(1)['name']} has disconnected from /demo-namespace. Goodbye!"
    )

    # Asserting logs for user 1:
    assert len(logs1) == 6
    for log in logs1:
        assert log["event"] == "demo_message"

    assert logs1[0]["data"] == (
        f"Welcome {current_token_payload()['name']} to /demo-namespace."
    )
    assert logs1[1]["data"].startswith("Your session ID is ")
    assert logs1[2]["data"] == (
        f"Welcome {current_token_payload(1)['name']} to /demo-namespace."
    )
    assert logs1[3]["data"] == (
        f"{current_token_payload(0)['name']}: sends message to server."
    )
    assert logs1[4]["data"] == (
        f"{current_token_payload(0)['name']}: Hello from {current_token_payload(0)['name']}"
    )
    assert logs1[5]["data"] == (
        f"{current_token_payload(1)['name']} has disconnected from /demo-namespace. Goodbye!"
    )

    # Asserting messages received by user 2:
    assert len(responses2) == 3
    assert (
        responses2[0]
        == f"Welcome {current_token_payload(1)['name']} to /demo-namespace."
    )
    assert responses2[1].startswith("Your session ID is ")
    assert (
        responses2[2]
        == f"{current_token_payload(0)['name']}: Hello from {current_token_payload(0)['name']}"
    )

    # Asserting logs for user 2:
    assert len(logs2) == 3
    for log in logs2:
        assert log["event"] == "demo_message"

    assert logs2[0]["data"] == (
        f"Welcome {current_token_payload(1)['name']} to /demo-namespace."
    )
    assert logs2[1]["data"].startswith("Your session ID is ")
    assert logs2[2]["data"] == (
        f"{current_token_payload(0)['name']}: Hello from {current_token_payload(0)['name']}"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_socketio]],
    indirect=True,
)
async def test_demo_message_with_production_server_fails_authorization(
    session_id_selector,
):
    """Test the demo socket.io message event."""

    try:
        client = socketio.AsyncClient(logger=True, engineio_logger=True)

        await client.connect(
            "http://127.0.0.1:80",
            socketio_path="socketio/v1",
            namespaces=["/demo-namespace"],
            auth={"session-id": str(session_id_selector(0))},
        )

        response = None

        @client.on("demo_message", namespace="/demo-namespace")
        async def handler(data):
            nonlocal response
            response = data

        await client.emit("demo_message", "Hello, world!", namespace="/demo-namespace")

        await client.sleep(1)

        raise Exception(
            "This should have failed due to missing authentication in on_connect."
        )

    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "session_id_selector",
#     [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
#     indirect=True,
# )
# async def test_client_disconnects_from_demo_namespace_and_gets_goodbye_message(
#     socketio_test_client,
# ):
#     """Test the demo socket.io message event."""

#     demo_messages = []
#     async for connection in socketio_test_client(client_config_demo_namespace):

#         await connection["client"].emit("demo_message", "Something", namespace="/demo-namespace")

#         # Wait for the response to be set
#         await connection["client"].sleep(1)

#         await connection["client"].disconnect()
#         # server = setup_namespace_server
#         # await server.disconnect(client.sid)

#         await connection["client"].sleep(1)  # Give time for the disconnect to be processed

#         demo_messages = response["/demo-namespace"]["demo_message"]

#         print("=== demo_messages ===")
#         pprint(demo_messages)

#         # assert len(demo_messages) == 3
#         assert (
#             demo_messages[0]
#             == f"Welcome {mocked_token_payload['name']} to /demo-namespace."
#         )
#         assert "Your session ID is " in demo_messages[1]
#         assert demo_messages[2] == f"{current_token_payload()['name']}: Something"

#         assert (
#             demo_messages[3]
#             == f"{current_token_payload()['name']} has disconnected from /demo-namespace. Goodbye!"
#         )
#         assert demo_messages[4] == f"Your session with ID {client.sid} is ending."
#     # The disconnect message is sent after a delay, so we need to wait for it


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_use_class_based_test_client(
    session_ids, socketio_test_client_demo_namespace, current_user_from_azure_token
):
    """Test the class-based socket.io test client."""

    # Initializing and connecting admin:
    # # TBD: potentially delete logging system, as teh responses are now growing along the way.
    # logs_admin = [
    #     {
    #         "event": "",
    #         "timestamp": datetime.now(),
    #         "data": "Connecting to demo namespace for first user.",
    #     },
    # ]
    query_admin = {"param1": "value1", "param2": "value2"}
    connection_admin = await socketio_test_client_demo_namespace(
        session_ids[0], query_parameters=query_admin
    )

    await connection_admin.client.sleep(0.1)
    assert connection_admin.session_id == session_ids[0]
    assert connection_admin.query_parameters == query_admin
    assert connection_admin.token_payload() == token_admin_read_write_socketio
    assert await connection_admin.current_user() == await current_user_from_azure_token(
        token_admin_read_write_socketio
    )
    assert len(connection_admin.responses()) == 2
    assert (
        connection_admin.responses()[0]
        == f"Welcome {token_admin_read_write_socketio['name']} to /demo-namespace."
    )
    assert "Your session ID is " in connection_admin.responses()[1]

    # Initializing and connecting user1:
    # # TBD: potentially delete logging system, as teh responses are now growing along the way.
    # logs_user1 = [
    #     {
    #         "event": "",
    #         "timestamp": datetime.now(),
    #         "data": "Connecting to demo namespace for second user.",
    #     },
    # ]
    query_user1 = {"param1": "Avalue", "paramB": "some-other-value"}
    connection_user1 = await socketio_test_client_demo_namespace(
        session_ids[1],
        query_parameters=query_user1,
        # logs=logs_user1,
    )

    await connection_admin.client.sleep(0.1)

    assert connection_user1.session_id == session_ids[1]
    assert connection_user1.query_parameters == query_user1
    assert connection_user1.token_payload() == token_user1_read_write_socketio
    assert await connection_user1.current_user() == await current_user_from_azure_token(
        token_user1_read_write_socketio
    )

    assert len(connection_admin.responses()) == 3
    assert connection_admin.responses()[2] == (
        f"Welcome {token_user1_read_write_socketio['name']} to /demo-namespace."
    )

    assert len(connection_user1.responses()) == 2
    assert (
        connection_user1.responses()[0]
        == f"Welcome {token_user1_read_write_socketio['name']} to /demo-namespace."
    )
    assert "Your session ID is " in connection_user1.responses()[1]

    # print("=== client - logs_admin ===")
    # pprint(connection_admin.logs)
    # assert len(connection_admin.logs) == 5
    # assert connection_admin.logs == logs_admin
    # assert connection_user1.logs == logs_user1

    # print("=== test_use_class_based_test_client - client.current_user ===")
    # print(await connection.current_user, flush=True)

    # logs_admin.append(
    #     {
    #         "event": "demo_message",
    #         "timestamp": datetime.now(),
    #         "data": "Before emitting demo message.",
    #     }
    # )

    # Admin sends a message in chat to everyone with name of user1:
    user1_name = connection_user1.token_payload()["name"]
    await connection_admin.client.emit(
        "demo_message", f"Hello, {user1_name}!", namespace="/demo-namespace"
    )

    await connection_admin.client.sleep(0.1)
    assert len(connection_admin.responses()) == 4

    assert connection_admin.responses()[3] == (
        f"{token_admin_read_write_socketio['name']}: Hello, {user1_name}!"
    )
    assert len(connection_user1.responses()) == 3
    assert connection_user1.responses()[2] == (
        f"{token_admin_read_write_socketio['name']}: Hello, {user1_name}!"
    )

    # logs_admin.append(
    #     {
    #         "event": "demo_message",
    #         "timestamp": datetime.now(),
    #         "data": "After emitting demo message.",
    #     }
    # )

    await connection_user1.client.sleep(0.1)
    admin_name = connection_admin.token_payload()["name"]
    await connection_user1.client.emit(
        "demo_message",
        f"Hi {admin_name}, good to see you, How are you!?",
        namespace="/demo-namespace",
    )

    await connection_user1.client.sleep(0.1)
    assert len(connection_admin.responses()) == 5
    assert connection_admin.responses()[4] == (
        f"{token_user1_read_write_socketio['name']}: Hi {admin_name}, good to see you, How are you!?"
    )
    assert len(connection_user1.responses()) == 4
    assert connection_user1.responses()[3] == (
        f"{token_user1_read_write_socketio['name']}: Hi {admin_name}, good to see you, How are you!?"
    )

    # await connection_admin.client.sleep(0.1)
    await connection_user1.client.disconnect()

    await connection_admin.client.sleep(0.1)
    assert len(connection_admin.responses()) == 6
    assert connection_admin.responses()[5] == (
        f"{token_user1_read_write_socketio['name']} has disconnected from /demo-namespace. Goodbye!"
    )
