import pytest
from httpx import AsyncClient
from fastapi import FastAPI

import uuid

import warnings

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
    user_id_user2,
    user_id_user3,
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
        assert int(content["id"])
        assert content["resource_id"] == policy["resource_id"]
        if "identity_id" in policy:
            assert content["identity_id"] == policy["identity_id"]
        assert content["action"] == policy["action"]
        if "public" in policy:
            assert content["public"] == policy["public"]
        else:
            assert content["public"] is not False


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


# TBD. add tests creating access policy for non-existing identity fails.
# TBD. add tests creating access policy for non-existing resource fails.


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
    assert len(content) == len(many_test_policies)
    # +1 for the user policy created, when the user accesses endpoint - not any more?
    for content, policy in zip(content, policies_in_database):
        # TBD: add model verification of results and compare the verified model?
        assert content["id"] == policy.id
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
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    # with warnings.catch_warnings(record=True) as warn:

    app_override_get_azure_payload_dependency
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    # Access policies for the querying user - which is owner of resource:
    own_test_access_policy_for_current_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": current_user.user_id,
        "action": Action.own,
    }
    write_test_access_policy_for_current_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }

    # Access policies for queried resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user3,
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": uuid.UUID(resource_id_for_query),
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

    existing_policies_in_db = []
    for policy in target_policies:
        created_policy = await add_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

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
        # assert 0
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
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid.uuid4())

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    # Access policies for the querying user - which is missing owner rights of resource:
    write_test_access_policy_for_current_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": current_user.user_id,
        "action": Action.read,
    }

    # Access policies for queried resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": uuid.UUID(resource_id_for_query),
        "identity_id": user_id_user3,
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": uuid.UUID(resource_id_for_query),
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

    # await add_test_access_policy(target_policies)
    existing_policies_in_db = []
    for policy in target_policies:
        created_policy = await add_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

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
