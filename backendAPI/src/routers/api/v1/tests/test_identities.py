import uuid
from datetime import datetime, timedelta
from typing import List

from pprint import pprint
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action, CurrentUserData
from crud.access import AccessLoggingCRUD
from models.identity import (
    User,
    UserRead,
    UeberGroup,
    UeberGroupRead,
    Group,
    GroupRead,
    SubGroup,
    SubGroupRead,
)
from routers.api.v1.identities import get_user_by_id
from tests.utils import (
    current_user_data_admin,
    many_test_azure_users,
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
    token_user1_read_write,
    token_user1_read_groups,
    token_user1_read_write_groups,
    token_user2_read,
    token_user2_read_write,
    many_test_ueber_groups,
    many_test_groups,
    many_test_sub_groups,
    many_test_sub_sub_groups,
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
# - all endpoints of group
# - all endpoints of sub-group
# - all endpoints of sub-sub-group
# - add user to ueber-group group, sub-group, sub-sub-group
# - add group to ueber-group
# - add sub-group to group,
# - add sub-sub-group to sub-group
# - access to resource through inheritance (user from any group)
# - access to resource through inheritance through multiple generations (user in ueber-group can access resource in sub-sub-group)
# - user inherits access to resource from group, group gets deleted, user no longer has access to resource

# region: ## POST tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    mock_guards,
    current_user_from_azure_token,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

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

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        created_user.id, mocked_get_azure_token_payload, mock_guards(roles=["User"])
    )
    assert db_user is not None
    assert db_user.id is not None
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[2]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[2]["azure_tenant_id"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    mock_guards,
    current_user_from_azure_token,
):
    """Tests posting a integer user_id to user_post endpoint fails"""
    app_override_get_azure_payload_dependency

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

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        created_user.id, mocked_get_azure_token_payload, mock_guards(roles=["User"])
    )
    assert db_user.id == uuid.UUID(created_user.id)
    assert db_user.id != 1
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[2]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[2]["azure_tenant_id"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    mock_guards,
    current_user_from_azure_token,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
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

    current_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
        created_user.id, mocked_get_azure_token_payload, mock_guards(roles=["User"])
    )
    assert db_user.id == uuid.UUID(created_user.id)
    assert db_user.id != uuid.UUID(test_uuid)
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[2]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[2]["azure_tenant_id"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
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
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
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
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_users(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_azure_test_users: List[User],
):
    """Test GET one user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_azure_test_users: List[User],
):
    """Test GET all users"""

    # mocks the access token:
    app_override_get_azure_payload_dependency

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
    "mocked_get_azure_token_payload",
    [
        # token_user1_read,
        # token_user1_read_write,
        token_user1_read_write_groups,
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    # the target user:
    user_in_database = await add_one_azure_test_user(0)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

    policy = {
        "resource_id": str(user_in_database.id),
        "identity_id": str(accessing_user.user_id),
        "action": Action.read,
    }
    await add_one_test_access_policy(policy)

    groups_for_user_in_database = many_test_azure_users[0]["groups"]
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
    "mocked_get_azure_token_payload",
    [
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id_with_partial_access_to_other_users_groups(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    # the target user:
    user_in_database = await add_one_azure_test_user(0)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
    assert len(modelled_response_user.azure_groups) == 2
    modelled_response_user.azure_groups = sorted(
        modelled_response_user.azure_groups, key=lambda x: x.id
    )

    assert modelled_response_user.azure_groups[0].id == uuid.UUID(
        groups_for_user_in_database[0]
    )
    assert modelled_response_user.azure_groups[1].id == uuid.UUID(
        groups_for_user_in_database[1]
    )

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
    "mocked_get_azure_token_payload",
    [
        token_user2_read,
        token_user2_read_write,
    ],
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id_with_no_access_to_other_users_groups(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    # the target user:
    user_in_database = await add_one_azure_test_user(0)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
    "mocked_get_azure_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_gets_another_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [token_user1_read_groups, token_admin_read],
    # here the admin get's itself => last_accessed_at should change!
    indirect=True,
)
async def test_user_gets_user_by_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    current_user_from_azure_token,
    add_one_test_access_policy,
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    # the target user:
    user_in_database = await add_one_azure_test_user(0)
    # the accessing user:
    accessing_user = await current_user_from_azure_token(mocked_get_azure_token_payload)

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
    "mocked_get_azure_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_user_by_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_gets_another_user_by_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test a user GETs it's another user id by its user id."""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = await add_one_azure_test_user(0)

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = await add_one_azure_test_user(0)

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


# endregion: ## GET tests

# region: ## PUT tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_put_user(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = await add_one_azure_test_user(0)

    existing_db_user = await get_user_by_id(
        str(existing_user.id), token_admin_read, mock_guards(roles=["User"])
    )
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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_put_user_from_admin(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    mock_guards,
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = await add_one_azure_test_user(2)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_get_azure_token_payload,
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

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    # refactored into: updating a user needs Admin roles
    indirect=True,
)
async def test_put_user_with_integer_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    mock_guards,
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = await add_one_azure_test_user(0)
    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_get_azure_token_payload,
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

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    # refactored into: updating a user needs Admin roles
    indirect=True,
)
async def test_admin_put_user_with_uuid_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    mock_guards,
):
    """Tests put user endpoint"""

    test_uuid = str(uuid.uuid4())

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = await add_one_azure_test_user(0)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_get_azure_token_payload,
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

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.time > created_at
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
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
            **token_payload_scope_api_read_write,
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
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_another_user(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = await add_one_azure_test_user(0)

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
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}


