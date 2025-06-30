from datetime import datetime
from uuid import UUID
from socketio.exceptions import ConnectionError
from unittest.mock import patch
import pytest
import socketio

from tests.utils import many_test_demo_resources
from models.access import AccessPolicy
from models.demo_resource import DemoResource, DemoResourceExtended
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from tests.utils import (
    token_admin_read_write_socketio,
    token_user1_read_write_socketio,
    token_admin_read,
    token_admin_write,
    token_user1_read,
    token_user1_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read, token_admin_write, token_user1_read, token_user1_write],
    # [token_admin_read_write_socketio, token_user1_read_write_socketio],# actually connects to the namespace!
    indirect=True,
)
async def test_demo_resource_namespace_fails_to_connect_when_socketio_scope_is_missing_in_token(
    provide_namespace_server,
    mock_token_payload,
    socketio_test_client,
):
    """Test the demo_resource_namespace socket.io connection needs socketio scope in token."""

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])
    # statuses = []
    try:
        async for client in socketio_test_client(["/demo-resource"]):

            await client.connect_to_test_client()

            await client.sleep(1)
            # assert statuses == [{"error": "Authorization failed."}]
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
async def test_user_submits_resource_without_id(
    mock_token_payload,
    provide_namespace_server,
    socketio_test_client,
):
    """Test the demo resource delete event."""

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

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


# TBD:
# - user submits resource with mandatory data (here name) missing => error
# - user submits resources with a UUID that does not exist => error
# - user submits resource with a UUID that exists => update
# - user submits resource with a UUID that exists and has no write access => error


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_owner_connects_to_demo_resource_namespace_and_gets_all_demoresources(
    mock_token_payload,
    # TBD: refactor for the test_client to also create the test-server and provide the namespace server
    provide_namespace_server,
    socketio_test_client,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    mocked_token_payload = mock_token_payload
    resources = await add_test_demo_resources(mocked_token_payload)

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

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
    # TBD: refactor into test client to also create the test-server and
    # provide the namespace server
    provide_namespace_server,
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

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

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
    # TBD: refactor into test client to also create the test-server and
    #  provide the namespace server
    provide_namespace_server,
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

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

    responses = []

    async for client in socketio_test_client(["/demo-resource"]):

        @client.on("transfer", namespace="/demo-resource")
        async def receiving_transfer(data):
            nonlocal responses
            responses.append(data)

        await client.connect_to_test_client()

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
    mock_token_payload, provide_namespace_server, socketio_test_client
):
    """Test the demo resource connect event."""
    with patch(
        "crud.demo_resource.DemoResourceCRUD.read",
        side_effect=Exception("Database error."),
    ):
        await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

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
    [token_user1_read_write_socketio],
    indirect=True,
)
async def test_one_client_deletes_a_demo_resource_and_another_client_gets_the_remove_event(
    mock_token_payload,
    provide_namespace_server,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(mock_token_payload)

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

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
    provide_namespace_server,
    add_test_demo_resources: list[DemoResource],
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(token_admin_read_write_socketio)

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

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
