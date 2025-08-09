import pytest

from tests.utils import (
    session_id_admin_read_write_socketio,
    session_id_user1_read_write_socketio,
)

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Ueber Group Namespace Tests:
# ✔︎ Admin connects, creates, updates, and deletes ueber group
# ✔︎ Admin gets all existing ueber groups on connnect
# ✔︎ User fails to create ueber group
# ✔︎ User succeeds to update ueber group, where user is owner
# ✔︎ User fails to update ueber group, due to missing ownership
# ✔︎ User fails to delete ueber group, despite being owner


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids", [[session_id_admin_read_write_socketio]], indirect=True
)
async def test_admin_access_connect_create_update_delete_events(
    socketio_test_client_ueber_group_namespace,
):
    """Test admin access to connect, create, update, and delete events in the ueber group namespace."""
    connection = await socketio_test_client_ueber_group_namespace()
    # Connect to the ueber group namespace:
    await connection.connect()
    assert connection.responses("transfer") == []

    # Create ueber group:
    test_group = {
        "name": "Dummy Ueber Group",
        "description": "A dummy group added via SocketIO.",
    }
    await connection.client.emit("submit", test_group, namespace="/ueber-group")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[0]["success"] == "created"
    assert "id" in connection.responses("status")[0]
    created_uber_group_id = connection.responses("status")[0]["id"]
    assert len(connection.responses("transfer")) == 0

    # Update ueber group:
    updated_group = {
        **test_group,
        "description": "Updated description",
        "id": created_uber_group_id,
    }
    await connection.client.emit("submit", updated_group, namespace="/ueber-group")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[1]["success"] == "updated"
    assert connection.responses("status")[1]["id"] == created_uber_group_id
    assert len(connection.responses("transfer")) == 1
    assert connection.responses("transfer")[0]["id"] == created_uber_group_id
    assert connection.responses("transfer")[0]["description"] == "Updated description"
    assert connection.responses("transfer")[0]["name"] == "Dummy Ueber Group"

    # Delete ueber group event:
    await connection.client.emit(
        "delete", created_uber_group_id, namespace="/ueber-group"
    )
    await connection.client.sleep(0.3)
    assert connection.responses("status")[2]["success"] == "deleted"
    assert connection.responses("status")[2]["id"] == created_uber_group_id
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
    assert len(connection.responses("transfer")) == 3


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
    assert connection.responses("transfer") == []

    # Create ueber group:
    test_group = {
        "name": "Dummy Ueber Group",
        "description": "A dummy group added via SocketIO.",
    }
    await connection.client.emit("submit", test_group, namespace="/ueber-group")
    await connection.client.sleep(0.3)
    assert connection.responses("status")[0]["error"] == "401: Invalid token."
    assert len(connection.responses("status")) == 1
    assert len(connection.responses("transfer")) == 0


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

    assert len(connection_admin.responses("transfer")) == 3
    assert len(connection_user.responses("transfer")) == 1

    # User updates ueber group:
    updated_test_group = {
        "id": str(many_test_ueber_groups[1].id),
        "name": "Updated Dummy Ueber Group",
        "description": "An updated dummy group added via SocketIO.",
    }
    await connection_user.client.emit(
        "submit", updated_test_group, namespace="/ueber-group"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["success"] == "updated"
    assert connection_user.responses("status")[0]["id"] == updated_test_group["id"]
    assert len(connection_user.responses("transfer")) == 2
    assert connection_user.responses("transfer")[1]["id"] == updated_test_group["id"]
    assert (
        connection_user.responses("transfer")[1]["description"]
        == updated_test_group["description"]
    )
    assert (
        connection_user.responses("transfer")[1]["name"] == updated_test_group["name"]
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

    assert len(connection_admin.responses("transfer")) == 3
    assert connection_user.responses("transfer") == []

    # User updates ueber group:
    updated_test_group = {
        "id": str(many_test_ueber_groups[1].id),
        "name": "Updated Dummy Ueber Group",
        "description": "An updated dummy group added via SocketIO.",
    }
    await connection_user.client.emit(
        "submit", updated_test_group, namespace="/ueber-group"
    )
    await connection_user.client.sleep(0.3)
    assert (
        connection_user.responses("status")[0]["error"]
        == "404: UeberGroup not updated."
    )
    assert connection_user.responses("transfer") == []


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

    assert len(connection_admin.responses("transfer")) == 3
    assert len(connection_user.responses("transfer")) == 1

    # User deletes ueber group:
    await connection_user.client.emit(
        "delete", str(many_test_ueber_groups[1].id), namespace="/ueber-group"
    )
    await connection_user.client.sleep(0.3)
    assert connection_user.responses("status")[0]["error"] == "401: Invalid token."
    assert len(connection_user.responses("transfer")) == 1
