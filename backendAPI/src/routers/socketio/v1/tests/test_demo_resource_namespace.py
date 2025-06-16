import pytest
import socketio

from models.access import AccessPolicy
from models.demo_resource import DemoResource
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
        auth={"session_id": "testsessionid"},
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
async def test_user_connects_to_demo_resource_namespace_and_gets_all_demoresources_with_access_rights(
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
            "resource_type": "DemoResource",
            "action": "read",
        },
        {
            "resource_id": resources[3].id,
            "identity_id": current_user.user_id,
            "resource_type": "DemoResource",
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
        auth={"session_id": "testsessionid"},
    )

    resources_with_user_acccess = [
        resources[1],  # Read access
        resources[3],  # Write access
    ]

    assert len(responses) == 2
    for response, resource in zip(responses, resources_with_user_acccess):
        assert "category" in response
        assert "tags" in response
        assert DemoResource.model_validate(response) == resource
