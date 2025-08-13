import pytest

from tests.utils import (
    session_id_admin_read_write_socketio,
    session_id_user1_read_write_socketio,
    session_id_user2_read_write_socketio,
    token_user1_read_write_socketio,
    many_test_azure_users,
    many_test_groups,
)

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented


# User Namespace Tests:
# ✔︎ Admin connects, creates, reads, updates, and deletes user
# ✔︎ Admin and users read Me
# ✔︎ Admin and users update Me
# ✔︎ User fails to create user
# ✔︎ User succeeds to update user, where user is owner
# ✔︎ User fails to update user, due to missing ownership
# ✔︎ User fails to delete user, despite being owner


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids", [[session_id_admin_read_write_socketio]], indirect=True
)
async def test_admin_access_user_connect_create_read_update_delete(
    socketio_test_client_user_namespace,
):
    """Test admin access to connect, create, update, and delete events in the user namespace."""
    connection = await socketio_test_client_user_namespace()
    # Connect to the user namespace:
    await connection.connect()
    await connection.client.sleep(0.5)
    assert len(connection.responses("transferred")) == 0

    # Create user:
    test_user = many_test_azure_users[1]
    await connection.client.emit("submit", {"payload": test_user}, namespace="/user")
    await connection.client.sleep(0.5)
    # Check if the user was created successfully:
    assert connection.responses("status")[0]["success"] == "created"
    assert "id" in connection.responses("status")[0]
    created_user_id = connection.responses("status")[0]["id"]
    # Admin automatically gets a shared notification:
    assert connection.responses("status")[1]["success"] == "shared"
    assert connection.responses("status")[1]["id"] == created_user_id
    assert len(connection.responses("transferred")) == 0

    # Read:
    await connection.client.emit("read", created_user_id, namespace="/user")
    await connection.client.sleep(1.3)
    assert len(connection.responses("transferred")) == 1
    assert connection.responses("transferred")[0]["id"] == created_user_id
    assert (
        connection.responses("transferred")[0]["azure_user_id"]
        == test_user["azure_user_id"]
    )
    assert (
        connection.responses("transferred")[0]["azure_tenant_id"]
        == test_user["azure_tenant_id"]
    )

    # Update user:
    updated_user = {
        **test_user,
        "id": created_user_id,
        "is_active": False,
    }
    await connection.client.emit("submit", {"payload": updated_user}, namespace="/user")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[2]["success"] == "updated"
    assert connection.responses("status")[2]["id"] == created_user_id
    assert len(connection.responses("transferred")) == 2
    assert connection.responses("transferred")[1]["id"] == created_user_id
    assert connection.responses("transferred")[1]["is_active"] is False

    # Delete user:
    await connection.client.emit("delete", created_user_id, namespace="/user")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[3]["success"] == "deleted"
    assert connection.responses("status")[3]["id"] == created_user_id
    assert connection.responses("deleted")[0] == created_user_id

    # Read deleted user fails:
    await connection.client.emit("read", created_user_id, namespace="/user")
    await connection.client.sleep(1)
    assert len(connection.responses("transferred")) == 2
    assert connection.responses("status")[4]["success"] == "deleted"
    assert connection.responses("status")[4]["id"] == created_user_id
    assert (
        connection.responses("status")[5]["error"]
        == f"Resource {created_user_id} not found."
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_admin_read_write_socketio],
        [session_id_user1_read_write_socketio],
        [session_id_user2_read_write_socketio],
    ],
    indirect=True,
)
async def test_read_me(
    socketio_test_client_user_namespace,
    add_many_azure_test_users,
):
    """Test admin access to connect, create, update, and delete events in the user namespace."""
    connection = await socketio_test_client_user_namespace()
    current_user = await connection.current_user()
    await add_many_azure_test_users()
    # Connect to the user namespace:
    await connection.connect()
    await connection.client.sleep(0.5)
    assert len(connection.responses("transferred")) == 0

    await connection.client.emit("read_me", namespace="/user")
    await connection.client.sleep(1.5)
    # it's only the admin, that is so slow (users get response within 0.3 seconds!)
    assert len(connection.responses("transferred")) == 1
    assert connection.responses("transferred")[0]["id"] == str(current_user.user_id)
    assert (
        connection.responses("transferred")[0]["azure_token_roles"]
        == current_user.azure_token_roles
    )
    assert (
        connection.responses("transferred")[0]["azure_token_groups"]
        == current_user.azure_token_groups
    )
    assert connection.responses("transferred")[0]["user_profile"]["contrast"] == 0.0
    assert (
        connection.responses("transferred")[0]["user_profile"]["theme_color"]
        == "#353c6e"
    )
    assert (
        connection.responses("transferred")[0]["user_profile"]["theme_variant"]
        == "Tonal Spot"
    )
    assert (
        connection.responses("transferred")[0]["user_account"]["is_publicAIuser"]
        is False
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_admin_read_write_socketio],
        [session_id_user1_read_write_socketio],
        [session_id_user2_read_write_socketio],
    ],
    indirect=True,
)
async def test_update_me(
    socketio_test_client_user_namespace,
    add_many_azure_test_users,
):
    """Test admin access to connect, create, update, and delete events in the user namespace."""
    connection = await socketio_test_client_user_namespace()
    current_user = await connection.current_user()
    await add_many_azure_test_users()
    # Connect to the user namespace:
    await connection.connect()
    await connection.client.sleep(0.5)
    assert len(connection.responses("transferred")) == 0

    await connection.client.emit("read_me", namespace="/user")
    await connection.client.sleep(1.5)
    assert len(connection.responses("transferred")) == 1
    me = connection.responses("transferred")[0]

    # Update user profile:
    updated_me = {
        **me,
        "user_profile": {
            "contrast": 0.4,
            "theme_color": "#FF5733",
            "theme_variant": "Vibrant",
        },
        "user_account": {
            "is_publicAIuser": True,
        },
    }
    await connection.client.emit("update_me", updated_me, namespace="/user")
    await connection.client.sleep(2.5)
    # it's only the admin, that is so slow (users get response within 0.3 seconds!)
    assert len(connection.responses("transferred")) == 2
    assert connection.responses("transferred")[1]["id"] == str(current_user.user_id)
    assert (
        connection.responses("transferred")[1]["azure_token_roles"]
        == current_user.azure_token_roles
    )
    assert (
        connection.responses("transferred")[1]["azure_token_groups"]
        == current_user.azure_token_groups
    )
    assert connection.responses("transferred")[1]["user_profile"]["contrast"] == 0.4
    assert (
        connection.responses("transferred")[1]["user_profile"]["theme_color"]
        == "#FF5733"
    )
    assert (
        connection.responses("transferred")[1]["user_profile"]["theme_variant"]
        == "Vibrant"
    )
    assert (
        connection.responses("transferred")[1]["user_account"]["is_publicAIuser"]
        is True
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids", [[session_id_user1_read_write_socketio]], indirect=True
)
async def test_user_creates_user_fails(
    socketio_test_client_user_namespace,
):
    """Test user access to connect, create, update, and delete events in the user namespace."""
    connection = await socketio_test_client_user_namespace()
    # Connect to the user namespace:
    await connection.connect()

    # Create user:
    test_user = {}
    await connection.client.emit("submit", {"payload": test_user}, namespace="/user")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[0]["error"] == "401: Invalid token."
    assert len(connection.responses("status")) == 1
    assert len(connection.responses("transferred")) == 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_updates_user_where_being_owner(
    socketio_test_client_user_namespace,
    session_ids,
    add_one_test_access_policy,
):
    """Test user access to connect, create, update, and delete events in the user namespace."""
    connection_admin = await socketio_test_client_user_namespace()
    connection_user = await socketio_test_client_user_namespace(session_ids[1])
    current_user = await connection_user.current_user()
    # Connect to the user namespace:
    await connection_admin.connect()
    await connection_user.connect()
    # await connection_user.client.sleep(0.3)

    # Admin creates a user:
    test_user = many_test_azure_users[1]
    await connection_admin.client.emit(
        "submit", {"payload": test_user}, namespace="/user"
    )
    await connection_admin.client.sleep(0.3)
    assert connection_admin.responses("status")[0]["success"] == "created"
    created_user_id = connection_admin.responses("status")[0]["id"]

    # Admin shares the created user:
    await add_one_test_access_policy(
        {
            "resource_id": str(created_user_id),
            "identity_id": str(current_user.user_id),
            "action": "own",
        }
    )

    # User updates user:
    updated_test_user = {
        "id": str(created_user_id),
        "is_active": "False",
    }
    await connection_user.client.emit(
        "submit", {"payload": updated_test_user}, namespace="/user"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["success"] == "updated"
    assert connection_user.responses("status")[0]["id"] == updated_test_user["id"]
    assert len(connection_user.responses("transferred")) == 1
    assert connection_user.responses("transferred")[0]["id"] == updated_test_user["id"]
    assert connection_user.responses("transferred")[0]["is_active"] is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_updates_user_fails_due_to_missing_ownership(
    socketio_test_client_user_namespace,
    session_ids,
):
    """Test user access to connect, create, update, and delete events in the user namespace."""
    connection_admin = await socketio_test_client_user_namespace()
    connection_user = await socketio_test_client_user_namespace(session_ids[1])
    # Connect to the user namespace:
    await connection_admin.connect()
    await connection_user.connect()

    # Admin creates a user:
    test_user = many_test_azure_users[1]
    await connection_admin.client.emit(
        "submit", {"payload": test_user}, namespace="/user"
    )
    await connection_admin.client.sleep(0.3)
    assert connection_admin.responses("status")[0]["success"] == "created"
    created_user_id = connection_admin.responses("status")[0]["id"]

    # User updates user:
    updated_test_user = {
        "id": str(created_user_id),
        "is_active": "False",
    }
    await connection_user.client.emit(
        "submit", {"payload": updated_test_user}, namespace="/user"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["error"] == "404: User not updated."
    assert connection_user.responses("transferred") == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_deletes_user_where_being_owner_fails(
    socketio_test_client_user_namespace,
    add_many_azure_test_users,
    session_ids,
    add_one_test_access_policy,
):
    """Test user access to connect, create, update, and delete events in the user namespace."""
    connection_admin = await socketio_test_client_user_namespace()
    connection_user = await socketio_test_client_user_namespace(session_ids[1])
    many_test_users = await add_many_azure_test_users()
    current_user = await connection_user.current_user()
    await add_one_test_access_policy(
        {
            "resource_id": str(many_test_users[2].id),
            "identity_id": str(current_user.user_id),
            "action": "own",
        }
    )
    # Connect to the user namespace:
    await connection_admin.connect()
    await connection_user.connect()

    # User deletes user:
    await connection_user.client.emit(
        "delete", str(many_test_users[1].id), namespace="/user"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["error"] == "401: Invalid token."
    assert connection_user.responses("transferred") == []


# Ueber Group Namespace Tests:
# ✔︎ Admin connects, creates, updates, and deletes an ueber group
# ✔︎ Admin gets all existing ueber groups on connnect
# ✔︎ User fails to create ueber group
# ✔︎ User succeeds to update ueber group, where user is owner
# ✔︎ User fails to update ueber group, due to missing ownership
# ✔︎ User fails to delete ueber group, despite being owner


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids", [[session_id_admin_read_write_socketio]], indirect=True
)
async def test_admin_access_ueber_group_connect_create_update_delete(
    socketio_test_client_ueber_group_namespace,
):
    """Test admin access to connect, create, update, and delete events in the ueber group namespace."""
    connection = await socketio_test_client_ueber_group_namespace()
    # Connect to the ueber group namespace:
    await connection.connect()
    assert connection.responses("transferred") == []

    # Create ueber group:
    test_group = {
        "name": "Dummy Ueber Group",
        "description": "A dummy group added via SocketIO.",
    }
    await connection.client.emit(
        "submit", {"payload": test_group}, namespace="/ueber-group"
    )
    await connection.client.sleep(0.3)
    assert connection.responses("status")[0]["success"] == "created"
    assert "id" in connection.responses("status")[0]
    created_uber_group_id = connection.responses("status")[0]["id"]
    # Admin automatically gets a shared notification:
    assert connection.responses("status")[1]["success"] == "shared"
    assert connection.responses("status")[1]["id"] == created_uber_group_id
    assert len(connection.responses("transferred")) == 0

    # Update ueber group:
    updated_group = {
        **test_group,
        "description": "Updated description",
        "id": created_uber_group_id,
    }
    await connection.client.emit(
        "submit", {"payload": updated_group}, namespace="/ueber-group"
    )
    await connection.client.sleep(0.3)
    assert connection.responses("status")[2]["success"] == "updated"
    assert connection.responses("status")[2]["id"] == created_uber_group_id
    assert len(connection.responses("transferred")) == 1
    assert connection.responses("transferred")[0]["id"] == created_uber_group_id
    assert (
        connection.responses("transferred")[0]["description"] == "Updated description"
    )
    assert connection.responses("transferred")[0]["name"] == "Dummy Ueber Group"

    # Delete ueber group event:
    await connection.client.emit(
        "delete", created_uber_group_id, namespace="/ueber-group"
    )
    await connection.client.sleep(0.3)
    assert connection.responses("status")[3]["success"] == "deleted"
    assert connection.responses("status")[3]["id"] == created_uber_group_id
    assert connection.responses("deleted")[0] == created_uber_group_id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids", [[session_id_admin_read_write_socketio]], indirect=True
)
async def test_admin_gets_all_existing_ueber_groups_on_connect(
    socketio_test_client_ueber_group_namespace,
    add_many_test_ueber_groups,
):
    """Test admin access to connect, create, update, and delete events in the ueber group namespace."""
    connection = await socketio_test_client_ueber_group_namespace()
    await add_many_test_ueber_groups()
    # Connect to the ueber group namespace:
    await connection.connect()
    assert len(connection.responses("transferred")) == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids", [[session_id_user1_read_write_socketio]], indirect=True
)
async def test_user_creates_ueber_group_fails(
    socketio_test_client_ueber_group_namespace,
):
    """Test user access to connect, create, update, and delete events in the ueber group namespace."""
    connection = await socketio_test_client_ueber_group_namespace()
    # Connect to the ueber group namespace:
    await connection.connect()
    assert connection.responses("transferred") == []

    # Create ueber group:
    test_group = {
        "name": "Dummy Ueber Group",
        "description": "A dummy group added via SocketIO.",
    }
    await connection.client.emit(
        "submit", {"payload": test_group}, namespace="/ueber-group"
    )
    await connection.client.sleep(0.3)
    assert connection.responses("status")[0]["error"] == "401: Invalid token."
    assert len(connection.responses("status")) == 1
    assert len(connection.responses("transferred")) == 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_updates_ueber_group_where_being_owner(
    socketio_test_client_ueber_group_namespace,
    add_many_test_ueber_groups,
    session_ids,
    add_one_test_access_policy,
):
    """Test user access to connect, create, update, and delete events in the ueber group namespace."""
    connection_admin = await socketio_test_client_ueber_group_namespace()
    connection_user = await socketio_test_client_ueber_group_namespace(session_ids[1])
    many_test_ueber_groups = await add_many_test_ueber_groups()
    current_user = await connection_user.current_user()
    await add_one_test_access_policy(
        {
            "resource_id": str(many_test_ueber_groups[1].id),
            "identity_id": str(current_user.user_id),
            "action": "own",
        }
    )
    # Connect to the ueber group namespace:
    await connection_admin.connect()
    await connection_user.connect()

    assert len(connection_admin.responses("transferred")) == 3
    assert len(connection_user.responses("transferred")) == 1

    # User updates ueber group:
    updated_test_group = {
        "id": str(many_test_ueber_groups[1].id),
        "name": "Updated Dummy Ueber Group",
        "description": "An updated dummy group added via SocketIO.",
    }
    await connection_user.client.emit(
        "submit", {"payload": updated_test_group}, namespace="/ueber-group"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["success"] == "updated"
    assert connection_user.responses("status")[0]["id"] == updated_test_group["id"]
    assert len(connection_user.responses("transferred")) == 2
    assert connection_user.responses("transferred")[1]["id"] == updated_test_group["id"]
    assert (
        connection_user.responses("transferred")[1]["description"]
        == updated_test_group["description"]
    )
    assert (
        connection_user.responses("transferred")[1]["name"]
        == updated_test_group["name"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_updates_ueber_group_fails_due_to_missing_ownership(
    socketio_test_client_ueber_group_namespace,
    add_many_test_ueber_groups,
    session_ids,
):
    """Test user access to connect, create, update, and delete events in the ueber group namespace."""
    connection_admin = await socketio_test_client_ueber_group_namespace()
    connection_user = await socketio_test_client_ueber_group_namespace(session_ids[1])
    many_test_ueber_groups = await add_many_test_ueber_groups()
    # Connect to the ueber group namespace:
    await connection_admin.connect()
    await connection_user.connect()

    assert len(connection_admin.responses("transferred")) == 3
    assert connection_user.responses("transferred") == []

    # User updates ueber group:
    updated_test_group = {
        "id": str(many_test_ueber_groups[1].id),
        "name": "Updated Dummy Ueber Group",
        "description": "An updated dummy group added via SocketIO.",
    }
    await connection_user.client.emit(
        "submit", {"payload": updated_test_group}, namespace="/ueber-group"
    )
    await connection_user.client.sleep(0.3)
    assert (
        connection_user.responses("status")[0]["error"]
        == "404: UeberGroup not updated."
    )
    assert connection_user.responses("transferred") == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_deletes_ueber_group_where_being_owner_fails(
    socketio_test_client_ueber_group_namespace,
    add_many_test_ueber_groups,
    session_ids,
    add_one_test_access_policy,
):
    """Test user access to connect, create, update, and delete events in the ueber group namespace."""
    connection_admin = await socketio_test_client_ueber_group_namespace()
    connection_user = await socketio_test_client_ueber_group_namespace(session_ids[1])
    many_test_ueber_groups = await add_many_test_ueber_groups()
    current_user = await connection_user.current_user()
    await add_one_test_access_policy(
        {
            "resource_id": str(many_test_ueber_groups[1].id),
            "identity_id": str(current_user.user_id),
            "action": "own",
        }
    )
    # Connect to the ueber group namespace:
    await connection_admin.connect()
    await connection_user.connect()

    assert len(connection_admin.responses("transferred")) == 3
    assert len(connection_user.responses("transferred")) == 1

    # User deletes ueber group:
    await connection_user.client.emit(
        "delete", str(many_test_ueber_groups[1].id), namespace="/ueber-group"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["error"] == "401: Invalid token."
    assert len(connection_user.responses("transferred")) == 1


# Group Namespace Tests:
# ✔︎ user connects, creates, updates, and deletes a group
# ✔︎ get all groups on connect

group_client_config = [
    {
        "namespace": "/group",
        "events": [
            "transferred",
            "deleted",
            "status",
        ],
    }
]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_connect_create_read_update_delete_group(
    socketio_test_client,
):
    """Test admin access to connect, create, update, and delete events in the group namespace."""

    connection = await socketio_test_client(group_client_config)
    # Connect to the user namespace:
    await connection.connect()
    await connection.client.sleep(0.5)
    assert len(connection.responses("transferred")) == 0

    # Create group:
    test_group = many_test_groups[1]
    await connection.client.emit("submit", {"payload": test_group}, namespace="/group")
    await connection.client.sleep(0.5)
    # Check if the user was created successfully:
    assert connection.responses("status")[0]["success"] == "created"
    assert "id" in connection.responses("status")[0]
    created_group_id = connection.responses("status")[0]["id"]
    assert len(connection.responses("transferred")) == 0

    # Read:
    await connection.client.emit("read", created_group_id, namespace="/group")
    await connection.client.sleep(0.3)
    assert len(connection.responses("transferred")) == 1
    assert connection.responses("transferred")[0]["id"] == created_group_id
    assert connection.responses("transferred")[0]["name"] == test_group["name"]
    assert (
        connection.responses("transferred")[0]["description"]
        == test_group["description"]
    )

    # Update group:
    updated_group = {
        **test_group,
        "id": created_group_id,
        "description": "Updated description",
    }
    await connection.client.emit(
        "submit", {"payload": updated_group}, namespace="/group"
    )
    await connection.client.sleep(0.3)
    assert connection.responses("status")[1]["success"] == "updated"
    assert connection.responses("status")[1]["id"] == created_group_id
    assert len(connection.responses("transferred")) == 2
    assert connection.responses("transferred")[1]["id"] == created_group_id
    assert connection.responses("transferred")[1]["name"] == test_group["name"]
    assert (
        connection.responses("transferred")[1]["description"] == "Updated description"
    )

    # Delete group:
    await connection.client.emit("delete", created_group_id, namespace="/group")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[2]["success"] == "deleted"
    assert connection.responses("status")[2]["id"] == created_group_id
    assert connection.responses("deleted")[0] == created_group_id

    # Read deleted group fails:
    await connection.client.emit("read", created_group_id, namespace="/group")
    await connection.client.sleep(1)
    assert len(connection.responses("transferred")) == 2
    assert connection.responses("status")[3]["success"] == "deleted"
    assert connection.responses("status")[3]["id"] == created_group_id
    assert (
        connection.responses("status")[4]["error"]
        == f"Resource {created_group_id} not found."
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_get_all_existing_groups_on_connect(
    socketio_test_client,
    add_many_test_groups,
):
    """Test at connect get all existing groups with access."""
    connection = await socketio_test_client(group_client_config)
    added_test_groups = await add_many_test_groups(connection.token_payload())
    resource_ids = [
        str(added_test_groups[0].id),
        str(added_test_groups[2].id),
        str(added_test_groups[3].id),
    ]
    # Connect to the group namespace:
    await connection.connect(query_parameters={"resource-ids": ",".join(resource_ids)})
    assert len(connection.responses("transferred")) == 3
    assert connection.responses("transferred")[0]["id"] == str(resource_ids[0])
    assert connection.responses("transferred")[1]["id"] == str(resource_ids[1])
    assert connection.responses("transferred")[2]["id"] == str(resource_ids[2])


# Sub Group Namespace Tests:
# ✔︎ user connects, creates, updates, and deletes a group

sub_group_client_config = [
    {
        "namespace": "/sub-group",
        "events": [
            "transferred",
            "deleted",
            "status",
        ],
    }
]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio, session_id_user2_read_write_socketio]],
    indirect=True,
)
# Required for add_one_parent in add_many_test_sub_groups fixture:
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_connect_create_read_update_delete_sub_group(
    socketio_test_client, add_many_test_sub_groups, add_many_test_groups, session_ids
):
    """Test admin access to connect, create, update, and delete events in the sub group namespace."""
    connection_user1 = await socketio_test_client(sub_group_client_config)
    connection_user2 = await socketio_test_client(
        sub_group_client_config, session_ids[1]
    )
    added_test_sub_groups = await add_many_test_sub_groups(
        connection_user1.token_payload()
    )
    selected_sub_group_ids = [
        str(added_test_sub_groups[2].id),
        str(added_test_sub_groups[3].id),
        str(added_test_sub_groups[4].id),
    ]
    current_user2 = await connection_user2.current_user()
    # Connect to the user namespace:
    await connection_user1.connect(
        query_parameters={"resource-ids": ",".join(selected_sub_group_ids)}
    )
    await connection_user2.connect()
    await connection_user1.client.sleep(0.3)
    assert len(connection_user1.responses("transferred")) == 3
    assert connection_user1.responses("transferred")[0]["id"] == str(
        selected_sub_group_ids[0]
    )
    assert connection_user1.responses("transferred")[1]["id"] == str(
        selected_sub_group_ids[1]
    )
    assert connection_user1.responses("transferred")[2]["id"] == str(
        selected_sub_group_ids[2]
    )
    assert len(connection_user2.responses("transferred")) == 0

    # Create sub group - requires a parent group:
    added_test_groups = await add_many_test_groups(connection_user2.token_payload())
    test_sub_group = {
        "name": "Dummy Sub Group",
        "description": "A dummy sub group added via SocketIO.",
    }
    await connection_user2.client.emit(
        "submit",
        {
            "payload": test_sub_group,
            "parent_id": str(added_test_groups[3].id),
            # "inherit": True,
        },
        namespace="/sub-group",
    )
    await connection_user2.client.sleep(0.3)
    # Check if the sub group was created successfully:
    assert connection_user2.responses("status")[0]["success"] == "created"
    assert "id" in connection_user2.responses("status")[0]
    created_sub_group_id = connection_user2.responses("status")[0]["id"]
    assert len(connection_user2.responses("transferred")) == 0

    # Read:
    await connection_user2.client.emit(
        "read", created_sub_group_id, namespace="/sub-group"
    )
    await connection_user2.client.sleep(0.3)
    assert len(connection_user2.responses("transferred")) == 1
    assert connection_user2.responses("transferred")[0]["id"] == created_sub_group_id
    assert (
        connection_user2.responses("transferred")[0]["name"] == test_sub_group["name"]
    )
    assert (
        connection_user2.responses("transferred")[0]["description"]
        == test_sub_group["description"]
    )

    # User 1 shares a sub-group with user 2:
    shared_sub_group_id = str(added_test_sub_groups[3].id)
    await connection_user1.client.emit(
        "share",
        {
            "resource_id": shared_sub_group_id,
            "identity_id": str(current_user2.user_id),
            "action": "own",
        },
        namespace="/sub-group",
    )
    await connection_user1.client.sleep(0.3)
    assert connection_user1.responses("status")[0]["success"] == "shared"
    assert connection_user1.responses("status")[0]["id"] == shared_sub_group_id
    assert len(connection_user2.responses("transferred")) == 1

    # Update sub group:
    updated_sub_group = {
        "id": shared_sub_group_id,
        "description": "Updated description",
    }
    await connection_user2.client.emit(
        "submit", {"payload": updated_sub_group}, namespace="/sub-group"
    )
    await connection_user2.client.sleep(0.3)
    assert connection_user2.responses("status")[1]["success"] == "updated"
    assert connection_user2.responses("status")[1]["id"] == shared_sub_group_id
    assert len(connection_user1.responses("transferred")) == 4
    assert connection_user1.responses("transferred")[3]["id"] == shared_sub_group_id
    assert connection_user1.responses("transferred")[3]["name"] == str(
        added_test_sub_groups[3].name
    )
    assert (
        connection_user1.responses("transferred")[3]["description"]
        == "Updated description"
    )
    assert len(connection_user2.responses("transferred")) == 2
    assert connection_user2.responses("transferred")[1]["id"] == shared_sub_group_id
    assert connection_user2.responses("transferred")[1]["name"] == str(
        added_test_sub_groups[3].name
    )
    assert (
        connection_user2.responses("transferred")[1]["description"]
        == "Updated description"
    )

    # Delete sub group:
    await connection_user2.client.emit(
        "delete", shared_sub_group_id, namespace="/sub-group"
    )
    await connection_user2.client.sleep(0.3)
    assert connection_user2.responses("status")[2]["success"] == "deleted"
    assert connection_user2.responses("status")[2]["id"] == shared_sub_group_id
    assert connection_user2.responses("deleted")[0] == shared_sub_group_id

    # Read deleted sub group fails:
    await connection_user2.client.emit(
        "read", shared_sub_group_id, namespace="/sub-group"
    )
    await connection_user2.client.sleep(0.3)
    assert len(connection_user2.responses("transferred")) == 2
    assert connection_user2.responses("status")[3]["success"] == "deleted"
    assert connection_user2.responses("status")[3]["id"] == shared_sub_group_id
    assert (
        connection_user2.responses("status")[4]["error"]
        == f"Resource {shared_sub_group_id} not found."
    )
