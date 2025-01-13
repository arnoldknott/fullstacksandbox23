import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action, CurrentUserData, IdentityType, ResourceType
from crud.access import AccessPolicyCRUD
from models.access import AccessLogCreate, AccessLogRead, AccessPolicy, AccessPolicyRead
from models.demo_resource import DemoResource
from models.identity import AzureGroup, User
from models.protected_resource import ProtectedResource
from tests.utils import (
    azure_group_id1,
    azure_group_id2,
    azure_group_id3,
    azure_group_id4,
    current_user_data_admin,
    identity_id_user1,
    identity_id_user2,
    identity_id_user3,
    many_test_policies,
    resource_id1,
    resource_id2,
    resource_id3,
    resource_id9,
    token_admin,
    token_admin_read,
    token_admin_read_write,
    token_admin_write,
    token_user1_read,
    token_user1_read_write,
    token_user1_write,
    token_user2_read,
    token_user2_read_write,
    token_user2_write,
)

# region ## AccessPolicy tests:

# Note: There are also plenty of tests for the access CRUD!!

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# implement protected routes for:
# AccessPolicies:
# ✔︎ create (share with identity, i.e. user, group)
# ✔︎ create (public share)
# ✔︎ make a generic for the above two - checks are handled in model AccessPolicyCreate!
# ✔︎ read all (check who has access)
# ✔︎ read by resource_id - use filter
# ✔︎ read by resource_type - use filter - join with IdentifierTypeTable
# ✔︎ read by identity - use filter
# ✔︎ read by identity_type - use filter - join with IdentifierTypeTable (can wait)
# ✔︎ change access Action (own, write, read) -> use delete first and then create; but update model can be used: derive from Create and add new action!
# ✔︎ delete (unshare)

