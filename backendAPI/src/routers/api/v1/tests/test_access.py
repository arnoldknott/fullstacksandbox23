import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from uuid import uuid4

from pprint import pprint

from core.types import Action
from models.access import AccessPolicy
from tests.utils import (
    token_admin,
    token_admin_read,
    token_admin_write,
    token_admin_read_write,
    token_user1_read,
    token_user1_write,
    token_user1_read_write,
    token_user2_read,
    token_user2_write,
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
        # assert content["resource_type"] == policy["resource_type"]
        if "identity_id" in policy:
            assert content["identity_id"] == policy["identity_id"]
        # if "identity_type" in policy:
        # assert content["identity_type"] == policy["identity_type"]
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
        assert content["identity_id"] == (
            str(policy.identity_id) if policy.identity_id else None
        )
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
        token_admin,
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
    add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policies")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_admin_read_write,
        token_admin_read,
        # token_user1_read,
        # token_user2_read_write,
        # token_user2_read,
        # token_user2_read_write,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_for_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
    mocked_get_azure_token_payload,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    existing_policies = add_many_test_access_policies

    # print("=== mocked_get_azure_token_payload ===")
    # pprint(mocked_get_azure_token_payload)

    # print("=== existing_policies ===")
    # pprint([policy.model_dump() for policy in existing_policies])

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{str(existing_policies[2].resource_id)}"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 2

    for policy, existing_policy in zip(payload[:2], existing_policies[1:3]):
        modelled_policy = AccessPolicy.model_validate(policy)
        assert modelled_policy.id == existing_policy.id
        assert modelled_policy.resource_id == existing_policy.resource_id
        # assert modelled_policy.resource_type == existing_policy.resource_type
        assert modelled_policy.identity_id == (
            existing_policy.identity_id if existing_policy.identity_id else None
        )
        # assert modelled_policy.identity_type == existing_policy.identity_type
        assert modelled_policy.action == existing_policy.action
        assert modelled_policy.public == existing_policy.public


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
    mock_current_user,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid4())
    current_user = await mock_current_user(mocked_get_azure_token_payload)

    print("=== current_user ===")
    pprint(current_user)

    print("\n")

    # Access policies for the querying user - which is owner of resource:
    own_test_access_policy_for_current_user = {
        "resource_id": resource_id_for_query,
        "identity_id": current_user.user_id,
        "action": Action.own,
    }
    write_test_access_policy_for_current_user = {
        "resource_id": resource_id_for_query,
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": resource_id_for_query,
        "identity_id": current_user.user_id,
        "action": Action.read,
    }

    # Access policies for queried resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": resource_id_for_query,
        "action": Action.read,
        "public": True,
    }

    target_policies = [
        own_test_access_policy_for_current_user,
        write_test_access_policy_for_current_user,
        read_test_access_policy_for_current_user,
        own_test_access_policy_for_random_user,
        write_test_access_policy_for_random_user,
        read1_test_access_policy_for_random_user,
        read2_test_access_policy_for_random_user,
        read_public_test_access_policy,
    ]

    existing_policies_in_db = await add_test_access_policy(target_policies)

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{resource_id_for_query}"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == len(target_policies)

    for policy, target in zip(payload, existing_policies_in_db):
        received_policy = AccessPolicy.model_validate(policy)
        target_policy = AccessPolicy.model_validate(target)
        # print("=== received_policy ===")
        # pprint(received_policy.model_dump())
        # print("\n")
        # print("=== target_policy ===")
        # pprint(target_policy.model_dump())
        # print("\n")
        assert received_policy.id == target_policy.id
        assert received_policy.resource_id == target_policy.resource_id
        assert received_policy.identity_id == target_policy.identity_id
        assert received_policy.action == target_policy.action
        assert received_policy.public == target_policy.public


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_without_being_owner(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
    mock_current_user,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid4())
    current_user = await mock_current_user(mocked_get_azure_token_payload)

    print("=== current_user ===")
    pprint(current_user)

    print("\n")

    # Access policies for the querying user - which is missing owner rights of resource:
    write_test_access_policy_for_current_user = {
        "resource_id": resource_id_for_query,
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": resource_id_for_query,
        "identity_id": current_user.user_id,
        "action": Action.read,
    }

    # Access policies for queried resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": str(uuid4()),
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": resource_id_for_query,
        "action": Action.read,
        "public": True,
    }

    target_policies = [
        write_test_access_policy_for_current_user,
        read_test_access_policy_for_current_user,
        own_test_access_policy_for_random_user,
        write_test_access_policy_for_random_user,
        read1_test_access_policy_for_random_user,
        read2_test_access_policy_for_random_user,
        read_public_test_access_policy,
    ]

    await add_test_access_policy(target_policies)

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{resource_id_for_query}"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_admin,
        token_admin_write,
        token_user1_write,
        token_user2_write,
    ],
    indirect=True,
)
async def test_access_policies_for_resource_missing_read_scope(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET existing access policies for specific resource without read scope."""
    app_override_get_azure_payload_dependency
    existing_policies = add_many_test_access_policies

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{str(existing_policies[2].resource_id)}"
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}
