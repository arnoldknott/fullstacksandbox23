# from unittest.mock import AsyncMock, patch

import pytest
from typing import Annotated
from fastapi import Depends, FastAPI
from crud.user import UserCRUD
from fastapi.encoders import jsonable_encoder
from core.security import Guards
from httpx import AsyncClient
from tests.utils import (
    # token_payload_roles_user,
    # token_payload_scope_api_write,
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_one_group,
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
    @app.get("/temp_endpoint")
    def temp_endpoint(
        current_user: Annotated[str, Depends(Guards.current_azure_user_in_database)]
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/temp_endpoint",
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
#         current_user: Annotated[str, Depends(Guards.current_azure_user_in_database)]
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
#             "groups": token_payload_many_groups["groups"] + token_payload_one_group["groups"],
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

#     existing_db_user_json = jsonable_encoder(existing_db_user)
#     print("=== existing_db_user_json ===")
#     print(existing_db_user_json)

#     assert len(existing_db_user_json["azure_groups"]) == 3

#     app = app_override_get_azure_payload_dependency

#     # create a temporary route that uses the guard adn call it:
#     @app.get("/temp_endpoint")
#     def temp_endpoint(
#         current_user: Annotated[str, Depends(Guards.current_azure_user_in_database)]
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