# region: ## POST tests:
# more detailed tests are done on CRUD level in test_access_crud.py


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_access_policies(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_current_users,
    register_many_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_provide_http_token_payload
    register_many_current_users
    register_many_resources

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
            assert content["public"] is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_access_policies_for_non_existing_resources(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_current_users,
    # register_many_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_provide_http_token_payload
    register_many_current_users

    for policy in many_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_non_public_access_policies_for_non_existing_identities(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_provide_http_token_payload
    register_many_resources

    private_test_policies = many_test_policies[0:9].copy()

    for policy in private_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_public_access_policies_for_non_existing_identities(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_provide_http_token_payload
    register_many_resources

    public_test_policy = many_test_policies[9].copy()

    response = await async_client.post("/api/v1/access/policy", json=public_test_policy)

    assert response.status_code == 201
    content = response.json()
    assert int(content["id"])
    assert content["resource_id"] == public_test_policy["resource_id"]
    assert content["identity_id"] is None
    assert content["action"] == public_test_policy["action"]
    assert content["public"] is True


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_with_owner_rights_posts_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
    register_one_identity,
):
    """Tests POST access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Give current user owner rights for the tested resource
    await add_one_test_access_policy(
        {
            "resource_id": many_test_policies[2]["resource_id"],
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        }
    )

    new_user_id = uuid.uuid4()
    await register_one_identity(new_user_id, User)

    new_share = {
        "resource_id": many_test_policies[2]["resource_id"],
        "identity_id": str(new_user_id),
        "action": Action.read,
    }

    response = await async_client.post("/api/v1/access/policy", json=new_share)
    payload = response.json()

    assert response.status_code == 201

    assert payload["id"] != policies_in_database[2].id

    assert payload["resource_id"] == many_test_policies[2]["resource_id"]
    assert payload["identity_id"] == str(new_user_id)
    assert payload["action"] == new_share["action"]
    assert payload["public"] is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
# TBD: should this pass - so an owner of a policy can publish the resource publicly?
async def test_user_with_owner_rights_posts_public_access_policy_fails(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests POST access policies, i.e. share."""
    app_override_provide_http_token_payload

    add_many_test_access_policies

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    print("=== current_user ===")
    print(current_user)

    # Give current user owner rights for the tested resource
    await add_one_test_access_policy(
        {
            "resource_id": many_test_policies[2]["resource_id"],
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        }
    )

    new_share = {
        "resource_id": many_test_policies[2]["resource_id"],
        "public": True,
        "action": Action.read,
    }

    read_response = await async_client.get(
        f"/api/v1/access/policy/resource/{many_test_policies[2]["resource_id"]}"
    )
    read_payload = read_response.json()

    print("=== read_payload ===")
    for policy in read_payload:
        print(policy)

    response = await async_client.post("/api/v1/access/policy", json=new_share)
    payload = response.json()

    assert response.status_code == 201

    assert payload["resource_id"] == many_test_policies[2]["resource_id"]
    assert payload["action"] == new_share["action"]
    assert payload["public"] is True

    # assert response.status_code == 403
    # assert payload == {"detail": "Forbidden."}

    # assert 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_user2_read_write],
    indirect=True,
)
async def test_user_posts_access_policies_without_access(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests POST access policies, i.e. share."""

    app_override_provide_http_token_payload

    for policy in many_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}


# More detailed delete tests in access CRUD!

# endregion: ## POST tests

# region: ## GET tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_admin_read],
    indirect=True,
)
async def test_admin_gets_access_policies(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policies")

    assert response.status_code == 200
    content = response.json()
    assert len(content) == len(many_test_policies) + 1
    # +1  for the user policy created, when the user accesses endpoint - not any more?
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
    "mocked_provide_http_token_payload",
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
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload
    add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policies")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_for_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload
    existing_policies = add_many_test_access_policies

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{str(existing_policies[2].resource_id)}"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 2

    for policy, existing_policy in zip(payload[:2], existing_policies[1:3]):
        modelled_policy = AccessPolicy.model_validate(policy)
        assert modelled_policy.resource_id == existing_policy.resource_id
        assert modelled_policy.identity_id == (
            existing_policy.identity_id if existing_policy.identity_id else None
        )
        assert modelled_policy.action == existing_policy.action
        assert modelled_policy.public == existing_policy.public


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_with_string_resource_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload
    add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policy/resource/wrong-format")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be a valid UUID" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "uuid_parsing"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_with_integer_resource_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload
    add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policy/resource/45392874598")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be a valid UUID" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "uuid_parsing"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

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
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }

    # Access policies for queried resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user3,
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

    existing_policies_in_db = []
    for policy in target_policies:
        created_policy = await add_one_test_access_policy(policy)
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
        assert received_policy.id == target_policy.id
        assert received_policy.resource_id == target_policy.resource_id
        assert received_policy.identity_id == target_policy.identity_id
        assert received_policy.action == target_policy.action
        assert received_policy.public == target_policy.public


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_without_being_owner(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid.uuid4())

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

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
        "identity_id": identity_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": identity_id_user3,
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

    existing_policies_in_db = []
    for policy in target_policies:
        created_policy = await add_one_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{resource_id_for_query}"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin,
        token_admin_write,
        token_user1_write,
        token_user2_write,
    ],
    indirect=True,
)
async def test_get_access_policies_for_resource_missing_read_scope(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET existing access policies for specific resource without read scope."""
    app_override_provide_http_token_payload
    existing_policies = add_many_test_access_policies

    response = await async_client.get(
        f"/api/v1/access/policy/resource/{str(existing_policies[2].resource_id)}"
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_type(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    register_one_resource,
    register_one_identity,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    entities = register_many_entities

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.own,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_one_test_access_policy(policy)

    admin_only_resources = [
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
        {
            "id": uuid.uuid4(),
            "type": ProtectedResource,
        },
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
    ]

    for resource in admin_only_resources:
        await register_one_resource(resource["id"], resource["type"])

    await register_one_identity(uuid.UUID(identity_id_user2), User)

    admin_only_policies = [
        {
            "resource_id": str(admin_only_resources[0]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # access user but write only
        },
        {
            "resource_id": str(admin_only_resources[1]["id"]),
            "action": Action.read,
            "public": True,
        },
        {
            "resource_id": str(admin_only_resources[2]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # access user but read only
        },
        {
            "resource_id": str(admin_only_resources[3]["id"]),
            "identity_id": str(identity_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_one_test_access_policy(policy)

    access_policy_crud = AccessPolicyCRUD()
    async with access_policy_crud as crud:
        admin_response = await crud.read_access_policies_by_resource_type(
            CurrentUserData(**current_user_data_admin), ResourceType.demo_resource
        )
        assert len(admin_response) == 6
        assert admin_response[0].resource_id == uuid.UUID(resource_id1)
        assert admin_response[1].resource_id == uuid.UUID(resource_id2)
        assert admin_response[2].resource_id == uuid.UUID(resource_id9)
        assert admin_response[3].resource_id == admin_only_resources[0]["id"]
        assert admin_response[4].resource_id == admin_only_resources[2]["id"]
        assert admin_response[5].resource_id == admin_only_resources[3]["id"]

    response = await async_client.get(
        "/api/v1/access/policy/resource/type/DemoResource"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 3

    expected_results = [str(resource_id1), str(resource_id2), str(resource_id9)]

    for read_policy in payload:
        assert read_policy["resource_id"] in expected_results
        policy["type"] = ResourceType.demo_resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_type_with_write_rights_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    register_one_resource,
    register_one_identity,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    entities = register_many_entities

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_one_test_access_policy(policy)

    admin_only_resources = [
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
        {
            "id": uuid.uuid4(),
            "type": ProtectedResource,
        },
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
    ]

    for resource in admin_only_resources:
        await register_one_resource(resource["id"], resource["type"])

    await register_one_identity(uuid.UUID(identity_id_user2), User)

    admin_only_policies = [
        {
            "resource_id": str(admin_only_resources[0]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # access user but write only
        },
        {
            "resource_id": str(admin_only_resources[1]["id"]),
            "action": Action.read,
            "public": True,
        },
        {
            "resource_id": str(admin_only_resources[2]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # access user but read only
        },
        {
            "resource_id": str(admin_only_resources[3]["id"]),
            "identity_id": str(identity_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_one_test_access_policy(policy)

    access_policy_crud = AccessPolicyCRUD()
    async with access_policy_crud as crud:
        admin_response = await crud.read_access_policies_by_resource_type(
            CurrentUserData(**current_user_data_admin), ResourceType.demo_resource
        )
        assert len(admin_response) == 6
        assert admin_response[0].resource_id == uuid.UUID(resource_id1)
        assert admin_response[1].resource_id == uuid.UUID(resource_id2)
        assert admin_response[2].resource_id == uuid.UUID(resource_id9)
        assert admin_response[3].resource_id == admin_only_resources[0]["id"]
        assert admin_response[4].resource_id == admin_only_resources[2]["id"]
        assert admin_response[5].resource_id == admin_only_resources[3]["id"]

    response = await async_client.get(
        "/api/v1/access/policy/resource/type/DemoResource"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_type_with_read_rights_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    register_one_resource,
    register_one_identity,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    entities = register_many_entities

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_one_test_access_policy(policy)

    admin_only_resources = [
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
        {
            "id": uuid.uuid4(),
            "type": ProtectedResource,
        },
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
        {
            "id": uuid.uuid4(),
            "type": DemoResource,
        },
    ]

    for resource in admin_only_resources:
        await register_one_resource(resource["id"], resource["type"])

    await register_one_identity(uuid.UUID(identity_id_user2), User)

    admin_only_policies = [
        {
            "resource_id": str(admin_only_resources[0]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # access user but write only
        },
        {
            "resource_id": str(admin_only_resources[1]["id"]),
            "action": Action.read,
            "public": True,
        },
        {
            "resource_id": str(admin_only_resources[2]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # access user but read only
        },
        {
            "resource_id": str(admin_only_resources[3]["id"]),
            "identity_id": str(identity_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_one_test_access_policy(policy)

    access_policy_crud = AccessPolicyCRUD()
    async with access_policy_crud as crud:
        admin_response = await crud.read_access_policies_by_resource_type(
            CurrentUserData(**current_user_data_admin), ResourceType.demo_resource
        )
        assert len(admin_response) == 6
        assert admin_response[0].resource_id == uuid.UUID(resource_id1)
        assert admin_response[1].resource_id == uuid.UUID(resource_id2)
        assert admin_response[2].resource_id == uuid.UUID(resource_id9)
        assert admin_response[3].resource_id == admin_only_resources[0]["id"]
        assert admin_response[4].resource_id == admin_only_resources[2]["id"]
        assert admin_response[5].resource_id == admin_only_resources[3]["id"]

    response = await async_client.get(
        "/api/v1/access/policy/resource/type/DemoResource"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read],
    indirect=True,
)
async def test_user_get_access_policies_for_non_existing_resource_type(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    response = await async_client.get("/api/v1/access/policy/resource/type/blablabla")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "enum"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_identity(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Access policies for the querying user - which is owner of resource:
    own_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.own,
    }
    write_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }

    # # Access policies for resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user3,
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": resource_id,
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
        created_policy = await add_one_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/identity/{str(current_user.user_id)}"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 4
    # the 3 from above and one for the user itself, that gets registered when the user logs in

    users_own_policy = {
        "resource_id": str(current_user.user_id),
        "identity_id": str(current_user.user_id),
        "action": Action.own,
    }

    expected_results = [
        own_test_access_policy_for_current_user,
        write_test_access_policy_for_current_user,
        read_test_access_policy_for_current_user,
        users_own_policy,
    ]

    for read_policy in payload:
        assert read_policy["resource_id"] in [
            result["resource_id"] for result in expected_results
        ]
        assert read_policy["identity_id"] == str(current_user.user_id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_for_identity(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload
    add_many_test_access_policies

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Access policies for the querying user - which is owner of resource:
    own_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.own,
    }
    write_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }

    # # Access policies for resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user3,
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": resource_id,
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
        created_policy = await add_one_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/identity/{str(current_user.user_id)}"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 4
    # the 3 from above and one for the user itself, that gets registered when the user logs in

    users_own_policy = {
        "resource_id": str(current_user.user_id),
        "identity_id": str(current_user.user_id),
        "action": Action.own,
    }

    expected_results = [
        own_test_access_policy_for_current_user,
        write_test_access_policy_for_current_user,
        read_test_access_policy_for_current_user,
        users_own_policy,
    ]

    for read_policy in payload:
        assert read_policy["resource_id"] in [
            result["resource_id"] for result in expected_results
        ]
        assert read_policy["identity_id"] == str(current_user.user_id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_another_users_identity_being_owner_of_common_resources(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Access policies for the querying user - which is owner of resource:
    own_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.own,
    }
    write_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }

    # # Access policies for resource for other users:
    own_test_access_policy_for_queried_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_queried_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_queried_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user3,
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": resource_id,
        "action": Action.read,
        "public": True,
    }

    target_policies = [
        own_test_access_policy_for_current_user,
        write_test_access_policy_for_current_user,
        read_test_access_policy_for_current_user,
        own_test_access_policy_for_queried_user,
        write_test_access_policy_for_queried_user,
        read1_test_access_policy_for_queried_user,
        read2_test_access_policy_for_random_user,
        read_public_test_access_policy,
    ]

    existing_policies_in_db = []
    for policy in target_policies:
        created_policy = await add_one_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/identity/{str(identity_id_user2)}"
    )
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 3

    expected_results = [
        own_test_access_policy_for_queried_user,
        write_test_access_policy_for_queried_user,
        read1_test_access_policy_for_queried_user,
    ]

    for read_policy in payload:
        assert read_policy["resource_id"] in [
            result["resource_id"] for result in expected_results
        ]
        assert read_policy["identity_id"] == str(identity_id_user2)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_another_users_identity_without_owner_of_common_resources(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Access policies for the querying user - which is owner of resource:
    write_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": current_user.user_id,
        "action": Action.write,
    }
    read_test_access_policy_for_current_user = {
        "resource_id": resource_id,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }

    # # Access policies for resource for other users:
    own_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": identity_id_user3,
        "action": Action.read,
    }
    read_public_test_access_policy = {
        "resource_id": resource_id,
        "action": Action.read,
        "public": True,
    }

    target_policies = [
        # own_test_access_policy_for_current_user,
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
        created_policy = await add_one_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/identity/{str(identity_id_user2)}"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_identity_type(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    register_one_resource,
    register_one_identity,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    entities = register_many_entities

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.own,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_one_test_access_policy(policy)

    admin_only_resources = [
        {
            "id": uuid.uuid4(),
            "type": AzureGroup,
        },
        {
            "id": uuid.uuid4(),
            "type": User,
        },
        {
            "id": uuid.uuid4(),
            "type": AzureGroup,
        },
        {
            "id": uuid.uuid4(),
            "type": User,
        },
    ]

    for resource in admin_only_resources:
        await register_one_resource(resource["id"], resource["type"])

    await register_one_identity(uuid.UUID(identity_id_user2), User)

    admin_only_policies = [
        {
            "resource_id": str(admin_only_resources[0]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # access user but write only
        },
        {
            "resource_id": str(admin_only_resources[1]["id"]),
            "action": Action.read,
            "public": True,
        },
        {
            "resource_id": str(admin_only_resources[2]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # access user but read only
        },
        {
            "resource_id": str(admin_only_resources[3]["id"]),
            "identity_id": str(identity_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_one_test_access_policy(policy)

    access_policy_crud = AccessPolicyCRUD()
    async with access_policy_crud as crud:
        admin_response = await crud.read_access_policies_by_identity_type(
            CurrentUserData(**current_user_data_admin), IdentityType.azure_group
        )
        assert len(admin_response) == 6
        assert admin_response[0].resource_id == uuid.UUID(azure_group_id1)
        assert admin_response[1].resource_id == uuid.UUID(azure_group_id2)
        assert admin_response[2].resource_id == uuid.UUID(azure_group_id3)
        assert admin_response[3].resource_id == uuid.UUID(azure_group_id4)
        assert admin_response[4].resource_id == admin_only_resources[0]["id"]
        assert admin_response[5].resource_id == admin_only_resources[2]["id"]

    response = await async_client.get("/api/v1/access/policy/identity/type/AzureGroup")
    payload = response.json()

    assert response.status_code == 200

    assert len(payload) == 4

    expected_results = [
        str(azure_group_id1),
        str(azure_group_id2),
        str(azure_group_id3),
        str(azure_group_id4),
    ]

    for read_policy in payload:
        assert read_policy["resource_id"] in expected_results
        policy["type"] = ResourceType.demo_resource


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_identity_type_missing_owner_rights(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    register_one_resource,
    register_one_identity,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    entities = register_many_entities

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_one_test_access_policy(policy)

    admin_only_resources = [
        {
            "id": uuid.uuid4(),
            "type": AzureGroup,
        },
        {
            "id": uuid.uuid4(),
            "type": User,
        },
        {
            "id": uuid.uuid4(),
            "type": AzureGroup,
        },
        {
            "id": uuid.uuid4(),
            "type": User,
        },
    ]

    for resource in admin_only_resources:
        await register_one_resource(resource["id"], resource["type"])

    await register_one_identity(uuid.UUID(identity_id_user2), User)

    admin_only_policies = [
        {
            "resource_id": str(admin_only_resources[0]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # access user but write only
        },
        {
            "resource_id": str(admin_only_resources[1]["id"]),
            "action": Action.read,
            "public": True,
        },
        {
            "resource_id": str(admin_only_resources[2]["id"]),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # access user but read only
        },
        {
            "resource_id": str(admin_only_resources[3]["id"]),
            "identity_id": str(identity_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_one_test_access_policy(policy)

    access_policy_crud = AccessPolicyCRUD()
    async with access_policy_crud as crud:
        admin_response = await crud.read_access_policies_by_identity_type(
            CurrentUserData(**current_user_data_admin), IdentityType.azure_group
        )
        assert len(admin_response) == 6
        assert admin_response[0].resource_id == uuid.UUID(azure_group_id1)
        assert admin_response[1].resource_id == uuid.UUID(azure_group_id2)
        assert admin_response[2].resource_id == uuid.UUID(azure_group_id3)
        assert admin_response[3].resource_id == uuid.UUID(azure_group_id4)
        assert admin_response[4].resource_id == admin_only_resources[0]["id"]
        assert admin_response[5].resource_id == admin_only_resources[2]["id"]

    response = await async_client.get("/api/v1/access/policy/identity/type/AzureGroup")
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read],
    indirect=True,
)
async def test_user_get_access_policies_for_non_existing_identity_type(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests GET access policies, i.e. share."""

    app_override_provide_http_token_payload

    response = await async_client.get("/api/v1/access/policy/identity/type/blablabla")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "enum"


# endregion: ## GET tests

# region: ## PUT tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_puts_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    update_policy = {
        **many_test_policies[2],
        "new_action": Action.own,
    }

    response = await async_client.put("/api/v1/access/policy", json=update_policy)
    payload = response.json()

    assert response.status_code == 200

    assert payload["id"] != policies_in_database[2].id
    assert payload["resource_id"] == update_policy["resource_id"]
    assert payload["resource_id"] == many_test_policies[2]["resource_id"]
    assert payload["identity_id"] == update_policy["identity_id"]
    assert payload["identity_id"] == many_test_policies[2]["identity_id"]
    assert payload["action"] == update_policy["new_action"]
    assert payload["action"] != many_test_policies[2]["action"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_with_owner_rights_puts_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Give current user owner rights for the tested resource
    await add_one_test_access_policy(
        {
            "resource_id": many_test_policies[2]["resource_id"],
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        }
    )

    update_policy = {
        **many_test_policies[2],
        "new_action": Action.own,
    }

    response = await async_client.put("/api/v1/access/policy", json=update_policy)
    payload = response.json()

    assert response.status_code == 200

    assert payload["id"] != policies_in_database[2].id
    assert payload["resource_id"] == update_policy["resource_id"]
    assert payload["resource_id"] == many_test_policies[2]["resource_id"]
    assert payload["identity_id"] == update_policy["identity_id"]
    assert payload["identity_id"] == many_test_policies[2]["identity_id"]
    assert payload["action"] == update_policy["new_action"]
    assert payload["action"] != many_test_policies[2]["action"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_with_owner_rights_puts_wrong_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    add_many_test_access_policies

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Give current user owner rights for the tested resource
    await add_one_test_access_policy(
        {
            "resource_id": many_test_policies[2]["resource_id"],
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        }
    )

    update_policy = {
        **many_test_policies[2],
        "action": Action.own,  # should be "new_action" instead of "action"
    }

    response = await async_client.put("/api/v1/access/policy", json=update_policy)
    payload = response.json()

    assert response.status_code == 422
    assert "Field required" in payload["detail"][0]["msg"]
    assert "missing" in payload["detail"][0]["type"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_without_owner_rights_puts_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    add_many_test_access_policies

    update_policy = {
        **many_test_policies[2],
        "new_action": Action.own,
    }

    response = await async_client.put("/api/v1/access/policy", json=update_policy)
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policy not found."}


# endregion: ## PUT tests

# region: ## DELETE tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_deletes_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    assert len(policies_in_database) == 10

    # should delete policies 0 and 4
    response = await async_client.delete(
        f"/api/v1/access/policy?resource_id={resource_id1}&identity_id={identity_id_user2}"
    )

    assert response.status_code == 200

    read_response = await async_client.get("/api/v1/access/policies")
    read_payload = read_response.json()

    assert len(read_payload) == 9
    # 2 deleted, but 1 created, when accessing the endpoint

    assert AccessPolicyRead(**read_payload[0]) == AccessPolicyRead(
        **policies_in_database[1].model_dump()
    )
    assert AccessPolicyRead(**read_payload[1]) == AccessPolicyRead(
        **policies_in_database[2].model_dump()
    )
    assert AccessPolicyRead(**read_payload[2]) == AccessPolicyRead(
        **policies_in_database[3].model_dump()
    )
    assert AccessPolicyRead(**read_payload[3]) == AccessPolicyRead(
        **policies_in_database[5].model_dump()
    )
    assert AccessPolicyRead(**read_payload[4]) == AccessPolicyRead(
        **policies_in_database[6].model_dump()
    )
    assert AccessPolicyRead(**read_payload[5]) == AccessPolicyRead(
        **policies_in_database[7].model_dump()
    )
    assert AccessPolicyRead(**read_payload[6]) == AccessPolicyRead(
        **policies_in_database[8].model_dump()
    )
    assert AccessPolicyRead(**read_payload[7]) == AccessPolicyRead(
        **policies_in_database[9].model_dump()
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_tries_to_delete_public_access_policy_without_resource_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    assert len(policies_in_database) == 10

    try:
        await async_client.delete("/api/v1/access/policy?public=True")
    except Exception as err:
        assert "Value error, Only one public resource can be deleted at a time." in str(
            err
        )
    else:
        pytest.fail("No Value error raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_tries_to_delete_all_access_policy_with_owner_rights(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    assert len(policies_in_database) == 10

    try:
        await async_client.delete("/api/v1/access/policy?Action=own")
    except Exception as err:
        assert (
            "Either resource_id or identity_id required when deleting policies."
            in str(err)
        )
    else:
        pytest.fail("No Value error raised!")


# # TBD: debug why this test fails!
@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_deletes_access_policy(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests DELETE access policy, i.e. stop sharing."""
    app_override_provide_http_token_payload

    policies_in_database = add_many_test_access_policies

    assert len(policies_in_database) == 10

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    # Give current user owner rights for the tested resource
    permission_for_test = await add_one_test_access_policy(
        {
            "resource_id": many_test_policies[0]["resource_id"],
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        }
    )

    # should delete policies 0 and 4
    response = await async_client.delete(
        f"/api/v1/access/policy?resource_id={resource_id1}&identity_id={identity_id_user2}"
    )

    assert response.status_code == 200

    read_response = await async_client.get(
        f"/api/v1/access/policy/resource/{many_test_policies[0]["resource_id"]}"
    )
    read_payload = read_response.json()

    assert len(read_payload) == 6
    # user has only access to 6

    assert AccessPolicyRead(**read_payload[0]) == AccessPolicyRead(
        **policies_in_database[5].model_dump()
    )
    assert AccessPolicyRead(**read_payload[1]) == AccessPolicyRead(
        **policies_in_database[6].model_dump()
    )
    assert AccessPolicyRead(**read_payload[2]) == AccessPolicyRead(
        **policies_in_database[7].model_dump()
    )
    assert AccessPolicyRead(**read_payload[3]) == AccessPolicyRead(
        **policies_in_database[8].model_dump()
    )
    assert AccessPolicyRead(**read_payload[4]) == AccessPolicyRead(
        **policies_in_database[9].model_dump()
    )
    # and the one created for the test:
    assert AccessPolicyRead(**read_payload[5]) == AccessPolicyRead(
        **permission_for_test.model_dump()
    )


# More detailed delete tests in access CRUD!

# endregion: ## DELETE tests

# endregion: ## AccessPolicy tests

# region: ## AccessLog tests

# Note the write log tests are in test_access_crud, as access logs only get written from inside the app.

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# AccessLogs:
# only read operations for log - no create, update, delete!
# implement as query parameters, wherever it makes sense?
# ✔︎ Admin reads all logs (admin only)
# ✔︎ Admin reads all logs for non-existing status_code
# ✔︎ User reads all logs fails
# ✔︎ Admin reads all logs with existing status_code
# ✔︎ Admin / User reads logs by resource_id
# ✔︎ Admin reads logs by resource_id for a specific identity_id
# ✔︎ User reads logs by resource_id without permission from access policies
# ✔︎ User reads logs by resource_id with write permission from access policies only fails
# ✔︎ User reads logs by resource_id with read permission from access policies only fails
# ✔︎ Admin reads logs by identity_id
# ✔︎ User reads access by identity for own identity
# ✔︎ User reads access by identity for other identity fails (consider if access policies can change that?)
# ✔︎ Admin / Users read resources first "own" log (created_at): corresponds to create
# ✔︎ Users read resources first "own" log (created_at) with write permission from access policies - date only, so everyone is allowed
# ✔︎ Users read resources first "own" log (created_at) with read permission from access policies - date only, so everyone is allowed
# ✔︎ Admin / Users read multiple resources first "own" log (created_at)
# ✔︎ Users read multiple resources first "own" log (created_at) - with write permissions only
# ✔︎ Users read multiple resources first "own" log (created_at) - with read permissions only
# ✔︎ Users read multiple resources first "own" log (created_at) - without permissions fails
# ✔︎ Admin / Users read resources latest access log (last_accessed)
# ✔︎ Users read resources latest access log (last_accessed) with write permission from access policies only fails - full access log - needs owner
# ✔︎ Users read resources latest access log (last_accessed) with read permission from access policies only fails - full access log - needs owner
# ✔︎ Admin / Users read multiple resources latest access log (last_accessed)
# ✔︎ Users read multiple resources latest access log (last_accessed) - with write permissions only fails - date-only, so everyone is allowed
# ✔︎ Users read multiple resources latest access log (last_accessed) - with read permissions only fails - date-only, so everyone is allowed
# ✔︎ Users read multiple resources latest access log (last_accessed) - without permissions fails
# ✔︎ Admin / User read access count - use func.count/len

# region: ## GET tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_created_access_all_logs(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    database_logs = add_many_test_access_logs

    response = await async_client.get("/api/v1/access/logs")
    payload = response.json()

    assert response.status_code == 200

    for returned, expected in zip(payload, database_logs):
        returned = AccessLogRead(**returned)
        assert int(returned.id)
        assert returned.resource_id == expected.resource_id
        assert returned.identity_id == expected.identity_id
        assert returned.action == expected.action
        assert returned.status_code == expected.status_code
        assert returned.time == expected.time


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_access_all_logs_with_non_existing_status_code(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    # No logs in the database
    # other than the ones created when the user logs in
    # But those have status_code 201!
    response = await async_client.get("/api/v1/access/logs?status_code=200")
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user1_read_write, token_user2_read],
    indirect=True,
)
async def test_user_gets_access_all_logs(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    # No logs in the database
    # other than the ones created when the user logs in
    # But those have status_code 201!
    response = await async_client.get("/api/v1/access/logs")
    payload = response.json()

    assert response.status_code == 401

    assert payload == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_all_logs_with_status_code(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    # getting the one, that's created due to admin accessing the endpoint
    before_time = datetime.now()
    response = await async_client.get("/api/v1/access/logs?status_code=201")
    after_time = datetime.now()
    payload = response.json()

    assert response.status_code == 200

    current_admin_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    modelled_access_log = AccessLogRead(**payload[0])

    assert modelled_access_log.resource_id == current_admin_user.user_id
    assert modelled_access_log.identity_id == current_admin_user.user_id
    assert modelled_access_log.action == Action.own
    assert modelled_access_log.status_code == 201
    assert modelled_access_log.time >= before_time - timedelta(seconds=1)
    assert modelled_access_log.time <= after_time + timedelta(seconds=1)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read],
    indirect=True,
)
async def test_get_logs_for_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload
    add_many_test_access_policies  # not relevant - just filling some data in the table

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id2,
        "identity_id": str(current_user.user_id),
        "action": Action.own,
    }
    await add_one_test_access_policy(policy)

    database_logs = add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id2}")
    payload = response.json()

    assert response.status_code == 200
    assert len(payload) == 5

    expected_logs = [
        database_logs[1],
        database_logs[3],
        database_logs[6],
        database_logs[7],
        database_logs[10],
    ]

    for returned, expected in zip(payload, expected_logs):
        returned = AccessLogRead(**returned)
        assert int(returned.id)
        assert returned.resource_id == expected.resource_id
        assert returned.identity_id == expected.identity_id
        assert returned.action == expected.action
        assert returned.status_code == expected.status_code
        # TBD: there should be a couple of hours offset
        # probably wrong, because AccessLogCreate is used to place the test logs
        # and AccessLogCreate ignores the time attribute
        assert returned.time == expected.time


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_get_logs_for_resource_and_identity(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    add_many_test_access_logs,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload
    add_many_test_access_policies  # not relevant - just filling some data in the table

    database_logs = add_many_test_access_logs

    response = await async_client.get(
        f"/api/v1/access/log/{resource_id2}?identity_id={str(identity_id_user1)}"
    )
    payload = response.json()

    assert response.status_code == 200
    assert len(payload) == 2

    expected_logs = [
        database_logs[1],
        database_logs[10],
    ]

    for returned, expected in zip(payload, expected_logs):
        returned = AccessLogRead(**returned)
        assert int(returned.id)
        assert returned.resource_id == expected.resource_id
        assert returned.identity_id == expected.identity_id
        assert returned.action == expected.action
        assert returned.status_code == expected.status_code
        # TBD: debug time offset
        assert returned.time == expected.time


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user2_read],
    indirect=True,
)
async def test_get_logs_for_resource_without_permissions_from_policies(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    add_many_test_access_logs,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload
    add_many_test_access_policies  # not relevant - just filling some data in the table

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id2}")
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_get_logs_for_resource_with_write_permission_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload
    add_many_test_access_policies  # not relevant - just filling some data in the table

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id2,
        "identity_id": str(current_user.user_id),
        "action": Action.write,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id2}")
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_get_logs_for_resource_with_read_permission_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_policies,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload
    add_many_test_access_policies  # not relevant - just filling some data in the table

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id2,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id2}")
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_get_logs_for_identity(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    database_logs = add_many_test_access_logs

    response = await async_client.get(
        f"/api/v1/access/log/identity/{str(identity_id_user3)}"
    )
    payload = response.json()

    assert response.status_code == 200
    assert len(payload) == 6

    expected_logs = [
        database_logs[3],
        database_logs[4],
        database_logs[5],
        database_logs[6],
        database_logs[7],
        database_logs[11],
    ]

    for returned, expected in zip(payload, expected_logs):
        returned = AccessLogRead(**returned)
        assert int(returned.id)
        assert returned.resource_id == expected.resource_id
        assert returned.identity_id == expected.identity_id
        assert returned.action == expected.action
        assert returned.status_code == expected.status_code
        assert returned.time == expected.time


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_get_logs_for_identity(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_test_access_policy,
    add_one_test_access_log,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": "own",
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": "own",
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    access_logs = [
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "own",
            "status_code": 201,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "own",
            "status_code": 201,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id1,
            "action": "read",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "read",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "write",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "read",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id1,
            "action": "read",
            "status_code": 200,
        },
    ]

    for log in access_logs:
        await add_one_test_access_log(log)

    async with AccessPolicyCRUD() as access_policy_crud:
        policies = await access_policy_crud.read_access_policies_for_identity(
            CurrentUserData(**current_user_data_admin), current_user.user_id
        )

    before_time = datetime.now()
    response = await async_client.get(
        f"/api/v1/access/log/identity/{str(current_user.user_id)}"
    )
    after_time = datetime.now()
    payload = response.json()

    assert response.status_code == 200
    assert len(payload) == 9

    # Note: the first two logs are created through user self-sign up and user reading itself
    for returned, expected in zip(payload[1:], access_logs):
        returned = AccessLogRead(**returned)
        expected = AccessLogCreate(**expected)
        assert int(returned.id)
        assert returned.resource_id == expected.resource_id
        assert returned.identity_id == expected.identity_id
        assert returned.action == expected.action
        assert returned.status_code == expected.status_code
        assert returned.time > before_time - timedelta(seconds=1)
        assert returned.time < after_time + timedelta(seconds=1)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_get_logs_for_identity_with_write_and_read_permission_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_test_access_policy,
    add_one_test_access_log,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": "write",
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": "read",
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    access_logs = [
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "own",
            "status_code": 201,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "own",
            "status_code": 201,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id1,
            "action": "read",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "read",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "write",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id2,
            "action": "read",
            "status_code": 200,
        },
        {
            "identity_id": str(current_user.user_id),
            "resource_id": resource_id1,
            "action": "read",
            "status_code": 200,
        },
    ]

    for log in access_logs:
        await add_one_test_access_log(log)

    async with AccessPolicyCRUD() as access_policy_crud:
        policies = await access_policy_crud.read_access_policies_for_identity(
            CurrentUserData(**current_user_data_admin), current_user.user_id
        )

    response = await async_client.get(
        f"/api/v1/access/log/identity/{str(current_user.user_id)}"
    )
    payload = response.json()

    assert response.status_code == 200
    assert len(payload) == 2

    for returned in payload:
        returned = AccessLogRead(**returned)
        assert returned.resource_id == current_user.user_id
        assert returned.resource_id != resource_id1
        assert returned.resource_id != resource_id2


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id1,
        "identity_id": str(current_user.user_id),
        "action": Action.own,
    }
    await add_one_test_access_policy(policy)

    response = await async_client.get(f"/api/v1/access/log/{resource_id1}/created")
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert payload == (database_logs[0].time).isoformat()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resource_with_only_write_permission(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id1,
        "identity_id": str(current_user.user_id),
        "action": Action.write,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id1}/created")
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert payload == (database_logs[0].time).isoformat()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resource_with_only_read_permission(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id1,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id1}/created")
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert payload == (database_logs[0].time).isoformat()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resource_without_access_fails(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id1}/created")
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resources(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id3,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    response = await async_client.post(
        "/api/v1/access/log/created", json=[resource_id1, resource_id2, resource_id3]
    )
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert (
        (database_logs[0].time - timedelta(seconds=1)).isoformat()
        < payload[0]
        < (database_logs[0].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[1].time - timedelta(seconds=1)).isoformat()
        < payload[1]
        < (database_logs[1].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[2].time - timedelta(seconds=1)).isoformat()
        < payload[2]
        < (database_logs[2].time + timedelta(seconds=1)).isoformat()
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resources_with_write_permission_on_one_resource_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": Action.write,
        },
        {
            "resource_id": resource_id3,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    response = await async_client.post(
        "/api/v1/access/log/created", json=[resource_id1, resource_id2, resource_id3]
    )
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert (
        (database_logs[0].time - timedelta(seconds=1)).isoformat()
        < payload[0]
        < (database_logs[0].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[1].time - timedelta(seconds=1)).isoformat()
        < payload[1]
        < (database_logs[1].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[2].time - timedelta(seconds=1)).isoformat()
        < payload[2]
        < (database_logs[2].time + timedelta(seconds=1)).isoformat()
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resources_with_read_permission_on_resources(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": Action.read,
        },
        {
            "resource_id": resource_id3,
            "identity_id": str(current_user.user_id),
            "action": Action.read,
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    response = await async_client.post(
        "/api/v1/access/log/created", json=[resource_id1, resource_id2, resource_id3]
    )
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert (
        (database_logs[0].time - timedelta(seconds=1)).isoformat()
        < payload[0]
        < (database_logs[0].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[1].time - timedelta(seconds=1)).isoformat()
        < payload[1]
        < (database_logs[1].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[2].time - timedelta(seconds=1)).isoformat()
        < payload[2]
        < (database_logs[2].time + timedelta(seconds=1)).isoformat()
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_creation_datetime_for_resources_without_access_on_one_resource_fails(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    response = await async_client.post(
        "/api/v1/access/log/created", json=[resource_id1, resource_id2, resource_id3]
    )
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_log_for_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id3,
        "identity_id": str(current_user.user_id),
        "action": Action.own,
    }
    await add_one_test_access_policy(policy)

    response = await async_client.get(
        f"/api/v1/access/log/{resource_id3}/last-accessed"
    )
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    returned = AccessLogRead(**payload)
    assert int(returned.id)
    assert returned.resource_id == database_logs[11].resource_id
    assert returned.identity_id == database_logs[11].identity_id
    assert returned.action == database_logs[11].action
    assert returned.status_code == database_logs[11].status_code
    # TBD: debug time offset
    assert returned.time == database_logs[11].time


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_log_for_resource_only_write_permission(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id3,
        "identity_id": str(current_user.user_id),
        "action": Action.write,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(
        f"/api/v1/access/log/{resource_id3}/last-accessed"
    )
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_log_for_resource_only_read_permission(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id3,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(
        f"/api/v1/access/log/{resource_id3}/last-accessed"
    )
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_log_for_resource_missing_access(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    add_many_test_access_logs

    response = await async_client.get(
        f"/api/v1/access/log/{resource_id3}/last-accessed"
    )
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_datetime_for_resources(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
        {
            "resource_id": resource_id3,
            "identity_id": str(current_user.user_id),
            "action": Action.own,
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    response = await async_client.post(
        "/api/v1/access/log/last-accessed",
        json=[resource_id1, resource_id2, resource_id3],
    )
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert (
        (database_logs[0].time - timedelta(seconds=1)).isoformat()
        < payload[0]
        < (database_logs[9].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[1].time - timedelta(seconds=1)).isoformat()
        < payload[1]
        < (database_logs[10].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[2].time - timedelta(seconds=1)).isoformat()
        < payload[2]
        < (database_logs[11].time + timedelta(seconds=1)).isoformat()
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_datetime_for_resources_with_read_and_write_access_only(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policies = [
        {
            "resource_id": resource_id1,
            "identity_id": str(current_user.user_id),
            "action": Action.read,
        },
        {
            "resource_id": resource_id2,
            "identity_id": str(current_user.user_id),
            "action": Action.write,
        },
        {
            "resource_id": resource_id3,
            "identity_id": str(current_user.user_id),
            "action": Action.read,
        },
    ]
    for policy in policies:
        await add_one_test_access_policy(policy)

    response = await async_client.post(
        "/api/v1/access/log/last-accessed",
        json=[resource_id1, resource_id2, resource_id3],
    )
    payload = response.json()

    database_logs = add_many_test_access_logs

    assert response.status_code == 200
    assert (
        (database_logs[0].time - timedelta(seconds=1)).isoformat()
        < payload[0]
        < (database_logs[9].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[1].time - timedelta(seconds=1)).isoformat()
        < payload[1]
        < (database_logs[10].time + timedelta(seconds=1)).isoformat()
    )
    assert (
        (database_logs[2].time - timedelta(seconds=1)).isoformat()
        < payload[2]
        < (database_logs[11].time + timedelta(seconds=1)).isoformat()
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_last_access_datetime_for_resources_without_access_fails(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    response = await async_client.post(
        "/api/v1/access/log/last-accessed",
        json=[resource_id1, resource_id2, resource_id3],
    )
    payload = response.json()

    assert response.status_code == 404
    assert payload == {"detail": "Access logs not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read, token_user1_read, token_user2_read],
    indirect=True,
)
async def test_get_access_count_for_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_access_logs,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
    add_one_test_access_policy,
):
    """Tests GET access logs."""
    app_override_provide_http_token_payload

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )
    policy = {
        "resource_id": resource_id2,
        "identity_id": str(current_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    add_many_test_access_logs

    response = await async_client.get(f"/api/v1/access/log/{resource_id2}/count")
    payload = response.json()

    assert response.status_code == 200
    assert int(payload) == 5


# endregion: ## GET tests

# endregion: ## AccessLog tests
