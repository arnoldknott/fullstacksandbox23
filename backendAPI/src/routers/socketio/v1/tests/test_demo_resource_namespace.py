from datetime import datetime
from uuid import UUID

import pytest
import socketio

from models.access import AccessPolicy
from models.demo_resource import DemoResource, DemoResourceExtended
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from tests.utils import (
    token_admin_read_write_socketio,
    token_user1_read_write_socketio,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio, token_user1_read_write_socketio],
    indirect=True,
)
async def test_owner_connects_to_demo_resource_namespace_and_gets_all_demoresources(
    mock_token_payload,
    provide_namespace_server,
    add_test_demo_resources: list[DemoResource],
):
    """Test the demo resource connect event."""
    mocked_token_payload = mock_token_payload
    resources = await add_test_demo_resources(mocked_token_payload)

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

    client = socketio.AsyncClient(logger=True, engineio_logger=True)

    responses = []

    @client.on("transfer", namespace="/demo-resource")
    async def receiving_transfer(data):
        nonlocal responses
        responses.append(data)

    await client.connect(
        "http://127.0.0.1:8669",
        socketio_path="socketio/v1",
        namespaces=["/demo-resource"],
        auth={"session-id": "testsessionid"},
    )

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
    provide_namespace_server,
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

    client = socketio.AsyncClient(logger=True, engineio_logger=True)

    responses = []

    @client.on("transfer", namespace="/demo-resource")
    async def receiving_transfer(data):
        nonlocal responses
        responses.append(data)

    await client.connect(
        "http://127.0.0.1:8669",
        socketio_path="socketio/v1",
        namespaces=["/demo-resource"],
        auth={"session-id": "testsessionid"},
    )

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
    provide_namespace_server,
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

    client = socketio.AsyncClient(logger=True, engineio_logger=True)

    responses = []

    @client.on("transfer", namespace="/demo-resource")
    async def receiving_transfer(data):
        nonlocal responses
        responses.append(data)

    await client.connect(
        "http://127.0.0.1:8669?request-access-data=true",
        socketio_path="socketio/v1",
        namespaces=["/demo-resource"],
        auth={"session-id": "testsessionid"},
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
async def test_one_client_deletes_a_demo_resource_and_another_client_gets_the_remove_event(
    mock_token_payload,
    provide_namespace_server,
    add_test_demo_resources: list[DemoResource],
    current_user_from_azure_token,
    add_test_policy_for_resource,
    socketio_test_client,
):
    """Test the demo resource delete event."""
    resources = await add_test_demo_resources(mock_token_payload)
    # current_user = await current_user_from_azusre_token(mock_token_payload)

    # policy = {
    #     "resource_id": resources[2].id,
    #     "identity_id": current_user.user_id,
    #     "action": "own",
    # }
    # await add_test_policy_for_resource(policy)

    await provide_namespace_server([DemoResourceNamespace("/demo-resource")])

    async for client1 in socketio_test_client(["/demo-resource"]):
        async for client2 in socketio_test_client(["/demo-resource"]):

            responses_client1 = []
            responses_client2 = []

            @client1.event(namespace="/demo-resource")
            async def remove(data):

                nonlocal responses_client1
                responses_client1 = data

            @client2.event(namespace="/demo-resource")
            async def remove(data):

                nonlocal responses_client2
                responses_client2 = data

            await client1.emit(
                "delete", str(resources[2].id), namespace="/demo-resource"
            )

            # Wait for the response to be set
            await client1.sleep(1)
            await client2.sleep(1)

            assert responses_client1 == str(resources[2].id)
            assert responses_client2 == str(resources[2].id)

            await client1.disconnect()
            await client2.disconnect()