# endregion: ## PUT tests

# region: ## DELETE tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_deletes_itself(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test user deletes itself"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_deletes_user(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mocked_get_azure_token_payload,
    mock_guards,
):
    """Test admin deletes a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = await add_one_azure_test_user(0)

    existing_db_user = await get_user_by_id(
        str(existing_user.id),
        mocked_get_azure_token_payload,
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
    "mocked_get_azure_token_payload",
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
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: User,
    mock_guards,
):
    """Test deleting a user with invalid token fails"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    # TBD: use user2 here somewhere?
    [token_user1_read_write],
    indirect=True,
)
async def test_user_deletes_another_user(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
    mock_guards,
):
    """Test delete another user fails"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_ueber_group_endpoints(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_ueber_groups,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

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
        mocked_get_azure_token_payload
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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_group_endpoints(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_groups,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the group
    response = await async_client.post(
        "/api/v1/group/",
        json=many_test_groups[0],
    )

    assert response.status_code == 201
    created_group = Group(**response.json())
    assert created_group.id is not None
    assert created_group.name == many_test_groups[0]["name"]
    assert created_group.description == many_test_groups[0]["description"]

    # add some more groups:
    # note: the first one is going to be double with different id's
    mocked_groups = await add_many_test_groups(mocked_get_azure_token_payload)
    created_group.id = uuid.UUID(created_group.id)
    expected_groups = [created_group] + mocked_groups
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
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_all_sub_group_endpoints(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_sub_groups,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the sub-group
    response = await async_client.post(
        "/api/v1/subgroup/",
        json=many_test_sub_groups[0],
    )

    assert response.status_code == 201
    created_sub_group = UeberGroup(**response.json())
    assert created_sub_group.id is not None
    assert created_sub_group.name == many_test_sub_groups[0]["name"]
    assert created_sub_group.description == many_test_sub_groups[0]["description"]

    # add some more sub groups:
    # note: the first one is going to be double with different id's
    mocked_sub_groups = await add_many_test_sub_groups(mocked_get_azure_token_payload)
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

# endregion: Sub-sub Group tests


# region identity hierarchy tests:

# # TBD: add users to an ueber-group
# response = await async_client.post(
#     f"/api/v1/user/{}/group/{str(mocked_ueber_groups[1].id)}",
# )

# # TBD: remove a user from an ueber-group

# # TBD: Delete ueber-group with attached users - make sure users afterwards don't have inherited rights any more


# # TBD: add groups to an ueber-group

# # TBD: remove a group from an ueber-group

# endregion identity hierarchy tests
