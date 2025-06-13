import pytest
import socketio

from models.demo_resource import DemoResource
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from tests.utils import (  # , token_user1_read_write_socketio
    token_admin_read_write_socketio,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mock_token_payload",
    [token_admin_read_write_socketio],
    indirect=True,
)
async def test_admin_connects_to_demo_resource_namespace_and_gets_all_demoresources(
    mock_token_payload, provide_namespace_server, add_test_demo_resources
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
        assert DemoResource.model_validate(response) == resource
