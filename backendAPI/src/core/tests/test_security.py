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
    token_payload_group,
    one_test_user,
)


# TBD: move to conftest:
# def mocked_get_azure_token_payload():
#     """Returns a mocked token payload."""
#     return {
#         # TBD: configure the token in conftest and use different mocking functions.
#         "oid": one_test_user["azure_user_id"],
#         "tid": one_test_user["azure_tenant_id"],
#         **token_payload_scope_api_write,
#         **token_payload_roles_user,
#         **token_payload_group,
#     }


# app.dependency_overrides[get_azure_token_payload] = mocked_get_azure_token_payload


# @pytest.mark.anyio
# async def test_azure_user_self_signup(async_client: AsyncClient):
#     """Tests if a new user can sign up by themselves."""
#     # with patch(
#     #     "core.security.get_azure_token_payload", new_callable=AsyncMock) as mock_get_azure_token_payload:
#     # # ):
#     # # as mock_get_azure_token_payload:
#     #     mock_get_azure_token_payload.return_value = {
#     #         'groups': 'some groups here',
#     #         **token_payload_scope_api_write,
#     #         **token_payload_roles_user,
#     #     }

#     #     # TBD: put inside patch: ??
#     #     #  return_value={
#     #     #     'groups': 'some groups here',
#     #     #     'oid': one_test_user["azure_user_id"],
#     #     #     **token_payload_scope_api_write,
#     #     #     **token_payload_roles_user,
#     #     # },

#     # with patch('core.security.get_azure_token_payload', return_value={'groups': 'mocked_groups'}):# as mock_get_azure_token_payload:

#     # call the guard function, which executes self-signup for the user:
#     # guards = Guards()
#     # current_user = await guards.current_azure_user_in_database()

#     # create a temporary route that uses the guard:
#     @app.get("/temp_endpoint")
#     def temp_endpoint(
#         current_user: Annotated[str, Depends(Guards.current_azure_user_in_database)]
#     ):
#         """Returns the result of the guard."""
#         # print("=== current_user ===")
#         # print(current_user)
#         return current_user

#     # app.add_api_route("/temp_endpoint", temp_endpoint)

#     # call that temporary route:
#     response = await async_client.get(
#         "/temp_endpoint",
#         # headers={"Authorization": "Bearer myaccesstoken"},
#         # json={key: str(value) for key, value in one_test_user.items()},
#         # json=one_test_user,
#     )
#     # print("=== response ===")
#     # print(response)
#     current_user = response.json()
#     print("=== current_user ===")
#     print(current_user)

#     # mock_get_azure_token_payload.assert_called_once()
#     # mocked_get_azure_token_payload.assert_called_once()

#     assert current_user["azure_user_id"] == one_test_user["azure_user_id"]
#     assert current_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]

#     # Verify that the user was created in the database
#     async with UserCRUD() as crud:
#         db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
#     assert db_user is not None
#     db_user_json = jsonable_encoder(db_user)
#     assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
#     assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]

#     # assert 1 == 2

#     # remove the temporary route:
#     # app.routes.remove("/temp_endpoint")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            "oid": one_test_user["azure_user_id"],
            "tid": one_test_user["azure_tenant_id"],
            # **token_payload_scope_api_write,
            # **token_payload_roles_user,
            **token_payload_group,
        }
    ],
    indirect=True,
)
async def test_azure_user_self_signup(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests if a new user can sign up by themselves."""

    # print("=== mocked_get_azure_token_payload ===")
    # print(app_override_get_azure_payload_dependency)

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/temp_endpoint")
    def temp_endpoint(
        current_user: Annotated[str, Depends(Guards.current_azure_user_in_database)]
    ):
        """Returns the result of the guard."""
        # print("=== current_user ===")
        # print(current_user)
        return current_user

        # call that temporary route:

    response = await async_client.get(
        "/temp_endpoint",
    )

    current_user = response.json()

    print("=== current_user ===")
    print(current_user)

    assert current_user["azure_user_id"] == one_test_user["azure_user_id"]
    assert current_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]

    # Verify that the user was created in the database
    async with UserCRUD() as crud:
        db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
    assert db_user is not None
    db_user_json = jsonable_encoder(db_user)
    assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
    assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]
