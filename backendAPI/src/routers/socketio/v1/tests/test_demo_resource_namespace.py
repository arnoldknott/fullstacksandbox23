import copy
from datetime import datetime
from unittest.mock import patch
from uuid import UUID, uuid4

from models.identity import Group
import pytest
from socketio.exceptions import ConnectionError

from crud.demo_resource import DemoResourceCRUD
from models.access import AccessPolicy
from models.demo_resource import DemoResource, DemoResourceExtended
from core.types import IdentityType
from tests.utils import (
    many_test_demo_resources,
    session_id_admin_read,
    session_id_admin_write,
    session_id_admin_read_socketio,
    session_id_admin_read_write_socketio,
    session_id_admin_read_write_socketio_groups,
    session_id_user1_read,
    session_id_user1_write,
    session_id_user1_read_socketio,
    session_id_user1_read_write_socketio,
    session_id_user1_read_write_socketio_groups,
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
# ✔︎ user submits resource with a UUID that exists => update
# ✔︎ user submits resource with a UUID that exists and has no write access => error
# Deletion:
# ✔︎ one client deletes a demo resource and another client gets the remove event
# ✔︎ client tries to delete demo resource without owner rights fails and returns status

client_config_demo_resource_namespace = [
    {
        "namespace": "/demo-resource",
        "events": [
            "transfer",
            "deleted",
            "status",
        ],
    }
]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
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
    socketio_test_client,
):
    """Test the demo_resource_namespace socket.io connection needs socketio scope in token."""

    try:
        async for connection in socketio_test_client(
            client_config_demo_resource_namespace
        ):

            await connection["client"].sleep(1)
            await connection["client"].disconnect()
            raise Exception(
                "This should have failed due to missing authentication in on_connect."
            )
    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [session_id_admin_read_write_socketio],
        [session_id_user1_read_write_socketio],
        [session_id_user1_read_socketio],
        [session_id_user1_read_socketio],
    ],
    indirect=True,
)
async def test_owner_connects_to_demo_resource_namespace_and_gets_all_demoresources(
    current_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(current_token_payload())

    transfer_data = []
    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        transfer_data = connection["responses"]["/demo-resource"]["transfer"]

    assert len(transfer_data) == 4
    for transfer, resource in zip(transfer_data, resources):
        assert "category" in transfer
        assert "tags" in transfer
        assert DemoResource.model_validate(transfer) == resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_write_socketio], [session_id_user1_read_socketio]],
    indirect=True,
)
async def test_user_connects_to_demo_resource_namespace_and_gets_allowed_demoresources(
    current_user_from_session_id,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await current_user_from_session_id(0)

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

    transfer_data = []
    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        transfer_data = connection["responses"]["/demo-resource"]["transfer"]

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
    "session_id_selector",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_connects_to_demo_resource_namespace_and_gets_allowed_demoresources_with_access_data(
    current_user_from_session_id,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    time_before_creation = datetime.now()
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    time_after_creation = datetime.now()
    current_user = await current_user_from_session_id(0)

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

    transfer_data = []

    async for connection in socketio_test_client(
        client_config_demo_resource_namespace,
        query_parameters={"request-access-data": "true"},
    ):

        transfer_data = connection["responses"]["/demo-resource"]["transfer"]

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
    "session_id_selector",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_gets_error_on_status_event_due_to_database_error(
    socketio_test_client,
):
    """Test the demo resource connect event."""
    with patch(
        "crud.demo_resource.DemoResourceCRUD.read",
        side_effect=Exception("Database error."),
    ):

        transfer_data = []
        status_data = []

        async for connection in socketio_test_client(
            client_config_demo_resource_namespace
        ):

            transfer_data = connection["responses"]["/demo-resource"]["transfer"]
            status_data = connection["responses"]["/demo-resource"]["status"]

        # Wait for the response to be set
        # await client.sleep(1)

        assert transfer_data == []
        assert status_data == [{"error": "Database error."}]

        await connection["client"].disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio, session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation(
    socketio_test_client,
):
    """Test the demo resource submit event without ID."""

    status_data = []
    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        await connection["client"].emit(
            "submit", many_test_demo_resources[1], namespace="/demo-resource"
        )

        status_data = connection["responses"]["/demo-resource"]["status"]

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert status_data[0]["submitted_id"] is None
        assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
        assert status_data[0]["success"] == "created"

        await connection["client"].disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [session_id_admin_read_socketio],
        [session_id_user1_read_socketio],
    ],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation_missing_write_scope_in_token(
    current_user_from_session_id,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
    socketio_test_client,
):
    """Test the demo resource submit event without ID."""
    existing_demo_resources = await add_test_demo_resources()
    current_user = await current_user_from_session_id()

    if "Admin" not in current_user.azure_token_roles:
        for demo_resource in existing_demo_resources:
            policy = {
                "resource_id": demo_resource.id,
                "identity_id": current_user.user_id,
                "action": "read",
            }
            await add_test_policy_for_resource(policy)

    status_data = []
    transfer_data = []
    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        transfer_data = connection["responses"]["/demo-resource"]["transfer"]

        await connection["client"].emit(
            "submit", many_test_demo_resources[1], namespace="/demo-resource"
        )

        status_data = connection["responses"]["/demo-resource"]["status"]

        # Wait for the response to be set
        await connection["client"].sleep(1)

        await connection["client"].disconnect()

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
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_with_new__string_in_id_field_for_creation(
    socketio_test_client,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "new_34ab56z"

    status_data = []
    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        await connection["client"].emit(
            "submit", test_resource, namespace="/demo-resource"
        )

        status_data = connection["responses"]["/demo-resource"]["status"]
        # Wait for the response to be set
        await connection["client"].sleep(1)

        await connection["client"].disconnect()

    # assert "id" in status[0]
    assert status_data[0]["submitted_id"] == test_resource["id"]
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["success"] == "created"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_two_resource_with_new__string_in_id_field_for_creation_assessing_order_through_logs(
    socketio_test_client,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "new_34ab56z"

    test_resource2 = copy.deepcopy(many_test_demo_resources[1])
    test_resource2["id"] = "new_439832f"

    status_data = []
    logs = []
    async for connection in socketio_test_client(
        client_config_demo_resource_namespace, logs=logs
    ):

        time_before_first_submit = datetime.now()
        logs.append(
            {
                "event": "submit",
                "timestamp": time_before_first_submit,
                "data": test_resource,
            }
        )
        await connection["client"].emit(
            "submit", test_resource, namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        time_before_second_submit = datetime.now()
        logs.append(
            {
                "event": "submit",
                "timestamp": time_before_second_submit,
                "data": test_resource2,
            }
        )
        await connection["client"].emit(
            "submit", test_resource2, namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        status_data = connection["responses"]["/demo-resource"]["status"]

        await connection["client"].disconnect()

    assert len(logs) == 4  # Two submits, two responses
    assert logs[0]["event"] == "submit"
    assert logs[0]["timestamp"] == time_before_first_submit
    assert logs[0]["data"] == test_resource
    assert logs[1]["event"] == "status"
    assert logs[1]["timestamp"] > time_before_first_submit
    assert logs[1]["timestamp"] < time_before_second_submit
    assert logs[1]["data"]["submitted_id"] == test_resource["id"]
    assert logs[2]["event"] == "submit"
    assert logs[2]["timestamp"] == time_before_second_submit
    assert logs[2]["data"] == test_resource2
    assert logs[3]["event"] == "status"
    assert logs[3]["timestamp"] > time_before_second_submit
    assert logs[3]["data"]["submitted_id"] == test_resource2["id"]

    assert len(status_data) == 2

    assert status_data[0]["submitted_id"] == test_resource["id"]
    assert UUID(status_data[0]["id"])  # Check if the ID is a valid UUID
    assert status_data[0]["success"] == "created"
    assert status_data[1]["submitted_id"] == test_resource2["id"]
    assert UUID(status_data[1]["id"])  # Check if the ID is a valid UUID
    assert status_data[1]["success"] == "created"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_with_random_string_in_id_field_fails(
    socketio_test_client,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = copy.deepcopy(many_test_demo_resources[1])
    test_resource["id"] = "random_string"

    status_data = []
    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        await connection["client"].emit(
            "submit", test_resource, namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        status_data = connection["responses"]["/demo-resource"]["status"]

        await connection["client"].disconnect()

    assert status_data[0]["error"] == "badly formed hexadecimal UUID string"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation_missing_name(
    socketio_test_client,
):
    """Test the demo resource delete event."""

    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        statuses_data = connection["responses"]["/demo-resource"]["status"]

        await connection["client"].emit(
            "submit",
            {"description": "Description of test resource"},
            namespace="/demo-resource",
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert (
            statuses_data[0]["error"]
            == "1 validation error for DemoResourceCreate\nname\n  Field required [type=missing, input_value={'description': 'Description of test resource'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing"
        )

        await connection["client"].disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_resource_with_nonexisting_uuid_fails(
    socketio_test_client,
):
    """Test the demo resource submit event with non-existing UUID."""

    async for connection in socketio_test_client(client_config_demo_resource_namespace):
        statuses_data = connection["responses"]["/demo-resource"]["status"]

        test_demo_resource = copy.deepcopy(many_test_demo_resources[1])
        # test_demo_resource = many_test_demo_resources[1]
        test_demo_resource["id"] = str(uuid4())  # Set a non-existing UUID

        await connection["client"].emit(
            "submit", test_demo_resource, namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert statuses_data[0]["error"] == "404: DemoResource not updated."

        await connection["client"].disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_write_socketio], [session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_submits_existing_resource_for_update(
    current_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    current_user_from_session_id,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(current_token_payload())

    index_of_resource_to_update = next(
        i for i, r in enumerate(resources) if r.name == "A second cat 2 resource"
    )

    async for connection in socketio_test_client(client_config_demo_resource_namespace):
        statuses_data = connection["responses"]["/demo-resource"]["status"]

        modified_demo_resource = resources[index_of_resource_to_update]
        modified_demo_resource.name = "Altering the name of this demo resource"
        modified_demo_resource.language = "fr-FR"
        modified_demo_resource.id = str(modified_demo_resource.id)
        if modified_demo_resource.category_id:
            modified_demo_resource.category_id = str(modified_demo_resource.category_id)

        await connection["client"].emit(
            "submit", modified_demo_resource.model_dump(), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert UUID(statuses_data[0]["id"])  # Check if the ID is a valid UUID
        assert statuses_data[0]["success"] == "updated"
        assert statuses_data[0]["id"] == str(resources[index_of_resource_to_update].id)

        await connection["client"].disconnect()

    async with DemoResourceCRUD() as crud:
        current_user = await current_user_from_session_id()
        updated_resource = await crud.read_by_id(
            resources[index_of_resource_to_update].id, current_user
        )

        assert (
            updated_resource.description
            == resources[index_of_resource_to_update].description
        )
        assert updated_resource.category_id == UUID(
            resources[index_of_resource_to_update].category_id
        )
        assert updated_resource.tags == resources[index_of_resource_to_update].tags
        assert updated_resource.name == "Altering the name of this demo resource"
        assert updated_resource.language == "fr-FR"
        assert updated_resource.id == UUID(resources[index_of_resource_to_update].id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [session_id_admin_read_socketio],
        [session_id_user1_read_socketio],
    ],
    indirect=True,
)
async def test_user_updates_demo_resource_missing_write_scope_in_token_fails(
    current_user_from_session_id,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await current_user_from_session_id()

    if "Admin" not in current_user.azure_token_roles:
        policy = {
            "resource_id": resources[3].id,
            "identity_id": current_user.user_id,
            "action": "write",
        }
        await add_test_policy_for_resource(policy)

    async for connection in socketio_test_client(client_config_demo_resource_namespace):
        status_data = connection["responses"]["/demo-resource"]["status"]

        modified_demo_resource = resources[3]
        modified_demo_resource.name = "Altering the name of this demo resource"
        modified_demo_resource.language = "fr-FR"
        modified_demo_resource.id = str(modified_demo_resource.id)
        if modified_demo_resource.category_id:
            modified_demo_resource.category_id = str(modified_demo_resource.category_id)

        await connection["client"].emit(
            "submit", modified_demo_resource.model_dump(), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert status_data[0]["error"] == "401: Invalid token."

        # Connection is still open, so disconnection_result should be None
        disconnection_result = await connection["client"].disconnect()
        assert disconnection_result is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_user_updates_demo_resource_not_having_write_access_fails(
    current_user_from_session_id,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await current_user_from_session_id()

    policy = {
        "resource_id": resources[3].id,
        "identity_id": current_user.user_id,
        "action": "read",
    }
    await add_test_policy_for_resource(policy)

    async for connection in socketio_test_client(client_config_demo_resource_namespace):
        statuses_data = connection["responses"]["/demo-resource"]["status"]

        modified_demo_resource = resources[3]
        modified_demo_resource.name = "Altering the name of this demo resource"
        modified_demo_resource.language = "fr-FR"
        modified_demo_resource.id = str(modified_demo_resource.id)
        if modified_demo_resource.category_id:
            modified_demo_resource.category_id = str(modified_demo_resource.category_id)

        await connection["client"].emit(
            "submit", modified_demo_resource.model_dump(), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert statuses_data[0]["error"] == "404: DemoResource not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_one_client_deletes_a_demo_resource_and_another_client_from_same_user_gets_the_remove_event(
    current_token_payload,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(current_token_payload())

    # Two clients from same user - coming from current_token_payload()!
    async for connection1 in socketio_test_client(
        client_config_demo_resource_namespace
    ):
        async for connection2 in socketio_test_client(
            client_config_demo_resource_namespace
        ):

            deleted_data_client1 = []
            statuses_data_client1 = []
            deleted_data_client2 = []
            statuses_data_client2 = []

            statuses_data_client1 = connection1["responses"]["/demo-resource"]["status"]
            statuses_data_client2 = connection2["responses"]["/demo-resource"]["status"]
            deleted_data_client1 = connection1["responses"]["/demo-resource"]["deleted"]
            deleted_data_client2 = connection2["responses"]["/demo-resource"]["deleted"]

            await connection1["client"].emit(
                "delete", str(resources[2].id), namespace="/demo-resource"
            )

            # Wait for the response to be set
            await connection1["client"].sleep(1)
            await connection2["client"].sleep(1)

            assert deleted_data_client1 == [str(resources[2].id)]
            assert statuses_data_client1 == [
                {"success": "deleted", "id": str(resources[2].id)}
            ]
            assert deleted_data_client2 == [str(resources[2].id)]
            assert statuses_data_client2 == []

            await connection1["client"].disconnect()
            await connection2["client"].disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [
            session_id_user1_read_write_socketio,
            session_id_user2_read_socketio,
            session_id_admin_read_socketio,
        ]
    ],
    indirect=True,
)
async def test_one_client_deletes_a_demo_resource_and_another_client_with_different_user_gets_the_deleted_event(
    current_token_payload,
    current_user_from_session_id,
    add_test_policy_for_resource,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(current_token_payload())

    other_user = await current_user_from_session_id(1)
    policy = {
        "resource_id": resources[3].id,
        "identity_id": other_user.user_id,
        "action": "read",
    }
    # Creating user (first user) shares the resource with other user
    await add_test_policy_for_resource(policy, current_token_payload(0))

    # Two clients from different users
    async for connection1 in socketio_test_client(
        client_config_demo_resource_namespace
    ):
        async for connection2 in socketio_test_client(
            client_config_demo_resource_namespace
        ):
            async for connection_admin in socketio_test_client(
                client_config_demo_resource_namespace
            ):

                statuses_data_client1 = connection1["responses"]["/demo-resource"][
                    "status"
                ]
                statuses_data_client2 = connection2["responses"]["/demo-resource"][
                    "status"
                ]
                # statuses_data_admin = connection_admin["responses"]["/demo-resource"][
                #     "status"
                # ]
                deleted_data_client1 = connection1["responses"]["/demo-resource"][
                    "deleted"
                ]
                deleted_data_client2 = connection2["responses"]["/demo-resource"][
                    "deleted"
                ]
                # deleted_data_admin = connection_admin["responses"]["/demo-resource"][
                #     "deleted"
                # ]

                await connection1["client"].emit(
                    "delete", str(resources[2].id), namespace="/demo-resource"
                )

                # Wait for the response to be set
                await connection1["client"].sleep(1)
                await connection2["client"].sleep(1)

                assert deleted_data_client1 == [str(resources[2].id)]
                assert statuses_data_client1 == [
                    {"success": "deleted", "id": str(resources[2].id)}
                ]
                assert deleted_data_client2 == [str(resources[2].id)]
                assert statuses_data_client2 == []
                # Admin always gets the delete event:
                # TBD: think about it and fix this!
                # assert deleted_data_admin == [str(resources[2].id)]
                # assert statuses_data_admin == [
                #     {"success": "deleted", "id": str(resources[2].id)}
                # ]
                # assert 0

                await connection1["client"].disconnect()
                await connection2["client"].disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_admin_read_socketio], [session_id_user1_read_socketio]],
    indirect=True,
)
async def test_user_deletes_a_demo_resource_missing_write_scope_in_token(
    current_token_payload,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(current_token_payload())

    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        statuses_data = connection["responses"]["/demo-resource"]["status"]
        deleted_data = connection["responses"]["/demo-resource"]["deleted"]

        await connection["client"].emit(
            "delete", str(resources[2].id), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert deleted_data == []
        assert statuses_data == [{"error": "401: Invalid token."}]

        disconnection_result = await connection["client"].disconnect()

        assert disconnection_result is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [[session_id_user1_read_write_socketio]],
    indirect=True,
)
async def test_client_tries_to_delete_demo_resource_without_owner_rights_fails_and_returns_status(
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)

    async for connection in socketio_test_client(client_config_demo_resource_namespace):

        status_data = connection["responses"]["/demo-resource"]["status"]

        await connection["client"].emit(
            "delete", str(resources[2].id), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await connection["client"].sleep(1)

        assert status_data[0] == {"error": "404: DemoResource not deleted."}

        await connection["client"].disconnect()


# Testing the share events:

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# ✔︎ user shares a resource with a group: success
# ✔︎ user owning resource updates access to a different action level: success
# ✔︎ user owning resource updates access to same action level: error
# - user deletes access to a resource: success
#   includes:
#   - user has access to resource: success & transfer data
#   - user does not have access to resource: error
# ✔︎ user tries to share a resource, that the user does not own: error


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
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
    current_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    # First user owns the resources:
    token_user1 = current_token_payload(0)
    query_parameters_user1 = {}
    if "groups" in token_user1:
        identity_ids_user1 = [identity_id for identity_id in token_user1["groups"]]
        query_parameters_user1 = {"identity-id": ",".join(identity_ids_user1)}

    token_user2 = current_token_payload(1)
    query_parameters_user2 = {}
    if "groups" in token_user2:
        identity_ids_user2 = [identity_id for identity_id in token_user2["groups"]]
        query_parameters_user2 = {"identity-id": ",".join(identity_ids_user2)}

    token_user3 = current_token_payload(2)
    query_parameters_user3 = {}
    if "groups" in token_user3:
        identity_ids_user3 = [identity_id for identity_id in token_user3["groups"]]
        query_parameters_user3 = {"identity-id": ",".join(identity_ids_user3)}

    resources = await add_test_demo_resources(token_user1)
    # resources = await add_test_demo_resources(token_admin_read_write_socketio)

    async for connection1 in socketio_test_client(
        client_config_demo_resource_namespace,
        query_parameters=query_parameters_user1,
    ):
        status_data1 = connection1["responses"]["/demo-resource"]["status"]
        client1 = connection1["client"]
        async for connection2 in socketio_test_client(
            client_config_demo_resource_namespace,
            1,
            query_parameters=query_parameters_user2,
        ):
            status_data2 = connection2["responses"]["/demo-resource"]["status"]

            client2 = connection2["client"]

            async for connection3 in socketio_test_client(
                client_config_demo_resource_namespace,
                2,
                query_parameters=query_parameters_user3,
            ):
                status_data3 = connection3["responses"]["/demo-resource"]["status"]
                client3 = connection3["client"]

                # First user shares the resources with a group, that first and second user are member of:
                await client1.emit(
                    "share",
                    {
                        "resource_id": str(resources[0].id),
                        "identity_id": token_user1["groups"][1],
                        "action": "read",
                    },
                    namespace="/demo-resource",
                )

                # Wait for the response to be set
                await client1.sleep(1)
                await client2.sleep(1)
                await client3.sleep(1)

                assert status_data1 == [
                    {"success": "shared", "id": str(resources[0].id)}
                ]
                assert status_data2 == [
                    {"success": "shared", "id": str(resources[0].id)}
                ]
                # Even the third user is admin, share events don't get emitted automatically to admin,
                # Anyways can see everything!
                # Unless the admin also has the team in the groups from token.
                assert status_data3 == []

                transfer_data1 = connection1["responses"]["/demo-resource"]["transfer"]
                transfer_data2 = connection2["responses"]["/demo-resource"]["transfer"]
                assert len(transfer_data1) == len(resources)
                # Even though the access has been granted, no resources are transferred yet.
                # User needs to make another emit to event read, to get the resource,
                # because other existing access policies might influence the access rights.
                assert len(transfer_data2) == 0

                await client1.disconnect()
                await client2.disconnect()
                await client3.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
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
async def test_user_updates_access_to_owned_resource_for_an_group_identity(
    current_token_payload,
    current_user_from_session_id,
    add_test_demo_resources: list[DemoResource],
    add_many_test_groups: list[Group],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
    socketio_test_client,
):
    """Test the demo resource connect event."""
    # First user owns the resources:
    token_user1 = current_token_payload(0)
    many_test_groups = await add_many_test_groups()
    common_group_id = many_test_groups[2].id
    query_parameters_user1 = {"identity-id": str(common_group_id)}
    query_parameters_user2 = {"identity-id": str(common_group_id)}

    current_user1 = await current_user_from_session_id(0)
    current_user2 = await current_user_from_session_id(1)

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

    async for connection1 in socketio_test_client(
        client_config_demo_resource_namespace,
        query_parameters=query_parameters_user1,
    ):
        status_data1 = connection1["responses"]["/demo-resource"]["status"]
        client1 = connection1["client"]
        async for connection2 in socketio_test_client(
            client_config_demo_resource_namespace,
            1,
            query_parameters=query_parameters_user2,
        ):
            status_data2 = connection2["responses"]["/demo-resource"]["status"]

            client2 = connection2["client"]

            async for connection3 in socketio_test_client(
                client_config_demo_resource_namespace,
                2,
            ):
                status_data3 = connection3["responses"]["/demo-resource"]["status"]
                client3 = connection3["client"]

                # First user shares the resources with a group, that first and second user are member of:
                await client1.emit(
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
                await client1.sleep(1)
                await client2.sleep(1)
                await client3.sleep(1)

                assert status_data1 == [
                    {"success": "shared", "id": str(resources[1].id)}
                ]
                assert status_data2 == [
                    {"success": "shared", "id": str(resources[1].id)}
                ]
                # Even the third user is admin, share events don't get emitted automatically to admin,
                # Anyways can see everything!
                # Unless the admin also has the team in the groups from token.
                assert status_data3 == []

                transfer_data1 = connection1["responses"]["/demo-resource"]["transfer"]
                transfer_data2 = connection2["responses"]["/demo-resource"]["transfer"]
                assert len(transfer_data1) == len(resources)
                # Group had access before, so user2 got the resource on_connect:
                assert len(transfer_data2) == 1

                await client1.disconnect()
                await client2.disconnect()
                await client3.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
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
async def test_user_updates_access_to_owned_resource_for_an_group_identity_to_same_access(
    current_token_payload,
    current_user_from_session_id,
    add_test_demo_resources: list[DemoResource],
    add_many_test_groups: list[Group],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
    socketio_test_client,
):
    """Test the demo resource connect event."""
    # First user owns the resources:
    token_user1 = current_token_payload(0)
    many_test_groups = await add_many_test_groups()
    common_group_id = many_test_groups[2].id
    query_parameters_user1 = {"identity-id": str(common_group_id)}
    query_parameters_user2 = {"identity-id": str(common_group_id)}

    current_user1 = await current_user_from_session_id(0)
    current_user2 = await current_user_from_session_id(1)

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

    async for connection1 in socketio_test_client(
        client_config_demo_resource_namespace,
        query_parameters=query_parameters_user1,
    ):
        status_data1 = connection1["responses"]["/demo-resource"]["status"]
        client1 = connection1["client"]
        async for connection2 in socketio_test_client(
            client_config_demo_resource_namespace,
            1,
            query_parameters=query_parameters_user2,
        ):
            status_data2 = connection2["responses"]["/demo-resource"]["status"]

            client2 = connection2["client"]

            async for connection3 in socketio_test_client(
                client_config_demo_resource_namespace,
                2,
            ):
                status_data3 = connection3["responses"]["/demo-resource"]["status"]
                client3 = connection3["client"]

                # First user shares the resources with a group, that first and second user are member of:
                await client1.emit(
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
                await client1.sleep(1)
                await client2.sleep(1)
                await client3.sleep(1)

                assert status_data1 == [{"error": "404: Access policy not found."}]
                assert status_data2 == []
                # Even the third user is admin, share events don't get emitted automatically to admin,
                # Anyways can see everything!
                # Unless the admin also has the team in the groups from token.
                assert status_data3 == []

                transfer_data1 = connection1["responses"]["/demo-resource"]["transfer"]
                transfer_data2 = connection2["responses"]["/demo-resource"]["transfer"]
                assert len(transfer_data1) == len(resources)
                # Group had access before, so user2 got the resource on_connect:
                assert len(transfer_data2) == 1

                await client1.disconnect()
                await client2.disconnect()
                await client3.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
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
    current_token_payload,
    current_user_from_session_id,
    add_test_demo_resources: list[DemoResource],
    add_many_test_groups: list[Group],
    add_one_parent_child_identity_relationship,
    add_one_test_access_policy,
    socketio_test_client,
):
    """Test the demo resource connect event."""
    # First user owns the resources:
    token_user1 = current_token_payload(0)
    many_test_groups = await add_many_test_groups()
    common_group_id = many_test_groups[2].id
    query_parameters_user1 = {"identity-id": str(common_group_id)}
    query_parameters_user2 = {"identity-id": str(common_group_id)}

    current_user1 = await current_user_from_session_id(0)
    current_user2 = await current_user_from_session_id(1)

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

    async for connection1 in socketio_test_client(
        client_config_demo_resource_namespace,
        query_parameters=query_parameters_user1,
    ):
        status_data1 = connection1["responses"]["/demo-resource"]["status"]
        client1 = connection1["client"]
        async for connection2 in socketio_test_client(
            client_config_demo_resource_namespace,
            1,
            query_parameters=query_parameters_user2,
        ):
            status_data2 = connection2["responses"]["/demo-resource"]["status"]

            client2 = connection2["client"]

            async for connection3 in socketio_test_client(
                client_config_demo_resource_namespace,
                2,
            ):
                status_data3 = connection3["responses"]["/demo-resource"]["status"]
                client3 = connection3["client"]

                # First user shares the resources with a group, that first and second user are member of:
                await client1.emit(
                    "share",
                    {
                        "resource_id": str(resources[1].id),
                        "identity_id": str(common_group_id),
                    },
                    namespace="/demo-resource",
                )

                # Wait for the response to be set
                await client1.sleep(1)
                await client2.sleep(1)
                await client3.sleep(1)

                await client1.emit(
                    "read",
                    str(resources[1].id),
                    namespace="/demo-resource",
                )

                await client1.sleep(1)
                await client2.sleep(1)

                await client2.emit(
                    "read",
                    str(resources[1].id),
                    namespace="/demo-resource",
                )

                await client1.sleep(1)
                await client2.sleep(1)

                assert status_data1 == [
                    {"success": "unshared", "id": str(resources[1].id)}
                ]
                # After read event, triggered by unshare, user2 has no longer access:
                assert status_data2 == [
                    {"success": "unshared", "id": str(resources[1].id)},
                    {"success": "deleted", "id": str(resources[1].id)},
                    {"error": f"Resource {str(resources[1].id)} not found."},
                ]
                # Even the third user is admin, share events don't get emitted automatically to admin,
                # Anyways can see everything!
                # Unless the admin also has the team in the groups from token.
                assert status_data3 == []

                transfer_data1 = connection1["responses"]["/demo-resource"]["transfer"]
                transfer_data2 = connection2["responses"]["/demo-resource"]["transfer"]
                # user one gets the resource again after the unshare event
                # still has access from own access policy:
                assert len(transfer_data1) == len(resources) + 1
                # Group had access before, so user2 got the resource on_connect:
                assert len(transfer_data2) == 1

                await client1.disconnect()
                await client2.disconnect()
                await client3.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "session_id_selector",
    [
        [session_id_user1_read_write_socketio_groups],
        [session_id_user2_read_write_socketio_groups],
    ],
    indirect=True,
)
async def test_user_shares_tries_to_share_resource_without_having_access(
    current_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    # First user owns the resources:

    resources = await add_test_demo_resources(token_admin_read_write_socketio)

    token_user1 = current_token_payload(0)
    async for connection in socketio_test_client(
        client_config_demo_resource_namespace,
    ):
        status_data = connection["responses"]["/demo-resource"]["status"]
        client = connection["client"]

        # First user shares the resources with a group, that first and second user are member of:
        await client.emit(
            "share",
            {
                "resource_id": str(resources[0].id),
                "identity_id": token_user1["groups"][1],
                "action": "read",
            },
            namespace="/demo-resource",
        )

        # Wait for the response to be set
        await client.sleep(1)

        assert status_data == [{"error": "403: Forbidden."}]
        transfer_data = connection["responses"]["/demo-resource"]["transfer"]

        assert len(transfer_data) == 0
        await client.disconnect()
