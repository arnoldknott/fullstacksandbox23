# from unittest.mock import AsyncMock, patch

import pytest
import uuid
from typing import List
from crud.identity import UserCRUD
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from models.identity import User, UserRead
from models.access import AccessPolicy
from fastapi import FastAPI
from tests.utils import (
    token_user1_read,
    token_user1_write,
    token_user1_read_write,
    token_admin,
    token_admin_read,
    token_admin_write,
    token_admin_read_write,
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_roles_admin,
    token_payload_roles_user,
    token_payload_scope_api_read,
    token_payload_scope_api_write,
    token_payload_scope_api_read_write,
    token_payload_one_group,
    one_test_user,
    many_test_users,
)
from routers.api.v1.user import get_user_by_id

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
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        json=many_test_users[0],
    )

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == many_test_users[0]["azure_user_id"]
    assert created_user.azure_tenant_id == many_test_users[0]["azure_tenant_id"]

    # Verify that the user was created in the database
    # TBD: don't use the CRUD, but the API to get the user!
    db_user = await get_user_by_id(created_user.id, mocked_get_azure_token_payload)
    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_azure_user_id(many_test_users[0]["azure_user_id"])
    assert db_user is not None
    assert db_user.id is not None
    assert db_user.azure_user_id == uuid.UUID(many_test_users[0]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(many_test_users[0]["azure_tenant_id"])
    assert db_user.last_accessed_at is not None

    # db_user_json = jsonable_encoder(db_user)
    # assert "id" in db_user_json
    # assert "last_accessed_at" in db_user_json
    # assert "last_accessed_at" != None
    # assert db_user_json["azure_user_id"] == many_test_users[0]["azure_user_id"]
    # assert db_user_json["azure_tenant_id"] == many_test_users[0]["azure_tenant_id"]


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
):
    """Tests posting a integer user_id to user_post endpoint fails"""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        json={**many_test_users[0], "id": 1},
    )

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == many_test_users[0]["azure_user_id"]
    assert created_user.azure_tenant_id == many_test_users[0]["azure_tenant_id"]

    # Verify that the user was created in the database
    db_user = await get_user_by_id(created_user.id, mocked_get_azure_token_payload)
    assert db_user.id == uuid.UUID(created_user.id)
    assert db_user.id != 1
    assert db_user.azure_user_id == uuid.UUID(many_test_users[0]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(many_test_users[0]["azure_tenant_id"])
    assert db_user.last_accessed_at is not None

    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_azure_user_id(many_test_users[0]["azure_user_id"])
    # assert db_user is not None
    # db_user_json = jsonable_encoder(db_user)
    # assert db_user_json["id"] != 1


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
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    test_uuid = str(uuid.uuid4())

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        json={**many_test_users[0], "id": test_uuid},
    )

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == many_test_users[0]["azure_user_id"]
    assert created_user.azure_tenant_id == many_test_users[0]["azure_tenant_id"]

    # Verify that the user was created in the database
    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_azure_user_id(many_test_users[0]["azure_user_id"])
    # assert db_user is not None
    # # db_user_json = jsonable_encoder(db_user)
    # db_user = db_user.model_dump()
    # assert "last_accessed_at" in db_user
    # assert "last_accessed_at" != None
    # assert db_user["azure_user_id"] == uuid.UUID(many_test_users[0]["azure_user_id"])
    # assert db_user["azure_tenant_id"] == uuid.UUID(
    #     many_test_users[0]["azure_tenant_id"]
    # )
    # assert db_user["id"] != uuid.UUID(test_uuid)

    # Verify that the user was created in the database
    db_user = await get_user_by_id(created_user.id, mocked_get_azure_token_payload)
    assert db_user.id == uuid.UUID(created_user.id)
    assert db_user.id != uuid.UUID(test_uuid)
    assert db_user.azure_user_id == uuid.UUID(many_test_users[0]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(many_test_users[0]["azure_tenant_id"])
    assert db_user.last_accessed_at is not None


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
        json=one_test_user,
    )

    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'

    # this would allow other users to create users, which is not allowed - only self-sign-up!:
    # assert response.status_code == 201
    # created_user = User(**response.json())
    # assert created_user.azure_user_id == one_test_user["azure_user_id"]
    # assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]

    # # Verify that the user was created in the database
    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
    # assert db_user is not None
    # db_user_json = jsonable_encoder(db_user)
    # assert "last_accessed_at" in db_user_json
    # assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
    # assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]


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
        json=one_test_user,
    )

    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


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
    # add_test_policies_for_resources: List[AccessPolicy],
    add_many_test_users: List[User],
):
    """Test GET one user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency

    # adds a user to the database, which is the one to GET:
    users = add_many_test_users
    # TBD: should not be necessary - misses the point of admin can read everything!
    # await add_test_policies_for_resources(
    #     resources=[user],
    #     actions=["read"],
    #     # TBD: switch from public to admin-owned resources
    #     publics=[True],
    # )

    response = await async_client.get("/api/v1/user/")
    assert response.status_code == 200
    database_users = response.json()
    assert len(users) == 3
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
    add_many_test_users: List[User],
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test GET all users"""

    # mocks the access token:
    app_override_get_azure_payload_dependency

    # adds users to the database
    users = add_many_test_users
    await add_test_policies_for_resources(
        resources=users,
        actions=["read"] * len(users),
        publics=[True] * len(users),
    )

    response = await async_client.get("/api/v1/user/")
    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
