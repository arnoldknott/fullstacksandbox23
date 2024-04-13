import pytest
from httpx import AsyncClient
from fastapi import FastAPI

# from models.access import AccessPolicy
from tests.utils import (
    token_admin_read_write,
    token_user1_read_write,
    token_user2_read_write,
    many_test_policies,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_access_policies(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests POST access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    for policy in many_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)

        assert response.status_code == 201
        content = response.json()
        assert "id" in content
        assert content["resource_id"] == policy["resource_id"]
        assert content["resource_type"] == policy["resource_type"]
        if "identity_id" in policy:
            assert content["identity_id"] == policy["identity_id"]
        if "identity_type" in policy:
            assert content["identity_type"] == policy["identity_type"]
        assert content["action"] == policy["action"]
        if "public" in policy:
            assert content["public"] == policy["public"]
        else:
            assert content["public"] == False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_user2_read_write],
    indirect=True,
)
async def test_user_posts_access_policies(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests POST access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    for policy in many_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)

        # TBD: this should not be failing for resources, that the user owns
        # all other resources it should fail - so this test is good enough,
        # but more tests are needed.
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}
