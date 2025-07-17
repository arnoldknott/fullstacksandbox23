import uuid
from datetime import datetime, timedelta
from typing import List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action, CurrentUserData
from crud.access import AccessLoggingCRUD
from models.identity import (
    Group,
    GroupRead,
    Me,
    SubGroup,
    SubGroupRead,
    SubSubGroup,
    SubSubGroupRead,
    ThemeVariants,
    UeberGroup,
    UeberGroupRead,
    User,
    UserRead,
)
from models.protected_resource import ProtectedResourceRead
from routers.api.v1.identities import (
    delete_group,
    get_user_by_id,
    post_existing_groups_to_uebergroup,
    post_existing_subgroup_to_group,
    post_existing_user_to_group,
    post_existing_users_to_subgroup,
)
from tests.utils import (
    current_user_data_admin,
    many_test_azure_users,
    many_test_groups,
    many_test_sub_groups,
    many_test_sub_sub_groups,
    many_test_ueber_groups,
    token_admin_read,
    token_admin_read_write,
    token_payload_one_group,
    token_payload_roles_admin,
    token_payload_roles_user,
    token_payload_scope_api_read,
    token_payload_scope_api_read_write,
    token_payload_scope_api_write,
    token_payload_tenant_id,
    token_payload_user_id,
    token_user1_read,
    token_user1_read_groups,
    token_user1_read_write,
    token_user1_read_write_groups,
    token_user2_read,
    token_user2_read_write,
)

# Passing tests:
# ✔︎ admin user creates a user
# ✔︎ admin user reads all users
# ✔︎ admin user reads a user by azure id
# ✔︎ admin user reads a user by id
# ✔︎ regular user reads itself by azure_id
# ✔︎ regular user reads itself by id
# ✔︎ regular user updates itself
# ✔︎ admin user updates a user -> is_active is the only thing, that can get updated
# ✔︎ admin user deletes a user
# ✔︎ regular user deletes itself
# ✔︎ last_accessed_at is updated on every create, read and update (unless admin access another user)
# groups: groups are not part of the user endpoints - need their own endpoints, but security is taking care of the sign-up!
# ✔︎ users connections to groups are created in the database - checked through security tests: adding a new group to a user.
# ✔︎ a user, that is already signed up was added in Azure to a new group: does the new connection show up in the database?

# Failing tests:
# - modify the user_id
# No token / invalid token provided
# ✔︎ read all user
# ✔︎ read user by azure_id
# ✔︎ read user by id
# ✔︎ update user
# ✔︎ delete user
# Regular user (not admin):
# ✔︎ wants to create another user
# ✔︎ wants to read all user
# ✔︎ wants to update another user
# ✔︎ wants to read another user by id
# ✔︎ wants to read another user by azure id
# ✔︎ regular user wants to delete another user

# Identity tests:
# ✔︎ all endpoints of ueber-group
# ✔︎ all endpoints of group
# ✔︎ all endpoints of sub-group
# ✔︎ all endpoints of sub-sub-group
# ✔ add user to ueber-group and remove again
# ✔︎ bulk add users to ueber-group and bulk remove again
# ✔︎ bulk add groups to ueber-group and bulk remove again
# ✔︎ add user to group and remove again
# ✔︎ bulk add users to group and bulk remove again
# ✔︎ bulk add sub-groups to group and bulk remove again
# ✔︎ add user to sub-group and remove again
# ✔︎ bulk add users to sub-group and bulk remove again
# ✔︎ bulk add sub-sub-groups to sub-group and bulk remove again
# ✔ add user to sub-sub-group and remove again
# ✔︎ bulk add users to sub-sub-group and bulk remove again
# ✔︎ add user to group without inheriting group
# ✔︎ add group to ueber-group and delete again
# ✔︎ add sub-group to group and delete again
# ✔︎ add sub-sub-group to sub-group and delete again
# ✔︎ add sub_group and sub_sub_group to ueber_group fails
# ✔ add sub_sub_group to group fails
# ✔ access to resource through inheritance (user from any group) and logging access
# ✔ access to resource through inheritance (user from any group) without inheritance
# ✔ access to resource through inheritance through multiple generations (user in ueber-group can access resource in sub-sub-group)
# ✔ access to resource through inheritance through multiple generations with lack of inheritance
# ✔ user inherits access to resource from group, group gets deleted, user no longer has access to resource

