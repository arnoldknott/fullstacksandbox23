# from unittest.mock import AsyncMock, patch

import pytest
from typing import Annotated
from fastapi import Depends, FastAPI
from crud.user import UserCRUD
from fastapi.encoders import jsonable_encoder
from core.security import guards
from httpx import AsyncClient

from tests.utils import (
    # token_payload_roles_user,
    # token_payload_scope_api_write,
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_one_group,
    token_payload_roles_user_admin,
    token_payload_roles_admin_user,
    token_payload_roles_admin,
    token_payload_roles_user,
    one_test_user,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_write,
            # **token_payload_roles_user,
            **token_payload_one_group,
        }
    ],
    indirect=True,
)
async def test_azure_user_self_signup(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests if a new user can sign up by themselves."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_azure_user_self_signup")
    def temp_endpoint(
        current_user: Annotated[str, Depends(guards.current_azure_user_in_database)]
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_azure_user_self_signup",
    )

    assert response.status_code == 200
    current_user = response.json()

    assert current_user["azure_user_id"] == one_test_user["azure_user_id"]
    assert current_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]

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
            **token_payload_roles_admin,
        },
        {
            **token_payload_roles_user_admin,
        },
        {
            **token_payload_roles_admin_user,
        },
    ],
    indirect=True,
)
async def test_admin_guard_with_admin_role_in_azure_mocked_token_payload(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_admin_guard_with_admin_role_in_azure_mocked_token_payload")
    def temp_endpoint(current_user: bool = Depends(guards.current_azure_user_is_admin)):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_admin_guard_with_admin_role_in_azure_mocked_token_payload",
    )

    assert response.status_code == 200
    token_contains_role_admin = response.json()
    assert token_contains_role_admin is True


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_admin_guard_without_admin_role_in_azure_mocked_token_payload(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_admin_guard_without_admin_role_in_azure_mocked_token_payload")
    def temp_endpoint(current_user: bool = Depends(guards.current_azure_user_is_admin)):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_admin_guard_without_admin_role_in_azure_mocked_token_payload",
    )

    assert response.status_code == 200
    token_contains_role_admin = response.json()
    assert token_contains_role_admin is False


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_get_azure_token_payload",[{}],
#     indirect=True,
# )
# async def test_azure_user_self_signup_missing_token(
#     async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
# ):
#     """Tests that a new user cannot sign itself up without access token."""

#     app = app_override_get_azure_payload_dependency

#     # create a temporary route that uses the guard:
#     @app.get("/temp_endpoint")
#     def temp_endpoint(
#         current_user: Annotated[str, Depends(guards.current_azure_user_in_database)]
#     ):
#         """Returns the result of the guard."""
#         return current_user

#     # call that temporary route:
#     response = await async_client.get(
#         "/temp_endpoint",
#     )

#     assert response.status_code == 200


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_get_azure_token_payload",
#     [
#         {
#             **token_payload_user_id,
#             **token_payload_tenant_id,
#             # **token_payload_scope_api_write,
#             # **token_payload_roles_user,
#             "groups": token_payload_many_groups["groups"]
#             + token_payload_one_group["groups"],
#         }
#     ],
#     indirect=True,
# )
# async def test_existing_azure_user_has_new_group_in_token(
#     async_client: AsyncClient,
#     app_override_get_azure_payload_dependency: FastAPI,
#     add_one_test_user_with_groups: User,
# ):
#     """Tests if a new user can sign up by themselves."""
#     # preparing the test: adds a user to the database and ensure that this user is member of 3 groups:
#     existing_user = add_one_test_user_with_groups
#     async with UserCRUD() as crud:
#         existing_db_user = await crud.read_by_id_with_childs(existing_user.user_id)

#     existing_db_user_read = UserRead(**jsonable_encoder(existing_db_user))
#     print("=== existing_db_user_read ===")
#     print(existing_db_user_read)

#     # existing_db_user_json = jsonable_encoder(existing_db_user)
#     # print("=== existing_db_user_json ===")
#     # print(existing_db_user_json)

#     # existing_db_user_read = UserRead(**existing_db_user_json)

#     assert len(existing_db_user_read.azure_groups) == 3

#     app = app_override_get_azure_payload_dependency

#     # create a temporary route that uses the guard adn call it:
#     @app.get("/temp_endpoint")
#     def temp_endpoint(
#         current_user: Annotated[str, Depends(guards.current_azure_user_in_database)]
#     ):
#         """Returns the result of the guard."""
#         return current_user

#     response = await async_client.get(
#         "/temp_endpoint",
#     )

#     updated_user = response.json()

#     assert updated_user["azure_user_id"] == one_test_user["azure_user_id"]
#     assert updated_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]

#     # Verify that the user now has the new group in the database
#     async with UserCRUD() as crud:
#         db_user = await crud.read_by_id_with_childs(existing_user.user_id)
#     assert db_user is not None
#     db_user_json = jsonable_encoder(db_user)
#     print("=== db_user_json ===")
#     print(db_user_json)
#     assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
#     assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]

#     assert 1 == 2
