import copy
from datetime import datetime
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from socketio.exceptions import ConnectionError

from core.types import IdentityType
from crud.demo_resource import DemoResourceCRUD
from models.access import AccessPolicy
from models.demo_resource import DemoResource, DemoResourceExtended
from models.identity import Group, UeberGroup
from tests.utils import (
    many_test_demo_resources,
    session_id_admin_read,
    session_id_admin_read_socketio,
    session_id_admin_read_write_socketio,
    session_id_admin_read_write_socketio_groups,
    session_id_admin_write,
    session_id_user1_read,
    session_id_user1_read_socketio,
    session_id_user1_read_write_socketio,
    session_id_user1_read_write_socketio_groups,
    session_id_user1_write,
    session_id_user2_read_socketio,
    session_id_user2_read_write_socketio,
    session_id_user2_read_write_socketio_groups,
    token_admin_read_write_socketio,
)

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Connection:
# ✔︎ user connects to demo_resource namespace with a token that has no socketio scope => error
# ✔︎ resource owner connects to demo_resource namespace and gets all demo resources
# ✔︎ user connects to demo_resource namespace and gets allowed demo resources
# ✔︎ user connects to demo_resource namespace and gets allowed demo resources with access data
# ✔︎ user gets error on status event due to database error
# Creation:
# ✔︎ user submits resource without id field => new resource created
# ✔︎ user submits resource with "new_" string at beginning of id field => new resource created
# ✔︎ user submits resource with random string in id field => new resource created
# ✔︎ user submits resource with mandatory data (here name) missing => error
# ✔︎ user submits resources with a UUID that does not exist fails
# Updating
# ✔︎ user submits resource with a UUID that exists => update
# ✔︎ user submits resource with a UUID that exists and has no write access => error
# Deletion:
# ✔︎ one client deletes a demo resource and another client (same user) gets the remove event
# ✔︎ one client deletes a demo resource and another client (different user) gets the remove event
# ✔︎ client tries to delete demo resource without owner rights fails and returns status


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_admin_read],
        [session_id_admin_write],
        [session_id_user1_read],
        [session_id_user1_write],
    ],
    # [session_id_admin_read_write_socketio, session_id_user1_read_write_socketio],# actually connects to the namespace!
    indirect=True,
)
async def test_demo_resource_namespace_fails_to_connect_when_socketio_scope_is_missing_in_token(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo_resource_namespace socket.io connection needs socketio scope in token."""

    try:
        connection = await socketio_test_client_demo_resource_namespace()
        await connection.connect()
        raise Exception(
            "This should have failed due to missing authentication in on_connect."
        )
    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_admin_read_write_socketio],
        [session_id_user1_read_write_socketio],
        [session_id_user1_read_socketio],
        [session_id_user1_read_socketio],
    ],
    indirect=True,
)
async def test_owner_connects_to_demo_resource_namespace_and_gets_all_demoresources(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""

    transfer_data = []
    connection = await socketio_test_client_demo_resource_namespace()
    resources = await add_test_demo_resources(connection.token_payload())
    await connection.connect()

    await connection.client.sleep(0.2)
    transfer_data = connection.responses("transferred")

    assert len(transfer_data) == 4
    for transfer, resource in zip(transfer_data, resources):
        assert "category" in transfer
        assert "tags" in transfer
        assert DemoResource.model_validate(transfer) == resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio], [session_id_user1_read_socketio]],
    indirect=True,
)
async def test_user_connects_to_demo_resource_namespace_and_gets_allowed_demoresources(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    connection = await socketio_test_client_demo_resource_namespace()
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await connection.current_user()

    policies = [
        {
            "resource_id": resources[1].id,
            "identity_id": current_user.user_id,
            "action": "read",
        },
        {
            "resource_id": resources[3].id,
            "identity_id": current_user.user_id,
            "action": "write",
        },
    ]
    for policy in policies:
        await add_test_policy_for_resource(policy)

    await connection.connect()
    transfer_data = []

    await connection.client.sleep(0.2)
    transfer_data = connection.responses("transferred")

    resources_with_user_acccess = [
        resources[1],  # Read access
        resources[3],  # Write access
    ]

    assert len(transfer_data) == 2
    for response, resource in zip(transfer_data, resources_with_user_acccess):
        assert "category" in response
        assert "tags" in response
        assert "access_right" not in response
        assert "access_policies" not in response
        assert "created_at" not in response
        assert "last_modified_at" not in response
        assert DemoResource.model_validate(response) == resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_connects_to_demo_resource_namespace_and_gets_allowed_demoresources_with_access_data(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    connection = await socketio_test_client_demo_resource_namespace()
    current_user = await connection.current_user()

    time_before_creation = datetime.now()
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    time_after_creation = datetime.now()

    policies = [
        {
            "resource_id": resources[1].id,
            "identity_id": current_user.user_id,
            "action": "own",
        },
        {
            "resource_id": resources[3].id,
            "identity_id": current_user.user_id,
            "action": "write",
        },
    ]
    for policy in policies:
        await add_test_policy_for_resource(policy)

    await connection.connect(query_parameters={"request-access-data": "true"})

    await connection.client.sleep(1)
    transfer_data = connection.responses("transferred")

    resources_with_user_acccess = [
        resources[1],  # Own access
        resources[3],  # Write access
    ]

    assert len(transfer_data) == 2
    for response, resource in zip(transfer_data, resources_with_user_acccess):
        modelled_response = DemoResourceExtended.model_validate(response)
        assert "category" in response
        assert "tags" in response
        assert modelled_response.creation_date >= time_before_creation
        assert modelled_response.creation_date <= time_after_creation
        assert modelled_response.last_modified_date == modelled_response.creation_date
        assert DemoResource.model_validate(response) == resource

    assert transfer_data[0]["access_right"] == "own"
    assert "id" in transfer_data[0]["access_policies"][1]
    assert (
        UUID(transfer_data[0]["access_policies"][1]["identity_id"])
        == policies[0]["identity_id"]
    )
    assert (
        UUID(transfer_data[0]["access_policies"][1]["resource_id"])
        == policies[0]["resource_id"]
    )
    assert transfer_data[0]["access_policies"][1]["action"] == "own"
    assert not transfer_data[0]["access_policies"][1]["public"]
    assert transfer_data[1]["access_right"] == "write"
    assert transfer_data[1]["access_policies"] is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_gets_error_on_status_event_due_to_database_error(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource connect event."""
    with patch(
        "crud.demo_resource.DemoResourceCRUD.read",
        side_effect=Exception("Database error."),
    ):

        transfer_data = []
        status_data = []

        connection = await socketio_test_client_demo_resource_namespace()
        await connection.connect()

        # Wait for the response to be set
        # await client.sleep(0.2)

        transfer_data = connection.responses("transferred")
        status_data = connection.responses("status")

        assert transfer_data == []
        assert status_data == [{"error": "Database error."}]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio, session_id_admin_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation(
    socketio_test_client_demo_resource_namespace,
    session_ids: list[str],
):
    """Test the demo resource submit event without ID."""

    status_data = []
    connection_user = await socketio_test_client_demo_resource_namespace()
    connection_admin = await socketio_test_client_demo_resource_namespace(
        session_ids[1]
    )
    await connection_user.connect()
    await connection_admin.connect()

    await connection_user.client.emit(
        "submit", {"payload": many_test_demo_resources[1]}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection_user.client.sleep(0.2)

    status_data = connection_user.responses("status")

    print("=== test - create demo_resource - Status data ===")
    print(status_data, flush=True)

    assert status_data[0]["submitted_id"] is None
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["success"] == "created"

    assert len(connection_admin.responses("status")) == 1
    assert connection_admin.responses("status")[0]["success"] == "shared"
    assert connection_admin.responses("status")[0]["id"] == status_data[0]["id"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_admin_read_socketio],
        [session_id_user1_read_socketio],
    ],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation_missing_write_scope_in_token(
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource submit event without ID."""
    connection = await socketio_test_client_demo_resource_namespace()

    existing_demo_resources = await add_test_demo_resources()
    current_user = await connection.current_user()

    if "Admin" not in current_user.azure_token_roles:
        for demo_resource in existing_demo_resources:
            policy = {
                "resource_id": demo_resource.id,
                "identity_id": current_user.user_id,
                "action": "read",
            }
            await add_test_policy_for_resource(policy)

    await connection.connect()

    await connection.client.emit(
        "submit", {"payload": many_test_demo_resources[1]}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    status_data = connection.responses("status")
    transfer_data = connection.responses("transferred")

    # The get all resources on connect works: requires only "socketio" and "api.read" scope
    assert len(transfer_data) == len(existing_demo_resources)
    for transfer, resource in zip(transfer_data, existing_demo_resources):
        assert "category" in transfer
        assert "tags" in transfer
        assert DemoResource.model_validate(transfer) == resource

    # However the submit event fails due to missing "api.write" scope
    assert len(status_data) == 1
    assert status_data[0]["error"] == "401: Invalid token."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio]],
    indirect=True,
)
async def test_admin_submits_resource_with_new__string_in_id_field_for_creation(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "new_34ab56z"

    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()

    await connection.client.emit(
        "submit", {"payload": test_resource}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.3)
    status_data = connection.responses("status")

    assert len(status_data) == 2

    # assert "id" in status[0]
    assert status_data[0]["success"] == "created"
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["submitted_id"] == test_resource["id"]

    # admin also gets a shared notification for each created resource:
    assert status_data[1]["success"] == "shared"
    assert status_data[1]["id"] == status_data[0]["id"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_with_new__string_in_id_field_for_creation(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "new_34ab56z"

    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()

    await connection.client.emit(
        "submit", {"payload": test_resource}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.3)
    status_data = connection.responses("status")

    # assert "id" in status[0]
    assert status_data[0]["submitted_id"] == test_resource["id"]
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["success"] == "created"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_two_resource_with_new__string_in_id_field_for_creation(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "new_34ab56z"

    test_resource2 = copy.deepcopy(many_test_demo_resources[1])
    test_resource2["id"] = "new_439832f"

    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()

    time_before_first_submit = datetime.now()
    await connection.client.emit(
        "submit", {"payload": test_resource}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    status_data = connection.responses("status")

    assert len(status_data) == 1

    assert status_data[0]["submitted_id"] == test_resource["id"]
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["success"] == "created"

    time_before_second_submit = datetime.now()
    await connection.client.emit(
        "submit", {"payload": test_resource2}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)

    status_data = connection.responses("status")

    assert len(status_data) == 2

    assert status_data[0]["submitted_id"] == test_resource["id"]
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["success"] == "created"
    assert status_data[1]["submitted_id"] == test_resource2["id"]
    assert UUID(status_data[1]["id"])  # Check if the ID is a valid UUID
    assert status_data[1]["success"] == "created"

    assert time_before_first_submit < time_before_second_submit


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_with_random_string_in_id_field_fails(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "random_string"

    status_data = []
    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()

    await connection.client.emit(
        "submit", {"payload": test_resource}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    status_data = connection.responses("status")

    assert status_data[0]["error"] == "badly formed hexadecimal UUID string"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation_missing_name(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource delete event."""

    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()
    await connection.client.emit(
        "submit",
        {"payload": {"description": "Description of test resource"}},
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)

    statuses_data = connection.responses("status")

    assert (
        statuses_data[0]["error"]
        == "1 validation error for DemoResourceCreate\nname\n  Field required [type=missing, input_value={'description': 'Description of test resource'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_with_nonexisting_uuid_fails(
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource submit event with non-existing UUID."""

    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()

    test_demo_resource = copy.deepcopy(many_test_demo_resources[1])
    # test_demo_resource = many_test_demo_resources[1]
    test_demo_resource["id"] = str(uuid4())  # Set a non-existing UUID

    await connection.client.emit(
        "submit", {"payload": test_demo_resource}, namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    statuses_data = connection.responses("status")

    assert statuses_data[0]["error"] == "404: DemoResource not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_existing_resource_for_update(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    connection = await socketio_test_client_demo_resource_namespace()
    resources = await add_test_demo_resources(connection.token_payload())

    index_of_resource_to_update = next(
        i for i, r in enumerate(resources) if r.name == "A second cat 2 resource"
    )

    await connection.connect()

    modified_demo_resource = resources[index_of_resource_to_update]
    modified_demo_resource.name = "Altering the name of this demo resource"
    modified_demo_resource.language = "fr-FR"
    # modified_demo_resource.id = modified_demo_resource.id
    if modified_demo_resource.category_id:
        modified_demo_resource.category_id = modified_demo_resource.category_id

    await connection.client.emit(
        "submit",
        {"payload": modified_demo_resource.model_dump(mode="json")},
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    statuses_data = connection.responses("status")

    assert UUID(statuses_data[0]["id"])  # Check if the ID is a valid UUID
    assert statuses_data[0]["success"] == "updated"
    assert statuses_data[0]["id"] == str(resources[index_of_resource_to_update].id)

    async with DemoResourceCRUD() as crud:
        current_user = await connection.current_user()
        updated_resource = await crud.read_by_id(
            resources[index_of_resource_to_update].id, current_user
        )

        assert (
            updated_resource.description
            == resources[index_of_resource_to_update].description
        )
        assert (
            updated_resource.category_id
            == resources[index_of_resource_to_update].category_id
        )
        assert updated_resource.tags == resources[index_of_resource_to_update].tags
        assert updated_resource.name == "Altering the name of this demo resource"
        assert updated_resource.language == "fr-FR"
        assert updated_resource.id == resources[index_of_resource_to_update].id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_admin_read_socketio],
        [session_id_user1_read_socketio],
    ],
    indirect=True,
)
async def test_user_updates_demo_resource_missing_write_scope_in_token_fails(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    connection = await socketio_test_client_demo_resource_namespace()
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await connection.current_user()

    if "Admin" not in current_user.azure_token_roles:
        policy = {
            "resource_id": resources[3].id,
            "identity_id": current_user.user_id,
            "action": "write",
        }
        await add_test_policy_for_resource(policy)

    await connection.connect()

    modified_demo_resource = resources[3]
    modified_demo_resource.name = "Altering the name of this demo resource"
    modified_demo_resource.language = "fr-FR"
    modified_demo_resource.id = modified_demo_resource.id
    if modified_demo_resource.category_id:
        modified_demo_resource.category_id = modified_demo_resource.category_id

    await connection.client.emit(
        "submit",
        {"payload": modified_demo_resource.model_dump(mode="json")},
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    status_data = connection.responses("status")
    assert status_data[0]["error"] == "401: Invalid token."

    # Connection is still open, so disconnection_result should be None
    disconnection_result = await connection.client.disconnect()
    assert disconnection_result is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_updates_demo_resource_not_having_write_access_fails(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    connection = await socketio_test_client_demo_resource_namespace()

    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await connection.current_user()

    policy = {
        "resource_id": resources[3].id,
        "identity_id": current_user.user_id,
        "action": "read",
    }
    await add_test_policy_for_resource(policy)

    await connection.connect()

    modified_demo_resource = resources[3]
    modified_demo_resource.name = "Altering the name of this demo resource"
    modified_demo_resource.language = "fr-FR"
    modified_demo_resource.id = modified_demo_resource.id
    if modified_demo_resource.category_id:
        modified_demo_resource.category_id = modified_demo_resource.category_id

    await connection.client.emit(
        "submit",
        {"payload": modified_demo_resource.model_dump(mode="json")},
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    statuses_data = connection.responses("status")

    assert statuses_data[0]["error"] == "404: DemoResource not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_one_client_deletes_a_demo_resource_and_another_client_from_same_user_gets_the_remove_event(
    add_test_demo_resources: list[DemoResource],
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource delete event."""
    connection1 = await socketio_test_client_demo_resource_namespace()
    resources = await add_test_demo_resources(connection1.token_payload())

    # Two clients from same user - coming from token_payload()!
    await connection1.connect()
    connection2 = await socketio_test_client_demo_resource_namespace()
    await connection2.connect()

    await connection1.client.emit(
        "delete", str(resources[2].id), namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection1.client.sleep(0.2)
    await connection2.client.sleep(0.2)

    statuses_data_client1 = connection1.responses("status")
    statuses_data_client2 = connection2.responses("status")
    deleted_data_client1 = connection1.responses("deleted")
    deleted_data_client2 = connection2.responses("deleted")

    assert deleted_data_client1 == [str(resources[2].id)]
    assert statuses_data_client1 == [{"success": "deleted", "id": str(resources[2].id)}]
    assert deleted_data_client2 == [str(resources[2].id)]
    assert statuses_data_client2 == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio, session_id_user2_read_socketio]],
    indirect=True,
)
async def test_one_client_deletes_a_demo_resource_and_another_client_with_different_user_gets_the_deleted_event(
    session_ids,
    add_test_policy_for_resource,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource delete event."""
    # Two clients from different users
    connection1 = await socketio_test_client_demo_resource_namespace()
    connection2 = await socketio_test_client_demo_resource_namespace(session_ids[1])
    resources = await add_test_demo_resources(connection1.token_payload())

    other_user = await connection2.current_user()
    policy = {
        "resource_id": resources[3].id,
        "identity_id": other_user.user_id,
        "action": "read",
    }
    # Creating user (first user) shares the resource with other user
    await add_test_policy_for_resource(policy, connection1.token_payload())

    await connection1.connect()
    await connection2.connect()

    await connection1.client.emit(
        "delete", str(resources[2].id), namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection1.client.sleep(0.2)
    await connection2.client.sleep(0.2)

    assert connection1.responses("deleted") == [str(resources[2].id)]
    assert connection1.responses("status") == [
        {"success": "deleted", "id": str(resources[2].id)}
    ]
    assert connection2.responses("deleted") == [str(resources[2].id)]
    assert connection2.responses("status") == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_admin_read_socketio], [session_id_user1_read_socketio]],
    indirect=True,
)
async def test_user_deletes_a_demo_resource_missing_write_scope_in_token(
    add_test_demo_resources: list[DemoResource],
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource delete event."""
    connection = await socketio_test_client_demo_resource_namespace()
    resources = await add_test_demo_resources(connection.token_payload())
    await connection.connect()

    await connection.client.emit(
        "delete", str(resources[2].id), namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)
    statuses_data = connection.responses("status")
    deleted_data = connection.responses("deleted")

    assert deleted_data == []
    assert statuses_data == [{"error": "401: Invalid token."}]

    disconnection_result = await connection.client.disconnect()
    assert disconnection_result is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_client_tries_to_delete_demo_resource_without_owner_rights_fails_and_returns_status(
    add_test_demo_resources: list[DemoResource],
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource delete event."""
    connection = await socketio_test_client_demo_resource_namespace()
    await connection.connect()
    resources = await add_test_demo_resources(token_admin_read_write_socketio)

    await connection.client.emit(
        "delete", str(resources[2].id), namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.2)

    assert connection.responses("status")[0] == {
        "error": "404: DemoResource not deleted."
    }


# Testing the share events:

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# ✔︎ user shares a resource with a group: success
# ✔︎ user owning resource updates access to a different action level: success
# ✔︎ user owning resource updates access to same action level: error
# ✔︎ user deletes access to a resource: success
#   includes:
#   ✔︎ user has access to resource: success & transfer data
#   ✔︎ user does not have access to resource: error
# ✔︎ user tries to share a resource, that the user does not own: error
# ✔︎ user downgrades last inherited owner access
# ✔︎ user removes last inherited owner access and consecutive read fails


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio,
        ],
        [
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio,
        ],
        [
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio,
        ],
    ],
    indirect=True,
)
async def test_user_shares_owned_resource_with_groups_in_azure_token(
    session_ids,
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    # First user owns the resources:
    connection1 = await socketio_test_client_demo_resource_namespace()
    connection2 = await socketio_test_client_demo_resource_namespace(session_ids[1])
    connection3 = await socketio_test_client_demo_resource_namespace(session_ids[2])
    token_user1 = connection1.token_payload()
    token_user2 = connection2.token_payload()
    token_user3 = connection3.token_payload()
    # TBD:
    query_parameters_user1 = {}
    if "groups" in token_user1:
        identity_ids_user1 = [identity_id for identity_id in token_user1["groups"]]
        query_parameters_user1 = {"identity-ids": ",".join(identity_ids_user1)}

    query_parameters_user2 = {}
    if "groups" in token_user2:
        identity_ids_user2 = [identity_id for identity_id in token_user2["groups"]]
        query_parameters_user2 = {"identity-ids": ",".join(identity_ids_user2)}

    query_parameters_user3 = {}
    if "groups" in token_user3:
        identity_ids_user3 = [identity_id for identity_id in token_user3["groups"]]
        query_parameters_user3 = {"identity-ids": ",".join(identity_ids_user3)}

    resources = await add_test_demo_resources(token_user1)
    # resources = await add_test_demo_resources(token_admin_read_write_socketio)

    await connection1.connect(query_parameters=query_parameters_user1)
    await connection2.connect(query_parameters=query_parameters_user2)
    await connection3.connect(query_parameters=query_parameters_user3)

    # First user shares the resources with a group, that first and second user are member of:
    await connection1.client.emit(
        "share",
        {
            "resource_id": str(resources[0].id),
            "identity_id": token_user1["groups"][1],
            "action": "read",
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection1.client.sleep(0.4)

    status_data1 = connection1.responses("status")
    status_data2 = connection2.responses("status")
    status_data3 = connection3.responses("status")

    assert status_data1 == [{"success": "shared", "id": str(resources[0].id)}]
    assert status_data2 == [{"success": "shared", "id": str(resources[0].id)}]
    # Even the third user is admin, share events don't get emitted automatically to admin,
    # Anyways can see everything!
    # Unless the admin also has the team in the groups from token.
    assert status_data3 == []

    transfer_data1 = connection1.responses("transferred")
    transfer_data2 = connection2.responses("transferred")
    assert len(transfer_data1) == len(resources)
    # Even though the access has been granted, no resources are transferred yet.
    # User needs to make another emit to event read, to get the resource,
    # because other existing access policies might influence the access rights.
    assert len(transfer_data2) == 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio,
        ],
        [
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio,
        ],
        [
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio,
        ],
    ],
    indirect=True,
)
async def test_user_updates_access_to_owned_resource_for_a_group_identity(
    session_ids,
    add_test_demo_resources: list[DemoResource],
    add_many_test_groups: list[Group],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource connect event."""
    connection1 = await socketio_test_client_demo_resource_namespace()
    connection2 = await socketio_test_client_demo_resource_namespace(session_ids[1])
    connection3 = await socketio_test_client_demo_resource_namespace(session_ids[2])

    many_test_groups = await add_many_test_groups()
    common_group_id = many_test_groups[2].id
    query_parameters_user1 = {"identity-ids": str(common_group_id)}
    query_parameters_user2 = {"identity-ids": str(common_group_id)}

    # First user owns the resources:
    token_user1 = connection1.token_payload()

    current_user1 = await connection1.current_user()
    current_user2 = await connection2.current_user()

    await add_one_parent_child_identity_relationship(
        current_user1.user_id, common_group_id, IdentityType.user, inherit=True
    )
    await add_one_parent_child_identity_relationship(
        current_user2.user_id, common_group_id, IdentityType.user, inherit=True
    )

    resources = await add_test_demo_resources(token_user1)

    await add_one_test_access_policy(
        {
            "resource_id": str(resources[1].id),
            "identity_id": str(common_group_id),
            "action": "read",
        }
    )

    await connection1.connect(query_parameters=query_parameters_user1)
    await connection2.connect(query_parameters=query_parameters_user2)
    await connection3.connect()

    # First user shares the resources with a group, that first and second user are member of:
    await connection1.client.emit(
        "share",
        {
            "resource_id": str(resources[1].id),
            "identity_id": str(common_group_id),
            "action": "read",
            "new_action": "write",
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection1.client.sleep(0.4)

    status_data1 = connection1.responses("status")
    status_data2 = connection2.responses("status")
    status_data3 = connection3.responses("status")
    assert status_data1 == [{"success": "shared", "id": str(resources[1].id)}]
    assert status_data2 == [{"success": "shared", "id": str(resources[1].id)}]
    # Even the third user is admin, share events don't get emitted automatically to admin,
    # Anyways can see everything!
    # Unless the admin also has the team in the groups from token.
    assert status_data3 == []

    transfer_data1 = connection1.responses("transferred")
    transfer_data2 = connection2.responses("transferred")
    assert len(transfer_data1) == len(resources)
    # Group had access before, so user2 got the resource on_connect:
    assert len(transfer_data2) == 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio,
        ],
        [
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio,
        ],
        [
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio,
        ],
    ],
    indirect=True,
)
async def test_user_updates_access_to_owned_resource_for_a_group_identity_to_same_access(
    session_ids,
    add_test_demo_resources: list[DemoResource],
    add_many_test_groups: list[Group],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource connect event."""
    # First user owns the resources:
    connection1 = await socketio_test_client_demo_resource_namespace()
    connection2 = await socketio_test_client_demo_resource_namespace(session_ids[1])
    connection3 = await socketio_test_client_demo_resource_namespace(session_ids[2])

    many_test_groups = await add_many_test_groups()
    common_group_id = many_test_groups[2].id
    query_parameters_user1 = {"identity-ids": str(common_group_id)}
    query_parameters_user2 = {"identity-ids": str(common_group_id)}

    token_user1 = connection1.token_payload()
    current_user1 = await connection1.current_user()
    current_user2 = await connection2.current_user()

    await add_one_parent_child_identity_relationship(
        current_user1.user_id, common_group_id, IdentityType.user, inherit=True
    )
    await add_one_parent_child_identity_relationship(
        current_user2.user_id, common_group_id, IdentityType.user, inherit=True
    )

    resources = await add_test_demo_resources(token_user1)

    await add_one_test_access_policy(
        {
            "resource_id": str(resources[1].id),
            "identity_id": str(common_group_id),
            "action": "write",
        }
    )

    await connection1.connect(query_parameters=query_parameters_user1)
    await connection2.connect(query_parameters=query_parameters_user2)
    await connection3.connect()

    # First user shares the resources with a group, that first and second user are member of:
    await connection1.client.emit(
        "share",
        {
            "resource_id": str(resources[1].id),
            "identity_id": str(common_group_id),
            "action": "read",
            "new_action": "write",
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection1.client.sleep(0.2)

    assert connection1.responses("status") == [
        {"error": "404: Access policy not found."}
    ]
    assert connection2.responses("status") == []
    # Even the third user is admin, share events don't get emitted automatically to admin,
    # Anyways can see everything!
    # Unless the admin also has the team in the groups from token.
    assert connection3.responses("status") == []

    transfer_data1 = connection1.responses("transferred")
    transfer_data2 = connection2.responses("transferred")
    assert len(transfer_data1) == len(resources)
    # Group had access before, so user2 got the resource on_connect:
    assert len(transfer_data2) == 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio,
        ],
        [
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio_groups,
            session_id_user2_read_write_socketio,
        ],
        [
            session_id_user2_read_write_socketio_groups,
            session_id_admin_read_write_socketio_groups,
            session_id_user1_read_write_socketio,
        ],
    ],
    indirect=True,
)
async def test_user_removes_share_with_group(
    session_ids,
    add_test_demo_resources: list[DemoResource],
    add_many_test_groups: list[Group],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
    socketio_test_client_demo_resource_namespace,
):
    """Test the demo resource connect event."""
    connection1 = await socketio_test_client_demo_resource_namespace()
    connection2 = await socketio_test_client_demo_resource_namespace(session_ids[1])
    connection3 = await socketio_test_client_demo_resource_namespace(session_ids[2])

    # First user owns the resources:
    many_test_groups = await add_many_test_groups()
    common_group_id = many_test_groups[2].id
    query_parameters_user1 = {"identity-ids": str(common_group_id)}
    query_parameters_user2 = {"identity-ids": str(common_group_id)}

    token_user1 = connection1.token_payload()
    current_user1 = await connection1.current_user()
    current_user2 = await connection2.current_user()

    await add_one_parent_child_identity_relationship(
        current_user1.user_id, common_group_id, IdentityType.user, inherit=True
    )
    await add_one_parent_child_identity_relationship(
        current_user2.user_id, common_group_id, IdentityType.user, inherit=True
    )

    resources = await add_test_demo_resources(token_user1)

    await add_one_test_access_policy(
        {
            "resource_id": str(resources[1].id),
            "identity_id": str(common_group_id),
            "action": "write",
        }
    )
    await connection1.connect(query_parameters=query_parameters_user1)
    await connection2.connect(query_parameters=query_parameters_user2)
    await connection3.connect()

    # First user shares the resources with a group, that first and second user are member of:
    await connection1.client.emit(
        "share",
        {
            "resource_id": str(resources[1].id),
            "identity_id": str(common_group_id),
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection1.client.sleep(0.3)

    await connection1.client.emit(
        "read",
        str(resources[1].id),
        namespace="/demo-resource",
    )

    await connection1.client.sleep(0.3)

    await connection2.client.emit(
        "read",
        str(resources[1].id),
        namespace="/demo-resource",
    )

    await connection1.client.sleep(0.4)

    status_data1 = connection1.responses("status")
    status_data2 = connection2.responses("status")
    status_data3 = connection3.responses("status")
    assert status_data1 == [
        {
            "success": "unshared",
            "id": str(resources[1].id),
        }
    ]
    # After read event, triggered by unshare, user2 has no longer access:
    assert status_data2 == [
        {
            "success": "unshared",
            "id": str(resources[1].id),
        },
        {"success": "deleted", "id": str(resources[1].id)},
        {"error": f"Resource {str(resources[1].id)} not found."},
    ]
    # Even the third user is admin, share events don't get emitted automatically to admin,
    # Anyways can see everything!
    # Unless the admin also has the team in the groups from token.
    assert status_data3 == []

    # user one gets the resource again after the unshare event
    # still has access from own access policy:
    assert len(connection1.responses("transferred")) == len(resources) + 1
    # Group had access before, so user2 got the resource on_connect:
    assert len(connection2.responses("transferred")) == 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_user1_read_write_socketio_groups],
        [session_id_user2_read_write_socketio_groups],
    ],
    indirect=True,
)
async def test_user_shares_tries_to_share_resource_without_having_access(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    # First user owns the resources:

    resources = await add_test_demo_resources(token_admin_read_write_socketio)

    connection = await socketio_test_client_demo_resource_namespace()
    token_user1 = connection.token_payload()
    await connection.connect()

    # First user shares the resources with a group, that first and second user are member of:
    await connection.client.emit(
        "share",
        {
            "resource_id": str(resources[0].id),
            "identity_id": token_user1["groups"][1],
            "action": "read",
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.3)

    assert connection.responses("status") == [{"error": "403: Forbidden."}]

    assert len(connection.responses("transferred")) == 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_user1_read_write_socketio_groups],
        [session_id_user2_read_write_socketio_groups],
    ],
    indirect=True,
)
async def test_user_downgrades_last_inherited_owner_access(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
    add_many_test_ueber_groups: list[UeberGroup],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
):
    """Test the demo resource connect event."""

    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    ueber_groups = await add_many_test_ueber_groups(token_admin_read_write_socketio)
    connection = await socketio_test_client_demo_resource_namespace()

    current_user = await connection.current_user()
    # Add current_user to UeberGroup
    await add_one_parent_child_identity_relationship(
        current_user.user_id,
        ueber_groups[0].id,
        IdentityType.user,
        inherit=True,
    )
    # Add owner access policy for the resource to the UeberGroup
    await add_one_test_access_policy(
        {
            "resource_id": str(resources[0].id),
            "identity_id": str(ueber_groups[0].id),  # str(current_user.user_id),
            "action": "own",
        }
    )
    await connection.connect(query_parameters={"request-access-data": True})

    # Wait for the response to be set
    await connection.client.sleep(0.3)

    assert len(connection.responses("transferred")) == 1
    assert connection.responses("transferred")[0]["id"] == str(resources[0].id)
    assert connection.responses("transferred")[0]["name"] == str(resources[0].name)
    assert connection.responses("transferred")[0]["language"] == str(
        resources[0].language
    )
    assert connection.responses("transferred")[0]["description"] == str(
        resources[0].description
    )
    assert connection.responses("transferred")[0]["access_right"] == "own"
    assert len(connection.responses("transferred")[0]["access_policies"]) == 2

    # Downgrade the UeberGroup access to read:
    await connection.client.emit(
        "share",
        {
            "resource_id": str(resources[0].id),
            "identity_id": str(ueber_groups[0].id),
            "action": "own",
            "new_action": "read",
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.4)

    assert connection.responses("status")[0] == {
        "success": "shared",
        "id": str(resources[0].id),
    }

    await connection.client.emit(
        "read", str(resources[0].id), namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.4)

    assert len(connection.responses("transferred")) == 2
    assert connection.responses("transferred")[1]["id"] == str(resources[0].id)
    assert connection.responses("transferred")[1]["name"] == str(resources[0].name)
    assert connection.responses("transferred")[1]["language"] == str(
        resources[0].language
    )
    assert connection.responses("transferred")[1]["description"] == str(
        resources[0].description
    )
    assert connection.responses("transferred")[1]["access_right"] == "read"
    assert connection.responses("transferred")[1]["access_policies"] is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_ids",
    [
        [session_id_user1_read_write_socketio_groups],
        [session_id_user2_read_write_socketio_groups],
    ],
    indirect=True,
)
async def test_user_removes_last_inherited_owner_access_and_reread_fails(
    socketio_test_client_demo_resource_namespace,
    add_test_demo_resources: list[DemoResource],
    add_many_test_ueber_groups: list[UeberGroup],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
):
    """Test the demo resource connect event."""

    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    ueber_groups = await add_many_test_ueber_groups(token_admin_read_write_socketio)
    connection = await socketio_test_client_demo_resource_namespace()

    current_user = await connection.current_user()
    # Add current_user to UeberGroup
    await add_one_parent_child_identity_relationship(
        current_user.user_id,
        ueber_groups[0].id,
        IdentityType.user,
        inherit=True,
    )
    # Add owner access policy for the resource to the UeberGroup
    await add_one_test_access_policy(
        {
            "resource_id": str(resources[0].id),
            "identity_id": str(ueber_groups[0].id),  # str(current_user.user_id),
            "action": "own",
        }
    )
    await connection.connect(query_parameters={"request-access-data": True})

    # Wait for the response to be set
    await connection.client.sleep(0.3)

    assert len(connection.responses("transferred")) == 1
    assert connection.responses("transferred")[0]["id"] == str(resources[0].id)
    assert connection.responses("transferred")[0]["name"] == str(resources[0].name)
    assert connection.responses("transferred")[0]["language"] == str(
        resources[0].language
    )
    assert connection.responses("transferred")[0]["description"] == str(
        resources[0].description
    )
    assert connection.responses("transferred")[0]["access_right"] == "own"
    assert len(connection.responses("transferred")[0]["access_policies"]) == 2

    # Remove the UeberGroup access:
    await connection.client.emit(
        "share",
        {
            "resource_id": str(resources[0].id),
            "identity_id": str(ueber_groups[0].id),
        },
        namespace="/demo-resource",
    )

    # Wait for the response to be set
    await connection.client.sleep(0.3)

    assert connection.responses("status") == [
        {
            "success": "unshared",
            "id": str(resources[0].id),
        }
    ]

    await connection.client.emit(
        "read", str(resources[0].id), namespace="/demo-resource"
    )

    # Wait for the response to be set
    await connection.client.sleep(0.3)

    assert connection.responses("status")[1] == {
        "success": "deleted",
        "id": str(resources[0].id),
    }
    assert connection.responses("status")[2] == {
        "error": f"Resource {str(resources[0].id)} not found."
    }
    assert len(connection.responses("transferred")) == 1