# region: ## POST tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read_write,
            **token_payload_roles_admin,
            **token_payload_one_group,
        }
    ],
    indirect=True,
)
async def test_admin_posts_user(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    mock_guards,
    current_user_from_azure_token,
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    # Make a POST request to create the user
    before_time = datetime.now()
    response = await async_client.post(
        "/api/v1/user/",
        json=many_test_azure_users[2],
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == many_test_azure_users[2]["azure_user_id"]
    assert created_user.azure_tenant_id == many_test_azure_users[2]["azure_tenant_id"]

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            current_user, resource_id=created_user.id
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            current_user, resource_id=created_user.id
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time == created_at

    # Verify that the user was created in the database
    db_user = await get_user_by_id(
        created_user.id, mocked_provide_http_token_payload, mock_guards(roles=["User"])
    )
    assert db_user is not None
    assert db_user.id is not None
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[2]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[2]["azure_tenant_id"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read_write,
            **token_payload_roles_admin,
            **token_payload_one_group,
        }
    ],
    indirect=True,
)
async def test_post_user_with_integer_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    mock_guards,
    current_user_from_azure_token,
):
    """Tests posting a integer user_id to user_post endpoint fails"""
    app_override_provide_http_token_payload

    # Make a POST request to create the user
    before_time = datetime.now()
    response = await async_client.post(
        "/api/v1/user/",
        json={**many_test_azure_users[2], "id": 1},
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == many_test_azure_users[2]["azure_user_id"]
    assert created_user.azure_tenant_id == many_test_azure_users[2]["azure_tenant_id"]

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            current_user, resource_id=created_user.id
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            current_user, resource_id=created_user.id
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time == created_at

    # Verify that the user was created in the database
    db_user = await get_user_by_id(
        created_user.id, mocked_provide_http_token_payload, mock_guards(roles=["User"])
    )
    assert db_user.id == uuid.UUID(created_user.id)
    assert db_user.id != 1
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[2]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[2]["azure_tenant_id"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read_write,
            **token_payload_roles_admin,
            **token_payload_one_group,
        }
    ],
    indirect=True,
)
async def test_post_user_with_uuid_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    mock_guards,
    current_user_from_azure_token,
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload
    test_uuid = str(uuid.uuid4())

    # Make a POST request to create the user
    before_time = datetime.now()
    response = await async_client.post(
        "/api/v1/user/",
        json={**many_test_azure_users[2], "id": test_uuid},
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == many_test_azure_users[2]["azure_user_id"]
    assert created_user.azure_tenant_id == many_test_azure_users[2]["azure_tenant_id"]

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            current_user, resource_id=created_user.id
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            current_user, resource_id=created_user.id
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time == created_at

    # Verify that the user was created in the database
    db_user = await get_user_by_id(
        created_user.id, mocked_provide_http_token_payload, mock_guards(roles=["User"])
    )
    assert db_user.id == uuid.UUID(created_user.id)
    assert db_user.id != uuid.UUID(test_uuid)
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[2]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[2]["azure_tenant_id"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read_write,
            **token_payload_roles_user,
            **token_payload_one_group,
        }
    ],
    indirect=True,
)
async def test_user_posts_user(
    async_client: AsyncClient, app_override_provide_http_token_payload: FastAPI
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        json=many_test_azure_users[0],
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}

    # this would allow other users to create users, which is not allowed - only self-sign-up!:
    # assert response.status_code == 201
    # created_user = User(**response.json())
    # assert created_user.azure_user_id == one_test_user["azure_user_id"]
    # assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            # **token_payload_scope_api_read_write,
            **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            # **token_payload_scope_api_read_write,
            **token_payload_scope_api_write,
            **token_payload_roles_admin,
        },
        {
            **token_payload_scope_api_read_write,
            # **token_payload_roles_admin,
        },
        {},
    ],
    indirect=True,
)
async def test_post_user_invalid_token(
    async_client: AsyncClient, app_override_provide_http_token_payload: FastAPI
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        json=many_test_azure_users[0],
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


# endregion: ## POST tests

# region: ## GET tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_groups, token_admin_read],
    # here the admin get's itself => last_accessed_at should change!
    indirect=True,
)
async def test_user_gets_own_user_through_me_endpoint(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    await add_one_azure_test_user(0)

    before_time = datetime.now()
    response = await async_client.get("/api/v1/user/me")
    after_time = datetime.now()

    assert response.status_code == 200
    user = response.json()
    modelled_response_user = Me(**user)
    assert user["azure_token_roles"] == mocked_provide_http_token_payload["roles"]
    if "groups" in mocked_provide_http_token_payload:
        assert user["azure_token_groups"] == mocked_provide_http_token_payload["groups"]
        assert len(user["azure_token_groups"]) == len(
            mocked_provide_http_token_payload["groups"]
        )
    assert "id" in user
    assert user["azure_user_id"] == str(mocked_provide_http_token_payload["oid"])
    assert user["azure_tenant_id"] == str(mocked_provide_http_token_payload["tid"])
    assert "id" in user["user_account"]
    assert user["user_account"]["user_id"] == user["id"]
    assert user["user_account"]["is_publicAIuser"] is False
    assert "id" in user["user_profile"]
    assert user["user_profile"]["theme_color"] == "#353c6e"
    assert user["user_profile"]["theme_variant"] == ThemeVariants.tonal_spot
    assert user["user_profile"]["contrast"] == 0.0

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time >= created_at
    # assert last_accessed_at.status_code == 200  # admin gets a 201 for the creation.


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write_groups],
    # here the admin get's itself => last_accessed_at should change!
    indirect=True,
)
async def test_user_gets_own_user_through_me_endpoint_with_ueber_groups(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_ueber_groups,
    add_one_test_access_policy,
    mocked_provide_http_token_payload,
    current_user_from_azure_token: CurrentUserData,
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    mocked_ueber_groups = await add_many_test_ueber_groups()

    policy = {
        "resource_id": str(mocked_ueber_groups[1].id),
        "identity_id": str(current_user.user_id),
        "action": Action.write,
    }
    await add_one_test_access_policy(policy)

    response_add_user_to_ueber_group = await async_client.post(
        f"/api/v1/user/{current_user.user_id}/group/{str(mocked_ueber_groups[1].id)}"
    )
    assert response_add_user_to_ueber_group.status_code == 201

    response = await async_client.get("/api/v1/user/me")

    assert response.status_code == 200
    user = response.json()
    modelled_user = Me(**user)
    assert modelled_user.azure_token_roles == mocked_provide_http_token_payload["roles"]
    group_uuids = [uuid.UUID(g) for g in mocked_provide_http_token_payload["groups"]]
    if "groups" in mocked_provide_http_token_payload:
        assert modelled_user.azure_token_groups == group_uuids
        assert len(modelled_user.azure_token_groups) == len(
            mocked_provide_http_token_payload["groups"]
        )
    assert "id" in user
    assert modelled_user.id == current_user.user_id
    assert modelled_user.azure_user_id == uuid.UUID(
        mocked_provide_http_token_payload["oid"]
    )
    assert modelled_user.azure_tenant_id == uuid.UUID(
        mocked_provide_http_token_payload["tid"]
    )
    assert modelled_user.user_account.id is not None
    assert uuid.UUID(modelled_user.user_account.user_id) == modelled_user.id
    assert modelled_user.user_account.is_publicAIuser is False
    assert modelled_user.user_profile is not None
    assert modelled_user.user_profile.theme_color == "#353c6e"
    assert modelled_user.user_profile.theme_variant == ThemeVariants.tonal_spot
    assert modelled_user.user_profile.contrast == 0.0
    assert len(modelled_user.ueber_groups) == 1
    assert modelled_user.ueber_groups[0].id == mocked_ueber_groups[1].id
    assert modelled_user.ueber_groups[0].name == mocked_ueber_groups[1].name
    assert (
        modelled_user.ueber_groups[0].description == mocked_ueber_groups[1].description
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_users(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_azure_test_users: List[User],
):
    """Test GET one user"""

    # mocks the access token:
    app_override_provide_http_token_payload

    # adds a user to the database, which is the one to GET:
    users = await add_many_azure_test_users()

    response = await async_client.get("/api/v1/user/")
    assert response.status_code == 200
    database_users = response.json()
    database_users = sorted(database_users, key=lambda x: x["id"])
    assert len(users) == 5
    assert len(database_users) == 5
    for database_user, user in zip(database_users, users):
        assert "id" in database_user
        assert database_user["azure_user_id"] == str(user.azure_user_id)
        assert database_user["azure_tenant_id"] == str(user.azure_tenant_id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        }
    ],
    indirect=True,
)
async def test_user_gets_users(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_azure_test_users: List[User],
):
    """Test GET all users"""

    # mocks the access token:
    app_override_provide_http_token_payload

    # adds users to the database
    await add_many_azure_test_users()

    response = await async_client.get("/api/v1/user/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
async def test_get_users_without_token(
    async_client: AsyncClient,
    add_many_azure_test_users: List[User],
):
    """Test GET one user"""
    await add_many_azure_test_users()

    response = await async_client.get("/api/v1/user/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        # token_user1_read,
        # token_user1_read_write,
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    user_in_database = await add_one_azure_test_user(4)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    policy = {
        "resource_id": str(user_in_database.id),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    groups_for_user_in_database = many_test_azure_users[4]["groups"]
    for group_id in groups_for_user_in_database:
        policy = {
            "resource_id": str(group_id),
            "identity_id": str(accessing_user.user_id),
            "action": Action.read,
        }
        await add_one_test_access_policy(policy)

    before_time = datetime.now()
    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    after_time = datetime.now()
    assert response.status_code == 200
    response_user = response.json()

    modelled_response_user = UserRead(**response_user)

    assert modelled_response_user.id is not None
    assert modelled_response_user.azure_user_id == user_in_database.azure_user_id
    assert modelled_response_user.azure_tenant_id == user_in_database.azure_tenant_id
    assert len(modelled_response_user.azure_groups) == 3
    assert not hasattr(modelled_response_user, "user_account")
    assert not hasattr(modelled_response_user, "user_profile")

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        # token_user1_read,
        # token_user1_read_write,
        token_user1_read_write_groups,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id_with_common_groups(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    user_in_database = await add_one_azure_test_user(4)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    policy = {
        "resource_id": str(user_in_database.id),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    groups_for_user_in_database = many_test_azure_users[4]["groups"]
    policy_group0 = {
        "resource_id": str(groups_for_user_in_database[0]),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy_group0)
    policy_group2 = {
        "resource_id": str(groups_for_user_in_database[2]),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy_group2)

    before_time = datetime.now()
    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    after_time = datetime.now()
    assert response.status_code == 200
    response_user = response.json()

    modelled_response_user = UserRead(**response_user)

    assert modelled_response_user.id is not None
    assert modelled_response_user.azure_user_id == user_in_database.azure_user_id
    assert modelled_response_user.azure_tenant_id == user_in_database.azure_tenant_id
    assert not hasattr(modelled_response_user, "user_account")
    assert not hasattr(modelled_response_user, "user_profile")
    assert len(modelled_response_user.azure_groups) == 3

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id_with_partial_access_to_other_users_groups(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    user_in_database = await add_one_azure_test_user(0)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    policy = {
        "resource_id": str(user_in_database.id),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    groups_for_user_in_database = [
        many_test_azure_users[0]["groups"][0],
        many_test_azure_users[0]["groups"][2],
    ]
    for group_id in groups_for_user_in_database:
        policy = {
            "resource_id": str(group_id),
            "identity_id": str(accessing_user.user_id),
            "action": Action.read,
        }
        await add_one_test_access_policy(policy)

    before_time = datetime.now()
    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    after_time = datetime.now()
    assert response.status_code == 200
    response_user = response.json()

    modelled_response_user = UserRead(**response_user)

    assert modelled_response_user.id is not None
    assert modelled_response_user.azure_user_id == user_in_database.azure_user_id
    assert modelled_response_user.azure_tenant_id == user_in_database.azure_tenant_id
    assert not hasattr(modelled_response_user, "user_account")
    assert not hasattr(modelled_response_user, "user_profile")
    assert len(modelled_response_user.azure_groups) == 2
    modelled_response_user.azure_groups = sorted(
        modelled_response_user.azure_groups, key=lambda x: x.id
    )

    response_group_ids = {group.id for group in modelled_response_user.azure_groups}

    assert all(
        uuid.UUID(group_id) in response_group_ids
        for group_id in groups_for_user_in_database
    )

    # assert modelled_response_user.azure_groups[0].id == uuid.UUID(
    #     groups_for_user_in_database[0]
    # )
    # assert modelled_response_user.azure_groups[1].id == uuid.UUID(
    #     groups_for_user_in_database[1]
    # )

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id_with_no_access_to_other_users_groups(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    user_in_database = await add_one_azure_test_user(0)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    policy = {
        "resource_id": str(user_in_database.id),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    before_time = datetime.now()
    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    after_time = datetime.now()
    assert response.status_code == 200
    response_user = response.json()

    modelled_response_user = UserRead(**response_user)

    assert modelled_response_user.id is not None
    assert modelled_response_user.azure_user_id == user_in_database.azure_user_id
    assert modelled_response_user.azure_tenant_id == user_in_database.azure_tenant_id
    assert len(modelled_response_user.azure_groups) == 0

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_provide_http_token_payload
    user_in_database = await add_one_azure_test_user(1)

    before_time = datetime.now()
    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    after_time = datetime.now()
    assert response.status_code == 200
    response_user = response.json()
    modelled_response_user = UserRead(**response_user)
    assert "id" in response_user
    assert response_user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert response_user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    assert len(response_user["azure_groups"]) == 3

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_gets_another_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    user_in_database = await add_one_azure_test_user(2)

    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "User not found"


@pytest.mark.anyio
async def test_get_user_by_azure_id_without_token(
    async_client: AsyncClient,
    add_one_azure_test_user: List[User],
):
    """Test GET one user"""
    user_in_db = await add_one_azure_test_user(0)

    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_db.azure_user_id)}"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_groups, token_admin_read],
    # here the admin get's itself => last_accessed_at should change!
    indirect=True,
)
async def test_user_gets_user_by_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_provide_http_token_payload
    # the target user:
    user_in_database = await add_one_azure_test_user(1)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    groups_for_user_in_database = many_test_azure_users[1]["groups"]
    policy_non_common_group = {
        "resource_id": str(groups_for_user_in_database[1]),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy_non_common_group)

    policy = {
        "resource_id": str(user_in_database.id),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    before_time = datetime.now()
    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    after_time = datetime.now()

    assert response.status_code == 200
    user = response.json()
    modelled_response_user = UserRead(**user)
    assert "id" in user
    assert user["azure_user_id"] == str(modelled_response_user.azure_user_id)
    assert user["azure_tenant_id"] == str(modelled_response_user.azure_tenant_id)
    assert len(user["azure_groups"]) == 3
    assert not hasattr(modelled_response_user, "user_account")
    assert not hasattr(modelled_response_user, "user_profile")

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_user_by_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_provide_http_token_payload
    user_in_database = await add_one_azure_test_user(1)

    before_time = datetime.now()
    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    after_time = datetime.now()

    assert response.status_code == 200
    user = response.json()
    modelled_response_user = UserRead(**user)
    assert "id" in user
    assert user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    assert len(user["azure_groups"]) == 3

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=modelled_response_user.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_gets_another_user_by_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's another user id by its user id."""

    # mocks the access token:
    app_override_provide_http_token_payload
    user_in_database = await add_one_azure_test_user(1)

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "User not found."
    # assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
async def test_get_user_by_id_without_token(
    async_client: AsyncClient, add_one_azure_test_user: List[User], mock_guards
):
    """Test GET one user"""
    user_in_db = await add_one_azure_test_user(0)

    response = await async_client.get(f"/api/v1/user/azure/{str(user_in_db.id)}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            # missing scope_api_read
            **token_payload_roles_user,
            **token_payload_user_id,
            **token_payload_tenant_id,
        },
        # {
        #     ## Hmmm - user does not need to have a role to read itself
        #     # enabling this would mean that the all users need to be added in Azure Entra AD
        #     **token_payload_scope_api_read,
        #     # missing roles_user
        #     **token_payload_user_id,
        #     **token_payload_tenant_id,
        # },
    ],
    indirect=True,
)
async def test_get_user_by_id_with_missing_scope(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_provide_http_token_payload
    user_in_database = await add_one_azure_test_user(0)

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_scope_api_read,
            **token_payload_roles_user,
            # missing user_id
            **token_payload_tenant_id,
        },
        {
            **token_payload_scope_api_read,
            **token_payload_roles_user,
            **token_payload_user_id,
            # missing tenant_id
        },
    ],
    indirect=True,
)
async def test_get_user_by_id_invalid_token(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_provide_http_token_payload
    user_in_database = await add_one_azure_test_user(0)

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


# endregion: ## GET tests

# region: ## PUT tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_put_user(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    response = await async_client.get(f"/api/v1/user/{str(current_user.user_id)}")

    assert response.status_code == 200
    user = response.json()
    original_user = UserRead(**user)
    assert original_user.id is not None
    assert original_user.id == current_user.user_id
    assert not hasattr(original_user, "user_account")
    assert not hasattr(original_user, "user_profile")
    assert original_user.is_active is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(current_user.user_id)}",
        json={"is_active": False},
    )
    assert response.status_code == 200
    updated_user = User(**response.json())
    assert updated_user.is_active is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_own_user_account(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_account": {"is_publicAIuser": True},
        },
    )
    assert response.status_code == 200
    updated_user = Me(**response.json())
    assert updated_user.user_account.is_publicAIuser is True

    response_read = await async_client.get("/api/v1/user/me")

    assert response_read.status_code == 200
    user = response_read.json()

    assert user["azure_token_roles"] == mocked_provide_http_token_payload["roles"]
    if "groups" in mocked_provide_http_token_payload:
        assert user["azure_token_groups"] == mocked_provide_http_token_payload["groups"]
        assert len(user["azure_token_groups"]) == len(
            mocked_provide_http_token_payload["groups"]
        )
    assert "id" in user
    assert user["azure_user_id"] == str(mocked_provide_http_token_payload["oid"])
    assert user["azure_tenant_id"] == str(mocked_provide_http_token_payload["tid"])
    assert "id" in user["user_account"]
    assert user["user_account"]["user_id"] == user["id"]
    assert user["user_account"]["is_publicAIuser"] is True
    assert "id" in user["user_profile"]
    assert user["user_profile"]["theme_color"] == "#353c6e"
    assert user["user_profile"]["theme_variant"] == ThemeVariants.tonal_spot
    assert user["user_profile"]["contrast"] == 0.0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_own_user_profile(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "#769CDF",
                "theme_variant": "Vibrant",
                "contrast": 1.0,
            },
        },
    )
    assert response.status_code == 200
    updated_user = Me(**response.json())
    assert updated_user.user_profile.theme_color == "#769CDF"
    assert updated_user.user_profile.theme_variant == ThemeVariants.vibrant
    assert updated_user.user_profile.contrast == 1.0

    response_read = await async_client.get("/api/v1/user/me")

    assert response_read.status_code == 200
    user = response_read.json()

    assert user["azure_token_roles"] == mocked_provide_http_token_payload["roles"]
    if "groups" in mocked_provide_http_token_payload:
        assert user["azure_token_groups"] == mocked_provide_http_token_payload["groups"]
        assert len(user["azure_token_groups"]) == len(
            mocked_provide_http_token_payload["groups"]
        )
    assert "id" in user
    assert user["azure_user_id"] == str(mocked_provide_http_token_payload["oid"])
    assert user["azure_tenant_id"] == str(mocked_provide_http_token_payload["tid"])
    assert "id" in user["user_account"]
    assert user["user_account"]["user_id"] == user["id"]
    assert user["user_account"]["is_publicAIuser"] is False
    assert "id" in user["user_profile"]
    assert user["user_profile"]["theme_color"] == "#769CDF"
    assert user["user_profile"]["theme_variant"] == ThemeVariants.vibrant
    assert user["user_profile"]["contrast"] == 1.0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_own_user_account_and_profile(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_account": {"is_publicAIuser": True},
            "user_profile": {
                "theme_color": "#769CDF",
                "theme_variant": "Vibrant",
                "contrast": 1.0,
            },
        },
    )
    assert response.status_code == 200
    updated_user = Me(**response.json())
    assert updated_user.user_account.is_publicAIuser is True
    assert updated_user.user_profile.theme_color == "#769CDF"
    assert updated_user.user_profile.theme_variant == ThemeVariants.vibrant
    assert updated_user.user_profile.contrast == 1.0

    response_read = await async_client.get("/api/v1/user/me")

    assert response_read.status_code == 200
    user = response_read.json()

    assert user["azure_token_roles"] == mocked_provide_http_token_payload["roles"]
    if "groups" in mocked_provide_http_token_payload:
        assert user["azure_token_groups"] == mocked_provide_http_token_payload["groups"]
        assert len(user["azure_token_groups"]) == len(
            mocked_provide_http_token_payload["groups"]
        )
    assert "id" in user
    assert user["azure_user_id"] == str(mocked_provide_http_token_payload["oid"])
    assert user["azure_tenant_id"] == str(mocked_provide_http_token_payload["tid"])
    assert "id" in user["user_account"]
    assert user["user_account"]["user_id"] == user["id"]
    assert user["user_account"]["is_publicAIuser"] is True
    assert "id" in user["user_profile"]
    assert user["user_profile"]["theme_color"] == "#769CDF"
    assert user["user_profile"]["theme_variant"] == ThemeVariants.vibrant
    assert user["user_profile"]["contrast"] == 1.0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_user_profile_with_missing_hashtag_in_color(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "769CDF",
                "theme_variant": "Vibrant",
                "contrast": 1.0,
            },
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "User not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_user_profile_with_short_color(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "#769C",
                "theme_variant": "Vibrant",
                "contrast": 1.0,
            },
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "User not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_user_profile_with_wrong_color(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "#769CXY",
                "theme_variant": "Vibrant",
                "contrast": 1.0,
            },
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "User not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_user_profile_with_wrong_theme(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "#769CDF",
                "theme_variant": "SomeTheme",
                "contrast": 1.0,
            },
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "User not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_user_profile_contrast_too_low(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "#769CDF",
                "contrast": -3.0,
            },
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "User not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_user_profile_contrast_too_high(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_user = current_test_user

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(current_user.user_id),
            "user_profile": {
                "theme_color": "#769CDF",
                "contrast": 6.2,
            },
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "User not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_other_users_user_account(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_test_user
    other_user = await add_one_azure_test_user(2)

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(other_user.id),
            "user_account": {"is_publicAIuser": True},
        },
    )
    assert response.status_code == 403
    payload = response.json()
    assert payload["detail"] == "Forbidden."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_other_users_user_profile(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user,
    current_test_user,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    current_test_user
    other_user = await add_one_azure_test_user(2)

    # Make a PUT request to update the user
    response = await async_client.put(
        "/api/v1/user/me",
        json={
            "id": str(other_user.id),
            "user_profile": {"is_publicAIuser": True},
        },
    )
    assert response.status_code == 403
    payload = response.json()
    assert payload["detail"] == "Forbidden."


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_user1_read_write],
#     indirect=True,
# )
# async def test_user_put_user(
#     async_client: AsyncClient,
#     app_override_provide_http_token_payload: FastAPI,
#     add_one_azure_test_user: List[User],
#     mock_guards,
# ):
#     """Tests put user endpoint"""

