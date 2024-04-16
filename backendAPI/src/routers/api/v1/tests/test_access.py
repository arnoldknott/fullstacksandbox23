import pytest
from httpx import AsyncClient
from fastapi import FastAPI

# from models.access import AccessPolicy
from tests.utils import (
    token_admin,
    token_admin_read,
    token_admin_read_write,
    token_user1_read,
    token_user1_read_write,
    token_user2_read,
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


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_admin_read],
    indirect=True,
)
async def test_admin_gets_access_policies(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

    policies_in_database = add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policies")

    assert response.status_code == 200
    content = response.json()
    assert (
        len(content) == len(many_test_policies) + 1
    )  # +1 for the user policy created, when the user accesses endpoint
    for content, policy in zip(content, policies_in_database):
        assert content["id"] == str(policy.id)
        assert content["resource_id"] == str(policy.resource_id)
        assert content["resource_type"] == policy.resource_type
        assert content["identity_id"] == (
            str(policy.identity_id) if policy.identity_id else None
        )
        assert content["identity_type"] == policy.identity_type
        assert content["action"] == policy.action
        assert content["public"] == policy.public


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user1_read_write,
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_users_get_all_access_policies_fails(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

    policies_in_database = add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policies")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}