async def test_get_users_without_token(
    async_client: AsyncClient,
    add_one_test_user: User,
):
    """Test GET one user"""
    add_one_test_user

    response = await async_client.get("/api/v1/user/")
    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read, token_admin_read],
    # here the admin get's itself => last_accessed_at should change!
    indirect=True,
)
async def test_user_gets_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_test_user_with_groups: UserRead,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[user_in_database],
        actions=["read"],
        publics=[True],
    )

    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    assert response.status_code == 200
    response_user = response.json()
    modelled_response_user = UserRead(**response_user)
    assert "id" in response_user
    assert response_user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert response_user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    # TBD: admin access should not change the last_accessed_at!
    assert modelled_response_user.last_accessed_at > user_in_database.last_accessed_at
    assert len(response_user["azure_groups"]) == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_users_with_groups: List[UserRead],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_many_test_users_with_groups[1]

    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    assert response.status_code == 200
    response_user = response.json()
    modelled_response_user = UserRead(**response_user)
    assert "id" in response_user
    assert response_user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert response_user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    assert modelled_response_user.last_accessed_at == user_in_database.last_accessed_at
    assert len(response_user["azure_groups"]) == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_gets_another_user_by_azure_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_users: List[UserRead],
    # add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a user GETs it's own user id from it's linked azure user account"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_many_test_users[1]

    # await add_test_policies_for_resources(
    #     resources=[user_in_database],
    #     actions=["read"],
    #     publics=[True],
    # )

    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_database.azure_user_id)}"
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "User not found."
    # assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