#     # mocks the access token:
#     app_override_provide_http_token_payload
#     existing_user = await add_one_azure_test_user(0)

#     existing_db_user = await get_user_by_id(
#         str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
#     )
#     assert existing_db_user.is_active is True

#     # Make a PUT request to update the user
#     response = await async_client.put(
#         f"/api/v1/user/{str(existing_user.id)}",
#         json={"is_active": False},
#     )
#     assert response.status_code == 401
#     assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_put_user_from_admin(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    mock_guards,
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(2)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_provide_http_token_payload,
        mock_guards(roles=["User"]),
    )
    assert existing_db_user.is_active is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
    )
    assert response.status_code == 200
    updated_user = User(**response.json())
    assert updated_user.is_active is False

    # Verify that the user was updated in the database
    before_time = datetime.now()
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    after_time = datetime.now()
    content = response.json()
    db_user = User.model_validate(content)
    assert db_user is not None
    assert db_user.is_active is False

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=db_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=db_user.id,
        )

    assert created_at > before_time - timedelta(seconds=2)
    assert created_at < after_time + timedelta(seconds=2)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    # refactored into: updating a user needs Admin roles
    indirect=True,
)
async def test_put_user_with_integer_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    mock_guards,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(0)
    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_provide_http_token_payload,
        mock_guards(roles=["User"]),
    )
    assert existing_db_user.is_active is True

    # Make a PUT request to update the user
    before_time = datetime.now()
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False, "id": 1},
    )
    after_time = datetime.now()
    assert response.status_code == 200
    updated_user = User(**response.json())
    assert updated_user.is_active is False

    # Verify that the user was updated in the database
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    content = response.json()
    db_user = User.model_validate(content)
    assert db_user is not None
    assert db_user.is_active is False
    assert db_user.id != 1
    assert db_user.id == existing_user.id

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=db_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=db_user.id,
        )

    assert created_at > before_time - timedelta(
        seconds=3
    )  # TBD: set back to 2 seconds: 3, due to extremly slow localhost,
    assert created_at < after_time + timedelta(
        seconds=3
    )  # TBD: set back to 2 seconds: 3, dur to extremly slow localhost
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    # refactored into: updating a user needs Admin roles
    indirect=True,
)
async def test_admin_put_user_with_uuid_user_id(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    mock_guards,
):
    """Tests put user endpoint"""

    test_uuid = str(uuid.uuid4())

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(0)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_provide_http_token_payload,
        mock_guards(roles=["User"]),
    )
    assert existing_db_user.is_active is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False, "id": test_uuid},
    )
    assert response.status_code == 200
    updated_user = User(**response.json())
    assert updated_user.is_active is False

    # Verify that the user was updated in the database
    before_time = datetime.now()
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    after_time = datetime.now()
    content = response.json()
    db_user = User.model_validate(content)
    assert db_user is not None
    assert db_user.is_active is False
    assert db_user.id != uuid.UUID(test_uuid)

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=db_user.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=db_user.id,
        )

    assert created_at > before_time - timedelta(seconds=2)
    assert created_at < after_time + timedelta(seconds=2)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_write,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_write,
            **token_payload_roles_user,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
        },
    ],
    indirect=True,
)
async def test_put_user_invalid_token(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(0)

    existing_db_user = await get_user_by_id(
        str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_another_user(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(1)

    existing_db_user = await get_user_by_id(
        str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
    )
    assert existing_db_user.is_active is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
        # json={"azure_user_id": str(existing_user.azure_user_id), "is_active": False},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not updated."}


# endregion: ## PUT tests

# region: ## DELETE tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_deletes_itself(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test user deletes itself"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(0)
    existing_db_user = await get_user_by_id(
        str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True

    # Make a DELETE request to update the user
    response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}",
    )
    assert response.status_code == 200

    # Verify that the user was deleted in the database
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "User not found."
    # assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_deletes_user(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_provide_http_token_payload,
    mock_guards,
):
    """Test admin deletes a user"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(0)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_provide_http_token_payload,
        mock_guards(roles=["User"]),
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True

    # Make a DELETE request to update the user
    response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}",
    )
    assert response.status_code == 200

    # Verify that the user was deleted in the database
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "User not found."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_write,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
        },
    ],
    indirect=True,
)
async def test_delete_user_invalid_token(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: User,
    mock_guards,
):
    """Test deleting a user with invalid token fails"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(2)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        token_admin_read,
        mock_guards(roles=["User"]),
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True

    # Make a DELETE request to update the user
    response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}",
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}

    # check if user is still there:
    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        token_admin_read,
        mock_guards(roles=["User"]),
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    # TBD: use user2 here somewhere?
    [token_user1_read_write],
    indirect=True,
)
async def test_user_deletes_another_user(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test delete another user fails"""

    # mocks the access token:
    app_override_provide_http_token_payload
    existing_user = await add_one_azure_test_user(2)

    existing_db_user = await get_user_by_id(
        str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True

    # Make a DELETE request to update the user
    response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}",
    )
    assert response.status_code == 404
    assert response.text == '{"detail":"User not deleted."}'

    # check if user is still there:
    existing_db_user = await get_user_by_id(
        str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
    )
    assert existing_db_user.azure_user_id == existing_user.azure_user_id
    assert existing_db_user.id is not None
    assert existing_db_user.is_active is True


# endregion: ## DELETE tests

# region: Ueber Group tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_ueber_group_endpoints(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    add_many_test_ueber_groups,
):
    """Tests the ueber_group endpoints of the API."""
    app_override_provide_http_token_payload

    # Make a POST request to create the ueber-group
    response = await async_client.post(
        "/api/v1/uebergroup/",
        json=many_test_ueber_groups[0],
    )

    assert response.status_code == 201
    created_ueber_group = UeberGroup(**response.json())
    assert created_ueber_group.id is not None
    assert created_ueber_group.name == many_test_ueber_groups[0]["name"]
    assert created_ueber_group.description == many_test_ueber_groups[0]["description"]

    # add some more ueber groups:
    # note: the first one is going to be double with different id's
    mocked_ueber_groups = await add_many_test_ueber_groups(
        mocked_provide_http_token_payload
    )
    created_ueber_group.id = uuid.UUID(created_ueber_group.id)
    expected_ueber_groups = [created_ueber_group] + mocked_ueber_groups
    expected_ueber_groups = sorted(expected_ueber_groups, key=lambda x: x.id)

    # Make a GET request to get all ueber-groups
    response = await async_client.get(
        "/api/v1/uebergroup/",
    )
    assert response.status_code == 200
    read_ueber_groups = response.json()
    assert len(read_ueber_groups) == len(expected_ueber_groups)
    for read_child, expected_child in zip(read_ueber_groups, expected_ueber_groups):
        modelled_ueber_group = UeberGroupRead(**read_child)
        assert modelled_ueber_group.id == expected_child.id
        assert modelled_ueber_group.name == expected_child.name
        assert modelled_ueber_group.description == expected_child.description

    # Make a GET request to get one ueber-group by id
    response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[2].id)}",
    )
    assert response.status_code == 200
    read_ueber_group = response.json()
    modelled_ueber_group = UeberGroupRead(**read_ueber_group)
    assert modelled_ueber_group.id == mocked_ueber_groups[2].id
    assert modelled_ueber_group.name == mocked_ueber_groups[2].name
    assert modelled_ueber_group.description == mocked_ueber_groups[2].description

    # Make a PUT request to update one ueber-group
    new_data = {"name": "The updated title of a child."}

    response = await async_client.put(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}",
        json=new_data,
    )
    assert response.status_code == 200
    read_ueber_group = response.json()
    modelled_ueber_group = UeberGroupRead(**read_ueber_group)
    assert modelled_ueber_group.id == mocked_ueber_groups[1].id
    assert modelled_ueber_group.name == new_data["name"]
    assert modelled_ueber_group.description == mocked_ueber_groups[1].description

    # Make a DELETE request to delete one ueber-group
    response = await async_client.delete(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[0].id)}",
    )
    assert response.status_code == 200

    # Make a GET request to get deleted ueber-group by id fails
    response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[0].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "UeberGroup not found."}


# endregion: Ueber Group tests


# region: Group tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_group_endpoints(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    access_to_one_parent,
    add_many_test_groups,
):
    """Tests the group endpoints of the API."""
    app_override_provide_http_token_payload

    # Make a POST request to create a standalone group
    response = await async_client.post(
        "/api/v1/group/",
        json=many_test_groups[0],
    )

    parent_identity_id = await access_to_one_parent(UeberGroup)

    assert response.status_code == 201
    created_group = Group(**response.json())
    assert created_group.id is not None
    assert created_group.name == many_test_groups[0]["name"]
    assert created_group.description == many_test_groups[0]["description"]

    # Make a POST request to create a group as child of existing ueber-group
    response = await async_client.post(
        f"/api/v1/uebergroup/{parent_identity_id}/group",
        json=many_test_groups[0],
    )

    assert response.status_code == 201
    created_group_as_child = Group(**response.json())
    assert created_group_as_child.id is not None
    assert created_group_as_child.name == many_test_groups[0]["name"]
    assert created_group_as_child.description == many_test_groups[0]["description"]

    # add some more groups:
    # note: the first one is going to be double with different id's
    mocked_groups = await add_many_test_groups(mocked_provide_http_token_payload)
    created_group.id = uuid.UUID(created_group.id)
    created_group_as_child.id = uuid.UUID(created_group_as_child.id)
    expected_groups = [created_group, created_group_as_child] + mocked_groups
    expected_groups = sorted(expected_groups, key=lambda x: x.id)

    # Make a GET request to get all groups
    response = await async_client.get(
        "/api/v1/group/",
    )
    assert response.status_code == 200
    read_groups = response.json()
    assert len(read_groups) == len(expected_groups)
    for read_child, expected_child in zip(read_groups, expected_groups):
        modelled_group = GroupRead(**read_child)
        assert modelled_group.id == expected_child.id
        assert modelled_group.name == expected_child.name
        assert modelled_group.description == expected_child.description

    # Make a GET request to get one group by id
    response = await async_client.get(
        f"/api/v1/group/{str(mocked_groups[2].id)}",
    )
    assert response.status_code == 200
    read_group = response.json()
    modelled_group = GroupRead(**read_group)
    assert modelled_group.id == mocked_groups[2].id
    assert modelled_group.name == mocked_groups[2].name
    assert modelled_group.description == mocked_groups[2].description

    # Make a PUT request to update one group
    new_data = {"name": "The updated title of a child."}

    response = await async_client.put(
        f"/api/v1/group/{str(mocked_groups[1].id)}",
        json=new_data,
    )
    assert response.status_code == 200
    read_group = response.json()
    modelled_group = GroupRead(**read_group)
    assert modelled_group.id == mocked_groups[1].id
    assert modelled_group.name == new_data["name"]
    assert modelled_group.description == mocked_groups[1].description

    # Make a DELETE request to delete one group
    response = await async_client.delete(
        f"/api/v1/group/{str(mocked_groups[0].id)}",
    )
    assert response.status_code == 200

    # Make a GET request to get deleted group by id fails
    response = await async_client.get(
        f"/api/v1/group/{str(mocked_groups[0].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group not found."}


# endregion: Group tests

# region: Sub Group tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_sub_group_endpoints(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    access_to_one_parent,
    mocked_provide_http_token_payload,
    add_many_test_sub_groups,
):
    """Tests the sub_group endpoints of the API."""
    app_override_provide_http_token_payload

    parent_identity_id = await access_to_one_parent(Group)

    # Make a POST request to create the sub-group
    response = await async_client.post(
        f"/api/v1/group/{parent_identity_id}/subgroup",
        json=many_test_sub_groups[0],
    )
    # Addition for standalone sub-groups:
    # response = await async_client.post(
    #     "/api/v1/subgroup/",
    #     json=many_test_sub_groups[0],
    # )

    assert response.status_code == 201
    created_sub_group = SubGroup(**response.json())
    assert created_sub_group.id is not None
    assert created_sub_group.name == many_test_sub_groups[0]["name"]
    assert created_sub_group.description == many_test_sub_groups[0]["description"]

    # add some more sub groups:
    # note: the first one is going to be double with different id's
    mocked_sub_groups = await add_many_test_sub_groups(
        mocked_provide_http_token_payload
    )
    created_sub_group.id = uuid.UUID(created_sub_group.id)
    expected_sub_groups = [created_sub_group] + mocked_sub_groups
    expected_sub_groups = sorted(expected_sub_groups, key=lambda x: x.id)

    # Make a GET request to get all sub-groups
    response = await async_client.get(
        "/api/v1/subgroup/",
    )
    assert response.status_code == 200
    read_sub_groups = response.json()
    assert len(read_sub_groups) == len(expected_sub_groups)
    for read_child, expected_child in zip(read_sub_groups, expected_sub_groups):
        modelled_sub_group = SubGroupRead(**read_child)
        assert modelled_sub_group.id == expected_child.id
        assert modelled_sub_group.name == expected_child.name
        assert modelled_sub_group.description == expected_child.description

    # Make a GET request to get one sub-group by id
    response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[2].id)}",
    )
    assert response.status_code == 200
    read_sub_group = response.json()
    modelled_sub_group = SubGroupRead(**read_sub_group)
    assert modelled_sub_group.id == mocked_sub_groups[2].id
    assert modelled_sub_group.name == mocked_sub_groups[2].name
    assert modelled_sub_group.description == mocked_sub_groups[2].description

    # Make a PUT request to update one sub-group
    new_data = {"name": "The updated title of a child."}

    response = await async_client.put(
        f"/api/v1/subgroup/{str(mocked_sub_groups[1].id)}",
        json=new_data,
    )
    assert response.status_code == 200
    read_sub_group = response.json()
    modelled_sub_group = SubGroupRead(**read_sub_group)
    assert modelled_sub_group.id == mocked_sub_groups[1].id
    assert modelled_sub_group.name == new_data["name"]
    assert modelled_sub_group.description == mocked_sub_groups[1].description

    # Make a DELETE request to delete one sub-group
    response = await async_client.delete(
        f"/api/v1/subgroup/{str(mocked_sub_groups[0].id)}",
    )
    assert response.status_code == 200

    # Make a GET request to get deleted sub-group by id fails
    response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[0].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "SubGroup not found."}


# endregion: Sub Group tests


# region: Sub-sub Group tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_sub_sub_group_endpoints(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    access_to_one_parent,
    mocked_provide_http_token_payload,
    add_many_test_sub_sub_groups,
):
    """Tests the sub_sub_group endpoints of the API."""
    app_override_provide_http_token_payload

    subgroup_id = await access_to_one_parent(SubGroup)

    # Make a POST request to create the sub-sub-group
    response = await async_client.post(
        f"/api/v1/subgroup/{subgroup_id}/subsubgroup",
        json=many_test_sub_sub_groups[0],
    )
    # Addition for stand-alone sub-sub-groups:
    # response = await async_client.post(
    #     "/api/v1/subsubgroup/",
    #     json=many_test_sub_sub_groups[0],
    # )

    assert response.status_code == 201
    created_sub_sub_group = SubSubGroup(**response.json())
    assert created_sub_sub_group.id is not None
    assert created_sub_sub_group.name == many_test_sub_sub_groups[0]["name"]
    assert (
        created_sub_sub_group.description == many_test_sub_sub_groups[0]["description"]
    )

    # add some more sub-sub groups:
    # note: the first one is going to be double with different id's
    mocked_sub_sub_groups = await add_many_test_sub_sub_groups(
        mocked_provide_http_token_payload
    )
    created_sub_sub_group.id = uuid.UUID(created_sub_sub_group.id)
    expected_sub_sub_groups = [created_sub_sub_group] + mocked_sub_sub_groups
    expected_sub_sub_groups = sorted(expected_sub_sub_groups, key=lambda x: x.id)

    # Make a GET request to get all sub-sub-groups
    response = await async_client.get(
        "/api/v1/subsubgroup/",
    )
    assert response.status_code == 200
    read_sub_sub_groups = response.json()
    assert len(read_sub_sub_groups) == len(expected_sub_sub_groups)
    for read_child, expected_child in zip(read_sub_sub_groups, expected_sub_sub_groups):
        modelled_sub_sub_group = SubSubGroupRead(**read_child)
        assert modelled_sub_sub_group.id == expected_child.id
        assert modelled_sub_sub_group.name == expected_child.name
        assert modelled_sub_sub_group.description == expected_child.description

    # Make a GET request to get one sub-sub-group by id
    response = await async_client.get(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[2].id)}",
    )
    assert response.status_code == 200
    read_sub_sub_group = response.json()
    modelled_sub_sub_group = SubSubGroupRead(**read_sub_sub_group)
    assert modelled_sub_sub_group.id == mocked_sub_sub_groups[2].id
    assert modelled_sub_sub_group.name == mocked_sub_sub_groups[2].name
    assert modelled_sub_sub_group.description == mocked_sub_sub_groups[2].description

    # Make a PUT request to update one sub-sub-group
    new_data = {"name": "The updated title of a child."}

    response = await async_client.put(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[1].id)}",
        json=new_data,
    )
    assert response.status_code == 200
    read_sub_sub_group = response.json()
    modelled_sub_sub_group = SubSubGroupRead(**read_sub_sub_group)
    assert modelled_sub_sub_group.id == mocked_sub_sub_groups[1].id
    assert modelled_sub_sub_group.name == new_data["name"]
    assert modelled_sub_sub_group.description == mocked_sub_sub_groups[1].description

    # Make a DELETE request to delete one sub-sub-group
    response = await async_client.delete(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[0].id)}",
    )
    assert response.status_code == 200

    # Make a GET request to get deleted sub-sub-group by id fails
    response = await async_client.get(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[0].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "SubSubGroup not found."}


# endregion: Sub-sub_sub Group tests


# region: identity hierarchy tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_user_to_ueber_group_and_remove_again(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    add_many_test_ueber_groups,
):
    """Tests adding user to an ueber-group and remove again."""
    app_override_provide_http_token_payload

    existing_user = await add_one_azure_test_user(0)

    mocked_ueber_groups = await add_many_test_ueber_groups()

    response = await async_client.post(
        f"/api/v1/user/{existing_user.id}/group/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 201
    created_ueber_group_membership = response.json()
    assert created_ueber_group_membership["parent_id"] == str(mocked_ueber_groups[1].id)
    assert created_ueber_group_membership["child_id"] == str(existing_user.id)
    assert created_ueber_group_membership["inherit"] is True

    ueber_group_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert ueber_group_response.status_code == 200
    ueber_group = UeberGroupRead(**ueber_group_response.json())
    assert len(ueber_group.users) == 1
    assert any(user.id == str(existing_user.id) for user in ueber_group.users)

    # remove user from ueber group
    remove_response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}/group/{str(mocked_ueber_groups[1].id)}"
    )
    assert remove_response.status_code == 200

    ueber_group_after_delete_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert ueber_group_after_delete_response.status_code == 200
    ueber_group_after_delete = UeberGroupRead(
        **ueber_group_after_delete_response.json()
    )
    assert len(ueber_group_after_delete.users) == 0
    assert all(
        user.id != str(existing_user.id) for user in ueber_group_after_delete.users
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_users_to_ueber_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_azure_test_users: List[User],
    add_many_test_ueber_groups,
):
    """Tests bulk adding users to an ueber-group and remove some fo them again."""
    app_override_provide_http_token_payload

    existing_users = await add_many_azure_test_users()

    mocked_ueber_groups = await add_many_test_ueber_groups()

    response = await async_client.post(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(existing_users)
    for user, created_membership in zip(existing_users, created_memberships):
        assert created_membership["parent_id"] == str(mocked_ueber_groups[1].id)
        assert created_membership["child_id"] == str(user.id)
        assert created_membership["inherit"] is True

    ueber_group_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert ueber_group_response.status_code == 200
    ueber_group = UeberGroupRead(**ueber_group_response.json())
    assert len(ueber_group.users) == 5
    assert all(
        user.id in [str(existing_user.id) for existing_user in existing_users]
        for user in ueber_group.users
    )

    # bulk remove users from ueber group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users[0:2]],
    )
    assert remove_response.status_code == 200

    ueber_group_after_delete_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert ueber_group_after_delete_response.status_code == 200
    ueber_group_after_delete = UeberGroupRead(
        **ueber_group_after_delete_response.json()
    )
    assert len(ueber_group_after_delete.users) == 3
    assert any(
        user.id not in [str(existing_user.id) for existing_user in existing_users[0:2]]
        for user in ueber_group.users
    )
    expected_ids = [str(existing_user.id) for existing_user in existing_users[2:]]
    ueber_group_user_ids = [str(user.id) for user in ueber_group.users]
    assert all(user_id in ueber_group_user_ids for user_id in expected_ids)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_groups_to_ueber_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_ueber_groups,
    add_many_test_groups,
):
    """Tests bulk adding groups to an ueber-group and remove some of them again."""
    app_override_provide_http_token_payload

    mocked_groups = await add_many_test_groups()

    mocked_ueber_groups = await add_many_test_ueber_groups()

    response = await async_client.post(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}/groups",
        json=[str(group.id) for group in mocked_groups],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(mocked_groups)
    for group, created_membership in zip(mocked_groups, created_memberships):
        assert created_membership["parent_id"] == str(mocked_ueber_groups[1].id)
        assert created_membership["child_id"] == str(group.id)
        assert created_membership["inherit"] is True

    ueber_group_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert ueber_group_response.status_code == 200
    ueber_group = UeberGroupRead(**ueber_group_response.json())
    assert len(ueber_group.groups) == 4
    assert all(
        group.id in [str(mocked_group.id) for mocked_group in mocked_groups]
        for group in ueber_group.groups
    )

    # bulk remove groups from ueber group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}/groups",
        json=[str(group.id) for group in mocked_groups[0:2]],
    )
    assert remove_response.status_code == 200

    ueber_group_after_delete_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert ueber_group_after_delete_response.status_code == 200
    ueber_group_after_delete = UeberGroupRead(
        **ueber_group_after_delete_response.json()
    )
    assert len(ueber_group_after_delete.groups) == 2
    assert any(
        group.id not in [str(mocked_group.id) for mocked_group in mocked_groups[0:2]]
        for group in ueber_group.groups
    )
    expected_ids = [str(mocked_group.id) for mocked_group in mocked_groups[2:]]
    ueber_group_group_ids = [str(group.id) for group in ueber_group.groups]
    assert all(group_id in ueber_group_group_ids for group_id in expected_ids)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_user_to_group_and_remove_again(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    add_many_test_groups: List[Group],
):
    """Tests adding user to a group and remove again."""
    app_override_provide_http_token_payload

    existing_user = await add_one_azure_test_user(0)

    mocked_groups = await add_many_test_groups()

    response = await async_client.post(
        f"/api/v1/user/{existing_user.id}/group/{str(mocked_groups[3].id)}"
    )

    assert response.status_code == 201
    created_group_membership = response.json()
    assert created_group_membership["parent_id"] == str(mocked_groups[3].id)
    assert created_group_membership["child_id"] == str(existing_user.id)
    assert created_group_membership["inherit"] is True

    group_response = await async_client.get(f"/api/v1/group/{str(mocked_groups[3].id)}")

    assert group_response.status_code == 200
    group = GroupRead(**group_response.json())
    assert len(group.users) == 1
    assert any(user.id == str(existing_user.id) for user in group.users)

    # remove user from group
    remove_response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}/group/{str(mocked_groups[3].id)}"
    )
    assert remove_response.status_code == 200

    group_after_delete_response = await async_client.get(
        f"/api/v1/group/{str(mocked_groups[3].id)}"
    )

    assert group_after_delete_response.status_code == 200
    group_after_delete = GroupRead(**group_after_delete_response.json())
    assert len(group_after_delete.users) == 0
    assert all(user.id != str(existing_user.id) for user in group_after_delete.users)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_users_to_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_azure_test_users: List[User],
    add_many_test_groups,
):
    """Tests bulk adding users to a group and bulk remove some of them again."""
    app_override_provide_http_token_payload

    existing_users = await add_many_azure_test_users()

    mocked_groups = await add_many_test_groups()

    response = await async_client.post(
        f"/api/v1/group/{str(mocked_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(existing_users)
    for user, created_membership in zip(existing_users, created_memberships):
        assert created_membership["parent_id"] == str(mocked_groups[1].id)
        assert created_membership["child_id"] == str(user.id)
        assert created_membership["inherit"] is True

    group_response = await async_client.get(f"/api/v1/group/{str(mocked_groups[1].id)}")

    assert group_response.status_code == 200
    group = GroupRead(**group_response.json())
    assert len(group.users) == 5
    assert all(
        user.id in [str(existing_user.id) for existing_user in existing_users]
        for user in group.users
    )

    # bulk remove users from group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/group/{str(mocked_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users[0:2]],
    )
    assert remove_response.status_code == 200

    group_after_delete_response = await async_client.get(
        f"/api/v1/group/{str(mocked_groups[1].id)}"
    )

    assert group_after_delete_response.status_code == 200
    group_after_delete = GroupRead(**group_after_delete_response.json())
    assert len(group_after_delete.users) == 3
    assert any(
        user.id not in [str(existing_user.id) for existing_user in existing_users[0:2]]
        for user in group.users
    )
    expected_ids = [str(existing_user.id) for existing_user in existing_users[2:]]
    group_user_ids = [str(user.id) for user in group.users]
    assert all(user_id in group_user_ids for user_id in expected_ids)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_sub_groups_to_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_groups,
    add_many_test_sub_groups,
):
    """Tests bulk adding sub-groups to a group and bulk remove some of them again."""
    app_override_provide_http_token_payload

    mocked_sub_groups = await add_many_test_sub_groups()

    mocked_groups = await add_many_test_groups()

    response = await async_client.post(
        f"/api/v1/group/{str(mocked_groups[2].id)}/subgroups",
        json=[str(sub_group.id) for sub_group in mocked_sub_groups],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(mocked_sub_groups)
    for sub_group, created_membership in zip(mocked_sub_groups, created_memberships):
        assert created_membership["parent_id"] == str(mocked_groups[2].id)
        assert created_membership["child_id"] == str(sub_group.id)
        assert created_membership["inherit"] is True

    group_response = await async_client.get(f"/api/v1/group/{str(mocked_groups[2].id)}")

    assert group_response.status_code == 200
    group = GroupRead(**group_response.json())
    assert len(group.sub_groups) == 5
    assert all(
        sub_group.id
        in [str(mocked_sub_group.id) for mocked_sub_group in mocked_sub_groups]
        for sub_group in group.sub_groups
    )

    # bulk remove sub-groups from group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/group/{str(mocked_groups[2].id)}/subgroups",
        json=[str(sub_group.id) for sub_group in mocked_sub_groups[0:2]],
    )
    assert remove_response.status_code == 200

    group_after_delete_response = await async_client.get(
        f"/api/v1/group/{str(mocked_groups[2].id)}"
    )

    assert group_after_delete_response.status_code == 200
    group_after_delete = GroupRead(**group_after_delete_response.json())
    assert len(group_after_delete.sub_groups) == 3
    assert any(
        sub_group.id
        not in [str(mocked_sub_group.id) for mocked_sub_group in mocked_sub_groups[0:2]]
        for sub_group in group.sub_groups
    )
    expected_ids = [
        str(mocked_sub_group.id) for mocked_sub_group in mocked_sub_groups[2:]
    ]
    group_sub_group_ids = [str(sub_group.id) for sub_group in group.sub_groups]
    assert all(sub_group_id in group_sub_group_ids for sub_group_id in expected_ids)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_user_to_sub_group_and_remove_again(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    add_many_test_sub_groups,
):
    """Tests adding users to a sub-group."""
    app_override_provide_http_token_payload

    existing_user = await add_one_azure_test_user(0)

    mocked_sub_groups = await add_many_test_sub_groups()

    response = await async_client.post(
        f"/api/v1/user/{existing_user.id}/group/{str(mocked_sub_groups[2].id)}"
    )

    assert response.status_code == 201
    created_sub_group_membership = response.json()
    assert created_sub_group_membership["parent_id"] == str(mocked_sub_groups[2].id)
    assert created_sub_group_membership["child_id"] == str(existing_user.id)
    assert created_sub_group_membership["inherit"] is True

    sub_group_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[2].id)}"
    )

    assert sub_group_response.status_code == 200
    sub_group = SubGroupRead(**sub_group_response.json())
    assert len(sub_group.users) == 1
    assert any(user.id == str(existing_user.id) for user in sub_group.users)

    # remove user from sub group
    remove_response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}/group/{str(mocked_sub_groups[2].id)}"
    )
    assert remove_response.status_code == 200

    sub_group_after_delete_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[2].id)}"
    )

    assert sub_group_after_delete_response.status_code == 200
    sub_group_after_delete = SubGroupRead(**sub_group_after_delete_response.json())
    assert len(sub_group_after_delete.users) == 0
    assert all(
        user.id != str(existing_user.id) for user in sub_group_after_delete.users
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_users_to_sub_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_azure_test_users: List[User],
    add_many_test_sub_groups,
):
    """Tests bulk adding users to a sub-group and remove some of them again."""
    app_override_provide_http_token_payload

    existing_users = await add_many_azure_test_users()

    mocked_sub_groups = await add_many_test_sub_groups()

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(existing_users)
    for user, created_membership in zip(existing_users, created_memberships):
        assert created_membership["parent_id"] == str(mocked_sub_groups[1].id)
        assert created_membership["child_id"] == str(user.id)
        assert created_membership["inherit"] is True

    sub_group_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[1].id)}"
    )

    assert sub_group_response.status_code == 200
    sub_group = UeberGroupRead(**sub_group_response.json())
    assert len(sub_group.users) == 5
    assert all(
        user.id in [str(existing_user.id) for existing_user in existing_users]
        for user in sub_group.users
    )

    # bulk remove users from sub group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/subgroup/{str(mocked_sub_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users[0:2]],
    )
    assert remove_response.status_code == 200

    sub_group_after_delete_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[1].id)}"
    )

    assert sub_group_after_delete_response.status_code == 200
    sub_group_after_delete = SubGroupRead(**sub_group_after_delete_response.json())
    assert len(sub_group_after_delete.users) == 3
    assert any(
        user.id not in [str(existing_user.id) for existing_user in existing_users[0:2]]
        for user in sub_group.users
    )
    expected_ids = [str(existing_user.id) for existing_user in existing_users[2:]]
    sub_group_user_ids = [str(user.id) for user in sub_group.users]
    assert all(user_id in sub_group_user_ids for user_id in expected_ids)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_sub_sub_groups_to_sub_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_sub_groups,
    add_many_test_sub_sub_groups,
):
    """Tests bulk adding sub-sub-groups to a sub-group and bulk remove some of them again."""
    app_override_provide_http_token_payload

    mocked_sub_sub_groups = await add_many_test_sub_sub_groups()

    mocked_sub_groups = await add_many_test_sub_groups()

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_groups[3].id)}/subsubgroups",
        json=[str(sub_sub_group.id) for sub_sub_group in mocked_sub_sub_groups],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(mocked_sub_sub_groups)
    for sub_sub_group, created_membership in zip(
        mocked_sub_sub_groups, created_memberships
    ):
        assert created_membership["parent_id"] == str(mocked_sub_groups[3].id)
        assert created_membership["child_id"] == str(sub_sub_group.id)
        assert created_membership["inherit"] is True

    sub_group_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[3].id)}"
    )

    assert sub_group_response.status_code == 200
    sub_group = SubGroupRead(**sub_group_response.json())
    assert len(sub_group.sub_sub_groups) == 6
    assert all(
        sub_sub_group.id
        in [
            str(mocked_sub_sub_group.id)
            for mocked_sub_sub_group in mocked_sub_sub_groups
        ]
        for sub_sub_group in sub_group.sub_sub_groups
    )

    # bulk remove sub-sub-groups from sub-group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/subgroup/{str(mocked_sub_groups[3].id)}/subsubgroups",
        json=[str(sub_sub_group.id) for sub_sub_group in mocked_sub_sub_groups[0:2]],
    )
    assert remove_response.status_code == 200

    sub_group_after_delete_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[3].id)}"
    )

    assert sub_group_after_delete_response.status_code == 200
    sub_group_after_delete = SubGroupRead(**sub_group_after_delete_response.json())
    assert len(sub_group_after_delete.sub_sub_groups) == 4
    assert any(
        sub_sub_group.id
        not in [
            str(mocked_sub_sub_group.id)
            for mocked_sub_sub_group in mocked_sub_sub_groups[0:2]
        ]
        for sub_sub_group in sub_group.sub_sub_groups
    )
    expected_ids = [
        str(mocked_sub_sub_group.id)
        for mocked_sub_sub_group in mocked_sub_sub_groups[2:]
    ]
    sub_group_sub_sub_group_ids = [
        str(sub_sub_group.id) for sub_sub_group in sub_group_after_delete.sub_sub_groups
    ]
    assert all(
        sub_sub_group_id in sub_group_sub_sub_group_ids
        for sub_sub_group_id in expected_ids
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_user_to_sub_sub_group_and_remove_again(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    add_many_test_sub_sub_groups,
):
    """Tests adding user to a sub-sub-group and remove again."""
    app_override_provide_http_token_payload

    existing_user = await add_one_azure_test_user(0)

    mocked_sub_sub_groups = await add_many_test_sub_sub_groups()

    response = await async_client.post(
        f"/api/v1/user/{existing_user.id}/group/{str(mocked_sub_sub_groups[0].id)}"
    )

    assert response.status_code == 201
    created_sub_sub_group_membership = response.json()
    assert created_sub_sub_group_membership["parent_id"] == str(
        mocked_sub_sub_groups[0].id
    )
    assert created_sub_sub_group_membership["child_id"] == str(existing_user.id)
    assert created_sub_sub_group_membership["inherit"] is True

    sub_sub_group_response = await async_client.get(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[0].id)}"
    )

    assert sub_sub_group_response.status_code == 200
    sub_sub_group = SubSubGroupRead(**sub_sub_group_response.json())
    assert len(sub_sub_group.users) == 1
    assert any(user.id == str(existing_user.id) for user in sub_sub_group.users)

    # remove user from sub-sub-group
    remove_response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}/group/{str(mocked_sub_sub_groups[0].id)}"
    )
    assert remove_response.status_code == 200

    sub_sub_group_after_delete_response = await async_client.get(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[0].id)}"
    )

    assert sub_sub_group_after_delete_response.status_code == 200
    sub_sub_group_after_delete = SubSubGroupRead(
        **sub_sub_group_after_delete_response.json()
    )
    assert len(sub_sub_group_after_delete.users) == 0
    assert all(
        user.id != str(existing_user.id) for user in sub_sub_group_after_delete.users
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_bulk_add_users_to_sub_sub_group_and_bulk_remove(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_azure_test_users: List[User],
    add_many_test_sub_sub_groups,
):
    """Tests bulk adding users to a sub-sub-group"""
    app_override_provide_http_token_payload

    existing_users = await add_many_azure_test_users()

    mocked_sub_sub_groups = await add_many_test_sub_sub_groups()

    response = await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users],
    )

    assert response.status_code == 201
    created_memberships = response.json()
    assert len(created_memberships) == len(existing_users)
    for user, created_membership in zip(existing_users, created_memberships):
        assert created_membership["parent_id"] == str(mocked_sub_sub_groups[1].id)
        assert created_membership["child_id"] == str(user.id)
        assert created_membership["inherit"] is True

    sub_sub_group_response = await async_client.get(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[1].id)}"
    )

    assert sub_sub_group_response.status_code == 200
    sub_sub_group = SubSubGroupRead(**sub_sub_group_response.json())
    assert len(sub_sub_group.users) == 5
    assert all(
        user.id in [str(existing_user.id) for existing_user in existing_users]
        for user in sub_sub_group.users
    )

    # bulk remove users from sub-sub group
    remove_response = await async_client.request(
        "delete",
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[1].id)}/users",
        json=[str(user.id) for user in existing_users[0:2]],
    )
    assert remove_response.status_code == 200

    sub_sub_group_after_delete_response = await async_client.get(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[1].id)}"
    )

    assert sub_sub_group_after_delete_response.status_code == 200
    sub_sub_group_after_delete = SubSubGroupRead(
        **sub_sub_group_after_delete_response.json()
    )
    assert len(sub_sub_group_after_delete.users) == 3
    assert any(
        user.id not in [str(existing_user.id) for existing_user in existing_users[0:2]]
        for user in sub_sub_group.users
    )
    expected_ids = [str(existing_user.id) for existing_user in existing_users[2:]]
    sub_sub_group_user_ids = [str(user.id) for user in sub_sub_group.users]
    assert all(user_id in sub_sub_group_user_ids for user_id in expected_ids)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_user_to_groups_without_inheritance(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_one_azure_test_user: List[User],
    add_many_test_groups,
):
    """Tests adding users to an ueber-group, group, sub-group, and sub-sub-group."""
    app_override_provide_http_token_payload

    existing_user = await add_one_azure_test_user(0)

    mocked_groups = await add_many_test_groups()

    response = await async_client.post(
        f"/api/v1/user/{existing_user.id}/group/{str(mocked_groups[1].id)}?inherit=false"
    )

    assert response.status_code == 201
    created_hierarchy = response.json()
    assert created_hierarchy["parent_id"] == str(mocked_groups[1].id)
    assert created_hierarchy["child_id"] == str(existing_user.id)
    assert created_hierarchy["inherit"] is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_group_to_ueber_group(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_ueber_groups,
    add_many_test_groups,
):
    """Tests adding groups to an ueber-group."""
    app_override_provide_http_token_payload

    mocked_ueber_groups = await add_many_test_ueber_groups()
    mocked_groups = await add_many_test_groups()

    hierarchy_response = await async_client.post(
        f"/api/v1/group/{str(mocked_groups[1].id)}/uebergroup/{str(mocked_ueber_groups[2].id)}"
    )

    assert hierarchy_response.status_code == 201
    created_hierarchy = hierarchy_response.json()
    assert created_hierarchy["parent_id"] == str(mocked_ueber_groups[2].id)
    assert created_hierarchy["child_id"] == str(mocked_groups[1].id)

    # add another group to the ueber-group:
    await async_client.post(
        f"/api/v1/group/{str(mocked_groups[3].id)}/uebergroup/{str(mocked_ueber_groups[2].id)}"
    )

    ueber_group_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[2].id)}"
    )

    assert ueber_group_response.status_code == 200
    ueber_group = UeberGroupRead(**ueber_group_response.json())
    assert len(ueber_group.groups) == 2
    assert any(group.id == str(mocked_groups[1].id) for group in ueber_group.groups)
    assert any(group.id == str(mocked_groups[3].id) for group in ueber_group.groups)

    # remove a group from the ueber-group:
    remove_response = await async_client.delete(
        f"/api/v1/group/{str(mocked_groups[1].id)}/uebergroup/{str(mocked_ueber_groups[2].id)}"
    )
    assert remove_response.status_code == 200

    ueber_group_after_delete_response = await async_client.get(
        f"/api/v1/uebergroup/{str(mocked_ueber_groups[2].id)}"
    )

    assert ueber_group_after_delete_response.status_code == 200
    ueber_group_after_delete = UeberGroupRead(
        **ueber_group_after_delete_response.json()
    )
    assert len(ueber_group_after_delete.groups) == 1
    assert all(
        group.id != str(mocked_groups[1].id)
        for group in ueber_group_after_delete.groups
    )
    assert any(
        group.id == str(mocked_groups[3].id)
        for group in ueber_group_after_delete.groups
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_sub_group_to_group(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_groups,
    add_many_test_sub_groups,
):
    """Tests adding groups to an ueber-group."""
    app_override_provide_http_token_payload

    mocked_groups = await add_many_test_groups()
    mocked_sub_groups = await add_many_test_sub_groups()

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_groups[3].id)}/group/{str(mocked_groups[0].id)}"
    )

    assert response.status_code == 201
    created_hierarchy = response.json()
    assert created_hierarchy["parent_id"] == str(mocked_groups[0].id)
    assert created_hierarchy["child_id"] == str(mocked_sub_groups[3].id)

    group_response = await async_client.get(f"/api/v1/group/{str(mocked_groups[0].id)}")

    assert group_response.status_code == 200
    group = GroupRead(**group_response.json())
    assert any(
        sub_group.id == str(mocked_sub_groups[3].id) for sub_group in group.sub_groups
    )

    # add another sub_group to the group:
    await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_groups[0].id)}/group/{str(mocked_groups[0].id)}"
    )

    group_response = await async_client.get(f"/api/v1/group/{str(mocked_groups[0].id)}")

    assert group_response.status_code == 200
    group = GroupRead(**group_response.json())
    assert len(group.sub_groups) == 2
    assert any(
        sub_group.id == str(mocked_sub_groups[3].id) for sub_group in group.sub_groups
    )
    assert any(
        sub_group.id == str(mocked_sub_groups[0].id) for sub_group in group.sub_groups
    )

    # remove a sub_group from the group:
    remove_response = await async_client.delete(
        f"/api/v1/subgroup/{str(mocked_sub_groups[0].id)}/group/{str(mocked_groups[0].id)}"
    )
    assert remove_response.status_code == 200

    group_after_delete_response = await async_client.get(
        f"/api/v1/group/{str(mocked_groups[0].id)}"
    )

    assert group_after_delete_response.status_code == 200
    group_after_delete = GroupRead(**group_after_delete_response.json())
    assert len(group_after_delete.sub_groups) == 1
    assert all(
        sub_group.id != str(mocked_sub_groups[0].id)
        for sub_group in group_after_delete.sub_groups
    )
    assert any(
        sub_group.id == str(mocked_sub_groups[3].id)
        for sub_group in group_after_delete.sub_groups
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_sub_sub_group_to_sub_group(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_sub_groups,
    add_many_test_sub_sub_groups,
):
    """Tests adding groups to an ueber-group."""
    app_override_provide_http_token_payload

    mocked_sub_groups = await add_many_test_sub_groups()
    mocked_sub_sub_groups = await add_many_test_sub_sub_groups()

    response = await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[4].id)}/subgroup/{str(mocked_sub_groups[4].id)}"
    )

    assert response.status_code == 201
    created_hierarchy = response.json()
    assert created_hierarchy["parent_id"] == str(mocked_sub_groups[4].id)
    assert created_hierarchy["child_id"] == str(mocked_sub_sub_groups[4].id)

    sub_group_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[4].id)}"
    )

    assert sub_group_response.status_code == 200
    sub_group = SubGroupRead(**sub_group_response.json())
    assert any(
        sub_sub_group.id == str(mocked_sub_sub_groups[4].id)
        for sub_sub_group in sub_group.sub_sub_groups
    )

    # add another sub_sub_group to the sub_group:
    await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[3].id)}/subgroup/{str(mocked_sub_groups[4].id)}"
    )

    sub_group_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[4].id)}"
    )

    assert sub_group_response.status_code == 200
    sub_group = SubGroupRead(**sub_group_response.json())
    assert len(sub_group.sub_sub_groups) == 2
    assert any(
        sub_sub_group.id == str(mocked_sub_sub_groups[3].id)
        for sub_sub_group in sub_group.sub_sub_groups
    )
    assert any(
        sub_sub_group.id == str(mocked_sub_sub_groups[4].id)
        for sub_sub_group in sub_group.sub_sub_groups
    )

    # remove a sub_sub_group from the sub_group:
    remove_response = await async_client.delete(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[4].id)}/subgroup/{str(mocked_sub_groups[4].id)}"
    )
    assert remove_response.status_code == 200

    sub_group_after_delete_response = await async_client.get(
        f"/api/v1/subgroup/{str(mocked_sub_groups[4].id)}"
    )

    assert sub_group_after_delete_response.status_code == 200
    sub_group_after_delete = SubGroupRead(**sub_group_after_delete_response.json())
    assert len(sub_group_after_delete.sub_sub_groups) == 1
    assert all(
        sub_sub_group.id != str(mocked_sub_sub_groups[4].id)
        for sub_sub_group in sub_group_after_delete.sub_sub_groups
    )
    assert any(
        sub_sub_group.id == str(mocked_sub_sub_groups[3].id)
        for sub_sub_group in sub_group_after_delete.sub_sub_groups
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_prohibited_groups_to_ueber_group(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_ueber_groups,
    add_many_test_sub_groups,
    add_many_test_sub_sub_groups,
):
    """Tests adding groups to an ueber-group."""
    app_override_provide_http_token_payload

    mocked_ueber_groups = await add_many_test_ueber_groups()
    mocked_sub_groups = await add_many_test_sub_groups()
    mocked_sub_sub_groups = await add_many_test_sub_sub_groups()

    response = await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[3].id)}/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

    response = await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[3].id)}/subgroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_groups[3].id)}/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_sub_groups[3].id)}/group/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_add_prohibited_groups_to_group(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_many_test_ueber_groups,
    add_many_test_groups,
    add_many_test_sub_sub_groups,
):
    """Tests adding groups to an ueber-group."""
    app_override_provide_http_token_payload

    mocked_ueber_groups = await add_many_test_ueber_groups()
    mocked_groups = await add_many_test_groups()
    mocked_sub_sub_groups = await add_many_test_sub_sub_groups()

    response = await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[3].id)}/group/{str(mocked_groups[2].id)}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

    response = await async_client.post(
        f"/api/v1/subsubgroup/{str(mocked_sub_sub_groups[3].id)}/subgroup/{str(mocked_groups[2].id)}"
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_sub_groups[3].id)}/uebergroup/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

    response = await async_client.post(
        f"/api/v1/subgroup/{str(mocked_sub_sub_groups[3].id)}/group/{str(mocked_ueber_groups[1].id)}"
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_user_access_through_inheritance_from_direct_group_membership(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_test_user,
    mock_guards,
    add_many_test_protected_resources,
    add_one_test_access_policy,
    add_many_test_groups,
    current_user_from_azure_token,
):
    """Tests user access through inheritance from direct group membership."""
    app_override_provide_http_token_payload

    current_user = current_test_user

    mocked_groups = await add_many_test_groups()

    created_hierarchy = await post_existing_user_to_group(
        current_user.user_id,
        mocked_groups[1].id,
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_hierarchy.parent_id == mocked_groups[1].id
    assert created_hierarchy.child_id == current_user.user_id
    assert created_hierarchy.inherit is True

    mocked_protected_resources = await add_many_test_protected_resources()

    # Give read access to the group to the resource:
    policy = {
        "resource_id": str(mocked_protected_resources[2].id),
        "identity_id": str(mocked_groups[1].id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}"
    )
    assert response.status_code == 200
    read_resource = ProtectedResourceRead(**response.json())
    assert read_resource.id == mocked_protected_resources[2].id
    assert read_resource.name == mocked_protected_resources[2].name
    assert read_resource.description == mocked_protected_resources[2].description

    current_admin_user = await current_user_from_azure_token(token_admin_read_write)
    async with AccessLoggingCRUD() as crud:
        access_log = await crud.read_resource_last_accessed_at(
            current_admin_user,
            resource_id=mocked_protected_resources[2].id,
        )

    assert access_log.resource_id == mocked_protected_resources[2].id
    assert access_log.identity_id == current_user.user_id
    assert access_log.action == "read"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_user2_read_write],
    indirect=True,
)
async def test_user_access_prohibited_through_inheritance_missing_group_membership(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_test_user,
    mock_guards,
    add_many_test_protected_resources,
    add_one_test_access_policy,
    add_many_test_groups,
    current_user_from_azure_token,
):
    """Tests user access through inheritance from direct group membership."""
    app_override_provide_http_token_payload

    current_user = current_test_user

    mocked_groups = await add_many_test_groups()

    created_hierarchy = await post_existing_user_to_group(
        current_user.user_id,
        mocked_groups[1].id,
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_hierarchy.parent_id == mocked_groups[1].id
    assert created_hierarchy.child_id == current_user.user_id
    assert created_hierarchy.inherit is True

    mocked_protected_resources = await add_many_test_protected_resources()

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}"
    )
    assert response.status_code == 404
    assert response.text == '{"detail":"ProtectedResource not found."}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_user_access_through_inheritance_from_indirect_group_membership(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_test_user,
    mock_guards,
    add_many_test_protected_resources,
    add_one_test_access_policy,
    add_many_test_ueber_groups,
    add_many_test_groups,
    add_many_test_sub_groups,
    current_user_from_azure_token,
):
    """Tests user access through inheritance from direct group membership."""
    app_override_provide_http_token_payload

    current_user = current_test_user

    mocked_ueber_groups = await add_many_test_ueber_groups()
    mocked_groups = await add_many_test_groups()
    mocked_sub_groups = await add_many_test_sub_groups()

    # Adding user to sub-group:
    created_user_sub_group_membership = await post_existing_users_to_subgroup(
        mocked_sub_groups[2].id,
        [current_user.user_id],
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_user_sub_group_membership[0].parent_id == mocked_sub_groups[2].id
    assert created_user_sub_group_membership[0].child_id == current_user.user_id
    assert created_user_sub_group_membership[0].inherit is True

    # Adding sub-group to group:
    created_sub_group_group_membership = await post_existing_subgroup_to_group(
        mocked_sub_groups[2].id,
        mocked_groups[1].id,
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_sub_group_group_membership.parent_id == mocked_groups[1].id
    assert created_sub_group_group_membership.child_id == mocked_sub_groups[2].id
    assert created_sub_group_group_membership.inherit is True

    # Adding group to ueber-group:
    created_group_ueber_group_membership = await post_existing_groups_to_uebergroup(
        mocked_ueber_groups[0].id,
        [mocked_groups[1].id],
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert (
        created_group_ueber_group_membership[0].parent_id == mocked_ueber_groups[0].id
    )
    assert created_group_ueber_group_membership[0].child_id == mocked_groups[1].id
    assert created_group_ueber_group_membership[0].inherit is True

    mocked_protected_resources = await add_many_test_protected_resources()

    # Give read access to the group to the resource:
    policy = {
        "resource_id": str(mocked_protected_resources[2].id),
        "identity_id": str(mocked_ueber_groups[0].id),
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}"
    )
    assert response.status_code == 200
    read_resource = ProtectedResourceRead(**response.json())
    assert read_resource.id == mocked_protected_resources[2].id
    assert read_resource.name == mocked_protected_resources[2].name
    assert read_resource.description == mocked_protected_resources[2].description

    current_admin_user = await current_user_from_azure_token(token_admin_read_write)
    async with AccessLoggingCRUD() as crud:
        access_log = await crud.read_resource_last_accessed_at(
            current_admin_user,
            resource_id=mocked_protected_resources[2].id,
        )

    assert access_log.resource_id == mocked_protected_resources[2].id
    assert access_log.identity_id == current_user.user_id
    assert access_log.action == "read"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_access_prohibited_from_indirect_group_membership_missing_inheritance(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_test_user,
    mock_guards,
    add_many_test_protected_resources,
    add_one_test_access_policy,
    add_many_test_ueber_groups,
    add_many_test_groups,
    add_many_test_sub_groups,
    current_user_from_azure_token,
):
    """Tests user access through inheritance from direct group membership."""
    app_override_provide_http_token_payload

    current_user = current_test_user

    mocked_ueber_groups = await add_many_test_ueber_groups()
    mocked_groups = await add_many_test_groups()
    mocked_sub_groups = await add_many_test_sub_groups()

    # Adding user to sub-group:
    created_user_sub_group_membership = await post_existing_user_to_group(
        current_user.user_id,
        mocked_sub_groups[2].id,
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_user_sub_group_membership.parent_id == mocked_sub_groups[2].id
    assert created_user_sub_group_membership.child_id == current_user.user_id
    assert created_user_sub_group_membership.inherit is True

    # Adding sub-group to group:
    created_sub_group_group_membership = await post_existing_subgroup_to_group(
        mocked_sub_groups[2].id,
        mocked_groups[1].id,
        inherit=False,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_sub_group_group_membership.parent_id == mocked_groups[1].id
    assert created_sub_group_group_membership.child_id == mocked_sub_groups[2].id
    assert created_sub_group_group_membership.inherit is False

    # Adding group to ueber-group:
    created_group_ueber_group_membership = await post_existing_groups_to_uebergroup(
        mocked_ueber_groups[0].id,
        [mocked_groups[1].id],
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert (
        created_group_ueber_group_membership[0].parent_id == mocked_ueber_groups[0].id
    )
    assert created_group_ueber_group_membership[0].child_id == mocked_groups[1].id
    assert created_group_ueber_group_membership[0].inherit is True

    mocked_protected_resources = await add_many_test_protected_resources()

    # Give read access to the group to the resource:
    policy = {
        "resource_id": str(mocked_protected_resources[2].id),
        "identity_id": str(mocked_ueber_groups[0].id),
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}"
    )
    assert response.status_code == 404
    assert response.text == '{"detail":"ProtectedResource not found."}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_access_prohibited_after_deleting_group_with_direct_group_membership(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_test_user,
    mock_guards,
    add_many_test_protected_resources,
    add_one_test_access_policy,
    add_many_test_groups,
    current_user_from_azure_token,
):
    """Tests user access through inheritance from direct group membership."""
    app_override_provide_http_token_payload

    current_user = current_test_user

    mocked_groups = await add_many_test_groups()

    created_hierarchy = await post_existing_user_to_group(
        str(current_user.user_id),
        str(mocked_groups[1].id),
        inherit=True,
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )
    assert created_hierarchy.parent_id == mocked_groups[1].id
    assert created_hierarchy.child_id == current_user.user_id
    assert created_hierarchy.inherit is True

    mocked_protected_resources = await add_many_test_protected_resources()

    # Give read access to the group to the resource:
    policy = {
        "resource_id": str(mocked_protected_resources[2].id),
        "identity_id": str(mocked_groups[1].id),
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}"
    )
    assert response.status_code == 200
    read_resource = ProtectedResourceRead(**response.json())
    assert read_resource.id == mocked_protected_resources[2].id
    assert read_resource.name == mocked_protected_resources[2].name
    assert read_resource.description == mocked_protected_resources[2].description

    current_admin_user = await current_user_from_azure_token(token_admin_read_write)
    async with AccessLoggingCRUD() as crud:
        access_log = await crud.read_resource_last_accessed_at(
            current_admin_user,
            resource_id=mocked_protected_resources[2].id,
        )

    assert access_log.resource_id == mocked_protected_resources[2].id
    assert access_log.identity_id == current_user.user_id
    assert access_log.action == "read"

    # Delete group:
    await delete_group(
        str(mocked_groups[1].id),
        token_payload=token_admin_read_write,
        guards=mock_guards(scopes=["api.write"], roles=["Admin"]),
    )

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}"
    )
    assert response.status_code == 404
    assert response.text == '{"detail":"ProtectedResource not found."}'


# endregion identity hierarchy tests
