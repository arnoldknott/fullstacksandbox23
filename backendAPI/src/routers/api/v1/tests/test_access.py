import pytest
from httpx import AsyncClient
from fastapi import FastAPI

import uuid
from pprint import pprint

from core.types import Action, ResourceType, IdentityType, CurrentUserData
from models.identity import AzureGroup, User
from models.access import AccessPolicy, AccessPolicyRead
from models.demo_resource import DemoResource
from models.protected_resource import ProtectedResource
from crud.access import AccessPolicyCRUD
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
    resource_id1,
    resource_id2,
    resource_id9,
    azure_group_id1,
    azure_group_id2,
    azure_group_id3,
    azure_group_id4,
    current_user_data_admin,
)


# region: ## POST tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_access_policies(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_current_users,
    register_many_protected_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    register_many_current_users
    register_many_protected_resources

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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_access_policies_for_non_existing_resources(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_current_users,
    # register_many_protected_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    register_many_current_users

    for policy in many_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_non_public_access_policies_for_non_existing_identities(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_protected_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    register_many_protected_resources

    private_test_policies = many_test_policies[0:9].copy()

    for policy in private_test_policies:
        response = await async_client.post("/api/v1/access/policy", json=policy)

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_posts_public_access_policies_for_non_existing_identities(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_protected_resources,
):
    """Tests POST access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    register_many_protected_resources

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


# endregion: ## POST tests

# region: ## GET tests:


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
    ],
    indirect=True,
)
async def test_admin_get_access_policies_for_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [
        token_admin_read_write,
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_with_string_resource_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policy/resource/wrong-format")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be a valid UUID" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "uuid_parsing"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_admin_read_write,
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_with_integer_resource_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency
    add_many_test_access_policies

    response = await async_client.get("/api/v1/access/policy/resource/45392874598")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be a valid UUID" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "uuid_parsing"


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

    app_override_get_azure_payload_dependency
    add_many_test_access_policies  # not used - but added so there's more stuff in the database

    resource_id_for_query = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": user_id_user3,
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
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id_for_query,
        "identity_id": user_id_user3,
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
async def test_get_access_policies_for_resource_missing_read_scope(
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


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_type(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    register_one_resource,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    entities = register_many_entities

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.own,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_test_access_policy(policy)

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
            "identity_id": str(user_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_test_access_policy(policy)

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
        # TBD: check for the specific policies

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
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_type_with_write_rights_only(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    register_one_resource,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    entities = register_many_entities

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_test_access_policy(policy)

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
            "identity_id": str(user_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_test_access_policy(policy)

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
        # TBD: check for the specific policies

    response = await async_client.get(
        "/api/v1/access/policy/resource/type/DemoResource"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_resource_type_with_read_rights_only(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    register_one_resource,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    entities = register_many_entities

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.read,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_test_access_policy(policy)

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
            "identity_id": str(user_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_test_access_policy(policy)

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
        # TBD: check for the specific policies

    response = await async_client.get(
        "/api/v1/access/policy/resource/type/DemoResource"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read, token_user1_read],
    indirect=True,
)
async def test_user_get_access_policies_for_non_existing_resource_type(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    response = await async_client.get("/api/v1/access/policy/resource/type/blablabla")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "enum"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_identity(
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

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user3,
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
        created_policy = await add_test_access_policy(policy)
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
    "mocked_get_azure_token_payload",
    [
        token_admin_read,
    ],
    indirect=True,
)
async def test_admin_get_access_policies_for_identity(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency
    add_many_test_access_policies

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user3,
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
        created_policy = await add_test_access_policy(policy)
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
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_another_users_identity_being_owner_of_common_resources(
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

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_queried_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_queried_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user3,
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
        created_policy = await add_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/identity/{str(user_id_user2)}"
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
        assert read_policy["identity_id"] == str(user_id_user2)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user2_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_another_users_identity_without_owner_of_common_resources(
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

    resource_id = str(uuid.uuid4())
    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        "identity_id": user_id_user2,
        "action": Action.own,
    }
    write_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.write,
    }
    read1_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user2,
        "action": Action.read,
    }
    read2_test_access_policy_for_random_user = {
        "resource_id": resource_id,
        "identity_id": user_id_user3,
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
        created_policy = await add_test_access_policy(policy)
        existing_policies_in_db.append(created_policy)

    response = await async_client.get(
        f"/api/v1/access/policy/identity/{str(user_id_user2)}"
    )
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_identity_type(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    register_one_resource,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    entities = register_many_entities

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.own,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_test_access_policy(policy)

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
            "identity_id": str(user_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_test_access_policy(policy)

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
        # TBD: check for the specific policies

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
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
    ],
    indirect=True,
)
async def test_user_get_access_policies_for_identity_type_missing_owner_rights(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    register_many_entities,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    register_one_resource,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    entities = register_many_entities

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    for entity in entities:
        policy = {
            "resource_id": str(entity.id),
            "identity_id": str(current_user.user_id),
            "action": Action.write,  # user needs to own a resource for being allowed to read all access_policies
        }
        policy = await add_test_access_policy(policy)

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
            "identity_id": str(user_id_user2),
            "action": Action.own,  # another user owns the target resource
        },
    ]

    for policy in admin_only_policies:
        await add_test_access_policy(policy)

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
        # TBD: check for the specific policies

    response = await async_client.get("/api/v1/access/policy/identity/type/AzureGroup")
    payload = response.json()

    assert response.status_code == 404

    assert payload == {"detail": "Access policies not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read, token_user1_read],
    indirect=True,
)
async def test_user_get_access_policies_for_non_existing_identity_type(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET access policies, i.e. share."""

    app_override_get_azure_payload_dependency

    response = await async_client.get("/api/v1/access/policy/identity/type/blablabla")
    payload = response.json()

    assert response.status_code == 422
    assert "Input should be" in payload["detail"][0]["msg"]
    assert payload["detail"][0]["type"] == "enum"


# endregion: ## GET tests

# region: ## PUT tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_puts_access_policy(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_with_owner_rights_puts_access_policy(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

    policies_in_database = add_many_test_access_policies

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    # Give current user owner rights for the tested resource
    await add_test_access_policy(
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
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_with_owner_rights_puts_wrong_access_policy(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
    current_user_from_azure_token,
    mocked_get_azure_token_payload,
    add_test_access_policy,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

    add_many_test_access_policies

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    # Give current user owner rights for the tested resource
    await add_test_access_policy(
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

    print(payload)

    assert response.status_code == 422
    assert "Field required" in payload["detail"][0]["msg"]
    assert "missing" in payload["detail"][0]["type"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_without_owner_rights_puts_access_policy(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_deletes_access_policy(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

    policies_in_database = add_many_test_access_policies

    assert len(policies_in_database) == 10

    # should delete policies 0 and 4
    response = await async_client.delete(
        f"/api/v1/access/policy?resource_id={resource_id1}&identity_id={user_id_user2}"
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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_tries_to_delete_public_access_policy_without_resource_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_tries_to_delete_all_access_policy_wit_owner_rights(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_access_policies,
):
    """Tests GET access policies, i.e. share."""
    app_override_get_azure_payload_dependency

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


# TBD: implement delete tests

# endregion: ## DELETE tests