async def test_get_user_by_azure_id_without_token(
    async_client: AsyncClient,
    add_one_test_user: User,
):
    """Test GET one user"""
    user_in_db = add_one_test_user

    response = await async_client.get(
        f"/api/v1/user/azure/{str(user_in_db.azure_user_id)}"
    )
    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read, token_admin_read],
    # here the admin get's itself => last_accessed_at should change!
    indirect=True,
)
async def test_user_gets_user_by_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_test_user_with_groups: UserRead,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[user_in_database],
        actions=["read"],
        publics=[True],
    )

    print("=== user_in_database.id ===")
    print(user_in_database.id)

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")

    assert response.status_code == 200
    user = response.json()
    modelled_response_user = UserRead(**user)
    assert "id" in user
    assert user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    # TBD: admin access should not change the last_accessed_at!
    assert modelled_response_user.last_accessed_at > user_in_database.last_accessed_at
    assert len(user["azure_groups"]) == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read],
    indirect=True,
)
async def test_admin_gets_user_by_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_users_with_groups: List[UserRead],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency

    user_in_database = add_many_test_users_with_groups[1]

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")

    assert response.status_code == 200
    user = response.json()
    modelled_response_user = UserRead(**user)
    assert "id" in user
    assert user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    # TBD: admin access should not change the last_accessed_at!
    assert modelled_response_user.last_accessed_at == user_in_database.last_accessed_at
    assert len(user["azure_groups"]) == 3


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read],
    indirect=True,
)
async def test_user_gets_another_user_by_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_users: List[UserRead],
    # add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a user GETs it's another user id by its user id."""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_many_test_users[1]
    # await add_test_policies_for_resources(
    #     resources=[user_in_database],
    #     actions=["read"],
    #     publics=[True],
    # )

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "User not found."
    # assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
