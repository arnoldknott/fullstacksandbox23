from datetime import datetime
from uuid import UUID, uuid4

from socketio.exceptions import ConnectionError
from unittest.mock import patch
import pytest

from tests.utils import many_test_demo_resources
from models.access import AccessPolicy
from models.demo_resource import DemoResource, DemoResourceExtended
from crud.demo_resource import DemoResourceCRUD
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from tests.utils import (
    token_admin_read_write_socketio,
    token_user1_read_write_socketio,
    token_admin_read,
    token_admin_write,
    token_user1_read,
    token_user1_write,
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


@pytest.fixture(scope="module", autouse=True)
async def setup_namespace_server(provide_namespace_server):
    # Call setup function here
    socket_io_server = await provide_namespace_server(
        [DemoResourceNamespace("/demo-resource")]
    )
    # Yield to allow tests to run
    yield
    # Optionally, add teardown logic here if needed
    await socket_io_server.shutdown()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read, token_admin_write, token_user1_read, token_user1_write],
    # [token_admin_read_write_socketio, token_user1_read_write_socketio],# actually connects to the namespace!
    indirect=True,
)
async def test_demo_resource_namespace_fails_to_connect_when_socketio_scope_is_missing_in_token(
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo_resource_namespace socket.io connection needs socketio scope in token."""

    try:
        async for client in socketio_test_client(["/demo-resource"]):

            await client.connect_to_test_client()

            await client.sleep(1)
            await client.disconnect()
            raise Exception(
                "This should have failed due to missing authentication in on_connect."
            )
    except ConnectionError as err:
        assert str(err) == "One or more namespaces failed to connect"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_owner_connects_to_demo_resource_namespace_and_gets_all_demoresources(
    mock_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    mocked_token_payload = mock_token_payload
    resources = await add_test_demo_resources(mocked_token_payload)

    responses = []
    async for client in socketio_test_client(["/demo-resource"]):

        @client.on("transfer", namespace="/demo-resource")
        async def receiving_transfer(data):
            nonlocal responses
            responses.append(data)

        await client.connect_to_test_client()

    assert len(responses) == 4
    for response, resource in zip(responses, resources):
        assert "category" in response
        assert "tags" in response
        assert DemoResource.model_validate(response) == resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_connects_to_demo_resource_namespace_and_gets_allowed_demoresources(
    mock_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
    current_user_from_azure_token,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await current_user_from_azure_token(mock_token_payload)

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

    responses = []
    async for client in socketio_test_client(["/demo-resource"]):

        @client.on("transfer", namespace="/demo-resource")
        async def receiving_transfer(data):
            nonlocal responses
            responses.append(data)

    await client.connect_to_test_client()

    resources_with_user_acccess = [
        resources[1],  # Read access
        resources[3],  # Write access
    ]

    assert len(responses) == 2
    for response, resource in zip(responses, resources_with_user_acccess):
        assert "category" in response
        assert "tags" in response
        assert "user_right" not in response
        assert "access_policies" not in response
        assert "created_at" not in response
        assert "last_modified_at" not in response
        assert DemoResource.model_validate(response) == resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_connects_to_demo_resource_namespace_and_gets_allowed_demoresources_with_access_data(
    mock_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
    current_user_from_azure_token,
):
    """Test the demo resource connect event."""
    time_before_creation = datetime.now()
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    time_after_creation = datetime.now()
    current_user = await current_user_from_azure_token(mock_token_payload)

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

    responses = []

    async for client in socketio_test_client(["/demo-resource"]):

        @client.on("transfer", namespace="/demo-resource")
        async def receiving_transfer(data):
            nonlocal responses
            responses.append(data)

        await client.connect_to_test_client(
            query_parameters={"request-access-data": "true"}
        )

    resources_with_user_acccess = [
        resources[1],  # Own access
        resources[3],  # Write access
    ]

    assert len(responses) == 2
    for response, resource in zip(responses, resources_with_user_acccess):
        modelled_response = DemoResourceExtended.model_validate(response)
        assert "category" in response
        assert "tags" in response
        assert modelled_response.creation_date >= time_before_creation
        assert modelled_response.creation_date <= time_after_creation
        assert modelled_response.last_modified_date == modelled_response.creation_date
        assert DemoResource.model_validate(response) == resource

    assert responses[0]["user_right"] == "own"
    assert "id" in responses[0]["access_policies"][1]
    assert (
        UUID(responses[0]["access_policies"][1]["identity_id"])
        == policies[0]["identity_id"]
    )
    assert (
        UUID(responses[0]["access_policies"][1]["resource_id"])
        == policies[0]["resource_id"]
    )
    assert responses[0]["access_policies"][1]["action"] == "own"
    assert not responses[0]["access_policies"][1]["public"]
    assert responses[1]["user_right"] == "write"
    assert responses[1]["access_policies"] is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_gets_error_on_status_event_due_to_database_error(
    mock_token_payload, socketio_test_client
):
    """Test the demo resource connect event."""
    with patch(
        "crud.demo_resource.DemoResourceCRUD.read",
        side_effect=Exception("Database error."),
    ):

        resources = []
        statuses = []

        async for client in socketio_test_client(["/demo-resource"]):

            @client.event(namespace="/demo-resource")
            async def transfer(data):
                nonlocal resources
                resources.append(data)

            @client.event(namespace="/demo-resource")
            async def status(data):

                nonlocal statuses
                statuses.append(data)

            await client.connect_to_test_client()

        # Wait for the response to be set
        await client.sleep(1)

        assert resources == []
        assert statuses == [{"error": "Database error."}]

        await client.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation(
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo resource submit event without ID."""

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        await client.emit(
            "submit", many_test_demo_resources[1], namespace="/demo-resource"
        )

        # Wait for the response to be set
        await client.sleep(1)

        # assert "id" in status[0]
        assert statuses[0]["submitted_id"] is None
        assert UUID(statuses[0]["id"])  # Check if the ID is a valid UUID
        assert statuses[0]["success"] == "created"

        await client.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_submits_resource_with_new__string_in_id_field_for_creation(
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = many_test_demo_resources[1]
    test_resource["id"] = "new_34ab56z"

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        await client.emit("submit", test_resource, namespace="/demo-resource")

        # Wait for the response to be set
        await client.sleep(1)

        # assert "id" in status[0]
        assert statuses[0]["submitted_id"] == test_resource["id"]
        assert UUID(statuses[0]["id"])  # Check if the ID is a valid UUID
        assert statuses[0]["success"] == "created"

        await client.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_submits_resource_with_random_string_in_id_field_fails(
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo resource submit event with non-UUID in ID field."""

    test_resource = many_test_demo_resources[1]
    test_resource["id"] = "random_string"

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        await client.emit("submit", test_resource, namespace="/demo-resource")

        # Wait for the response to be set
        await client.sleep(1)

        assert statuses[0]["error"] == "badly formed hexadecimal UUID string"

        await client.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_submits_resource_without_id_for_creation_missing_name(
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo resource delete event."""

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        await client.emit(
            "submit",
            {"description": "Description of test resource"},
            namespace="/demo-resource",
        )

        # Wait for the response to be set
        await client.sleep(1)

        assert (
            statuses[0]["error"]
            == "1 validation error for DemoResourceCreate\nname\n  Field required [type=missing, input_value={'description': 'Description of test resource'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing"
        )

        await client.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_submits_resource_with_nonexisting_uuid_fails(
    mock_token_payload,
    provide_namespace_server,
    socketio_test_client,
):
    """Test the demo resource submit event with non-existing UUID."""

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        test_demo_resource = many_test_demo_resources[1]
        test_demo_resource["id"] = str(uuid4())  # Set a non-existing UUID

        await client.emit("submit", test_demo_resource, namespace="/demo-resource")

        # Wait for the response to be set
        await client.sleep(1)

        assert statuses[0]["error"] == "404: DemoResource not updated."

        await client.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_submits_existing_resource_for_update(
    mock_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    current_user_from_azure_token,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(mock_token_payload)

    index_of_resource_to_update = next(
        i for i, r in enumerate(resources) if r.name == "A second cat 2 resource"
    )

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        modified_demo_resource = resources[index_of_resource_to_update]
        modified_demo_resource.name = "Altering the name of this demo resource"
        modified_demo_resource.language = "fr-FR"
        modified_demo_resource.id = str(modified_demo_resource.id)
        if modified_demo_resource.category_id:
            modified_demo_resource.category_id = str(modified_demo_resource.category_id)

        await client.emit(
            "submit", modified_demo_resource.model_dump(), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await client.sleep(1)

        assert UUID(statuses[0]["id"])  # Check if the ID is a valid UUID
        assert statuses[0]["success"] == "updated"
        assert statuses[0]["id"] == str(resources[index_of_resource_to_update].id)

        await client.disconnect()

    async with DemoResourceCRUD() as crud:
        current_user = await current_user_from_azure_token(mock_token_payload)
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
    "mock_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_user_updates_demo_resource_not_having_write_access_fails(
    mock_token_payload,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
    current_user_from_azure_token,
):
    """Test the demo resource connect event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)
    current_user = await current_user_from_azure_token(mock_token_payload)

    policy = {
        "resource_id": resources[3].id,
        "identity_id": current_user.user_id,
        "action": "read",
    }
    await add_test_policy_for_resource(policy)

    async for client in socketio_test_client(["/demo-resource"]):
        statuses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal statuses
            statuses.append(data)

        await client.connect_to_test_client()

        modified_demo_resource = resources[3]
        modified_demo_resource.name = "Altering the name of this demo resource"
        modified_demo_resource.language = "fr-FR"
        modified_demo_resource.id = str(modified_demo_resource.id)
        if modified_demo_resource.category_id:
            modified_demo_resource.category_id = str(modified_demo_resource.category_id)

        await client.emit(
            "submit", modified_demo_resource.model_dump(), namespace="/demo-resource"
        )

        # Wait for the response to be set
        await client.sleep(1)

        assert statuses[0]["error"] == "404: DemoResource not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_one_client_deletes_a_demo_resource_and_another_client_gets_the_remove_event(
    mock_token_payload,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(mock_token_payload)

    async for client1 in socketio_test_client(["/demo-resource"]):
        async for client2 in socketio_test_client(["/demo-resource"]):

            responses_client1 = []
            statuses_client1 = []
            responses_client2 = []
            statuses_client2 = []

            @client1.event(namespace="/demo-resource")
            async def deleted(data):

                nonlocal responses_client1
                responses_client1.append(data)

            @client1.event(namespace="/demo-resource")
            async def status(data):

                nonlocal statuses_client1
                statuses_client1.append(data)

            @client2.event(namespace="/demo-resource")
            async def deleted(data):  # NOQA: F811

                nonlocal responses_client2
                responses_client2.append(data)

            @client2.event(namespace="/demo-resource")
            async def status(data):  # NOQA: F811

                nonlocal statuses_client2
                statuses_client2.append(data)

            await client1.connect_to_test_client()
            await client2.connect_to_test_client()

            await client1.emit(
                "delete", str(resources[2].id), namespace="/demo-resource"
            )

            # Wait for the response to be set
            await client1.sleep(1)
            await client2.sleep(1)

            assert responses_client1 == [str(resources[2].id)]
            assert statuses_client1 == [
                {"success": "deleted", "id": str(resources[2].id)}
            ]
            assert responses_client2 == [str(resources[2].id)]
            assert statuses_client2 == []

            await client1.disconnect()
            await client2.disconnect()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_client_tries_to_delete_demo_resource_without_owner_rights_fails_and_returns_status(
    mock_token_payload,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)

    async for client in socketio_test_client(["/demo-resource"]):

        responses = []

        @client.event(namespace="/demo-resource")
        async def status(data):

            nonlocal responses
            responses = data

        await client.connect_to_test_client()

        await client.emit("delete", str(resources[2].id), namespace="/demo-resource")

        # Wait for the response to be set
        await client.sleep(1)

        assert responses == {"error": "404: DemoResource not deleted."}

        await client.disconnect()
