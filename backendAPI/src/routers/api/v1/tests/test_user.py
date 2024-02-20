# from unittest.mock import AsyncMock, patch

import pytest
from crud.user import UserCRUD
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from models.user import User, UserRead
from fastapi import FastAPI
from tests.utils import (
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_roles_admin,
    token_payload_scope_api_read,
    token_payload_scope_api_read_write,
    token_payload_one_group,
    # token_payload_roles_user,
    one_test_user,
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
async def test_post_user(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        json=one_test_user,
    )

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == one_test_user["azure_user_id"]
    assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]

    # Verify that the user was created in the database
    async with UserCRUD() as crud:
        db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
    assert db_user is not None
    db_user_json = jsonable_encoder(db_user)
    assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
    assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_scope_api_read,
            **token_payload_roles_admin,
        }
    ],
    indirect=True,
)
async def test_get_user(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_test_user: User,
):
    '''Test GET one user'''

    # mocks the access token:
    app_override_get_azure_payload_dependency

    # adds a user to the database, which is the one to GET:
    user = add_one_test_user

    response = await async_client.get(f"/api/v1/user/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert "user_id" in users[0]
    assert users[0]["azure_user_id"] == str(user.azure_user_id)
    assert users[0]["azure_tenant_id"] == str(user.azure_tenant_id)


@pytest.mark.anyio
async def test_get_user_without_token(
    async_client: AsyncClient,
    add_one_test_user: User,
):
    '''Test GET one user'''
    user = add_one_test_user

    response = await async_client.get(f"/api/v1/user/")
    assert response.status_code == 401

# @pytest.mark.anyio
# async def test_get_user_by_id(
#     async_client: AsyncClient,
#     add_one_test_user_with_groups: UserRead,
# ):
#     '''Test GET one user by id'''
#     user = add_one_test_user_with_groups

#     response = await async_client.get(f"/api/v1/user/{user.user_id}")
#     assert response.status_code == 200
#     user = response.json()
#     assert "user_id" in user
#     assert user["azure_user_id"] == str(user.azure_user_id)
#     assert user["azure_tenant_id"] == str(user.azure_tenant_id)
#     assert len(user["azure_groups"]) == 3

# TBD: consider writing tests for security instead and drop all endpoints for user and groups (for now)?
# Passing tests:
# - admin user creates a user
# - admin user reads all users
# - admin user reads a user by id
# - regular user reads itself by id
# - admin user updates a user
# - admin user deletes a user
# - regular user deletes itself
# for the following: groups are not part of the user endpoints - need their own endpoints, but security is taking care of the sign-up!
# - users connections to groups are created in the database
# - a user, that is already signed up was added in Azure to a new group: does the new connection show up in the database?

# Failing tests:
# TBD: implement test, where regular user (not admin):
# - wants to create another user
# - wants to read all user
# - wants to put a user
# - wants to read a different user by id
# - regular user wants to delete another user