async def test_get_user_by_id_without_token(
    async_client: AsyncClient,
    add_one_test_user: User,
):
    """Test GET one user"""
    user_in_db = add_one_test_user

    response = await async_client.get(f"/api/v1/user/azure/{str(user_in_db.id)}")
    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token"}'


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
    add_one_test_user_with_groups: UserRead,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[user_in_database],
        actions=["read"],
        publics=[True],
    )

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


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
    add_one_test_user_with_groups: UserRead,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a user GETs it's own user by id"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    user_in_database = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[user_in_database],
        actions=["read"],
        publics=[True],
    )

    response = await async_client.get(f"/api/v1/user/{str(user_in_database.id)}")
    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token"}'


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
    add_one_test_user_with_groups: User,
    # add_test_policies_for_resources: List[AccessPolicy],
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_one_test_user_with_groups
    # await add_test_policies_for_resources(
    #     resources=[existing_user],
    #     actions=["write"],
    #     publics=[True],
    # )

    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["is_active"] is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
        # json={"azure_user_id": str(existing_user.azure_user_id), "is_active": False},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Access denied"
    # assert response.status_code == 200
    # updated_user = User(**response.json())
    # assert updated_user.is_active is False

    # # Verify that the user was updated in the database
    # # async with UserCRUD() as crud:
    # #     db_user = await crud.read_by_id(existing_user.id)
    # response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    # content = response.json()
    # db_user = User.model_validate(content)

    # assert db_user is not None
    # assert db_user.last_accessed_at > existing_db_user["last_accessed_at"]
    # assert db_user.is_active is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_put_user_from_admin(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_users: List[User],
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_many_test_users[2]
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["is_active"] is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
        # json={"azure_user_id": str(existing_user.azure_user_id), "is_active": False},
    )
    assert response.status_code == 200
    updated_user = User(**response.json())
    assert updated_user.is_active is False

    # Verify that the user was updated in the database
    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_id(existing_user.id)
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    content = response.json()
    db_user = User.model_validate(content)
    assert db_user is not None
    assert db_user.last_accessed_at == existing_db_user["last_accessed_at"]
    assert db_user.is_active is False


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
    add_one_test_user_with_groups: User,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Tests put user endpoint"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[existing_user],
        actions=["write"],
        publics=[True],
    )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    # existing_db_user = existing_db_user.model_dump()
    # assert existing_db_user["is_active"] is True
    assert existing_db_user.is_active is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False, "id": 1},
    )
    assert response.status_code == 200
    updated_user = User(**response.json())
    assert updated_user.is_active is False

    # Verify that the user was updated in the database
    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_id(existing_user.id)
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    content = response.json()
    db_user = User.model_validate(content)
    assert db_user is not None
    assert (
        db_user.last_accessed_at > existing_db_user.last_accessed_at
    )  # ["last_accessed_at"]
    assert db_user.is_active is False
    assert db_user.id != 1
    assert db_user.id == existing_user.id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    # refactored into: updating a user needs Admin roles
    indirect=True,
)
async def test_put_user_with_uuid_user_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_test_user_with_groups: User,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Tests put user endpoint"""

    test_uuid = str(uuid.uuid4())

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[existing_user],
        actions=["write"],
        publics=[True],
    )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    # existing_db_user = existing_db_user.model_dump()
    # assert existing_db_user["is_active"] is True
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
    # async with UserCRUD() as crud:
    #     db_user = await crud.read_by_id(existing_user.id)
    response = await async_client.get(f"/api/v1/user/{str(existing_user.id)}")
    content = response.json()
    db_user = User.model_validate(content)
    assert db_user is not None
    assert (
        db_user.last_accessed_at > existing_db_user.last_accessed_at
    )  # ["last_accessed_at"]
    assert db_user.is_active is False
    assert db_user.id != uuid.UUID(test_uuid)


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
    add_one_test_user_with_groups: User,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_one_test_user_with_groups
    await add_test_policies_for_resources(
        resources=[existing_user],
        actions=["write"],
        publics=[True],
    )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["is_active"] is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
    )
    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_puts_another_user(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_users: List[User],
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test a admin updates a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_many_test_users[0]
    await add_test_policies_for_resources(
        resources=[existing_user],
        actions=["write"],
        publics=[True],
    )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["is_active"] is True

    # Make a PUT request to update the user
    response = await async_client.put(
        f"/api/v1/user/{str(existing_user.id)}",
        json={"is_active": False},
        # json={"azure_user_id": str(existing_user.azure_user_id), "is_active": False},
    )
    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


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
    add_one_test_user: User,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test user deletes itself"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_one_test_user
    await add_test_policies_for_resources(
        resources=[existing_user],
        actions=["own"],
        publics=[True],
    )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["azure_user_id"] == existing_user.azure_user_id
    assert existing_db_user["id"] is not None
    assert existing_db_user["is_active"] is True

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
    add_one_test_user: User,
):
    """Test admin deletes a user"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_one_test_user
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["azure_user_id"] == existing_user.azure_user_id
    assert existing_db_user["id"] is not None
    assert existing_db_user["is_active"] is True

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
    add_many_test_users: User,
    add_test_policies_for_resources: List[AccessPolicy],
):
    """Test deleting a user with invalid token fails"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_many_test_users[2]
    await add_test_policies_for_resources(
        resources=[existing_user],
        actions=["own"],
        publics=[True],
    )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["azure_user_id"] == existing_user.azure_user_id
    assert existing_db_user["id"] is not None
    assert existing_db_user["is_active"] is True

    # Make a DELETE request to update the user
    response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}",
    )
    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'

    # check if user is still there:
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["azure_user_id"] == existing_user.azure_user_id
    assert existing_db_user["id"] is not None
    assert existing_db_user["is_active"] is True


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
    add_many_test_users_with_groups: List[User],
    # add_test_policies_for_resources: List[AccessPolicy],
):
    """Test delete another user fails"""

    # mocks the access token:
    app_override_get_azure_payload_dependency
    existing_user = add_many_test_users_with_groups[2]
    # await add_test_policies_for_resources(
    #     resources=[existing_user],
    #     actions=["own"],
    #     publics=[True],
    # )
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["azure_user_id"] == existing_user.azure_user_id
    assert existing_db_user["id"] is not None
    assert existing_db_user["is_active"] is True

    # Make a DELETE request to update the user
    response = await async_client.delete(
        f"/api/v1/user/{str(existing_user.id)}",
    )
    assert response.status_code == 404
    assert response.text == '{"detail":"User not deleted."}'

    # check if user is still there:
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.id)
    existing_db_user = existing_db_user.model_dump()
    assert existing_db_user["azure_user_id"] == existing_user.azure_user_id
    assert existing_db_user["id"] is not None
    assert existing_db_user["is_active"] is True


# endregion: ## DELETE tests

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
