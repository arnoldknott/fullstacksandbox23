# from unittest.mock import AsyncMock, patch

import pytest
from crud.user import UserCRUD
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from main import app
from core.security import get_azure_token_payload
from models.user import User
from tests.utils import (
    token_payload_roles_admin,
    token_payload_scope_api_write,
    token_payload_group,
    # token_payload_roles_user,
    one_test_user,
)

# TBD: move to conftest:
def mocked_get_azure_token_payload():
    """ Returns a mocked token payload. """
    return {
        # TBD: configure the token in conftest and use different mocking functions.
        'oid': one_test_user["azure_user_id"],
        'tid': one_test_user["azure_tenant_id"],
        **token_payload_scope_api_write,
        **token_payload_roles_admin,
        **token_payload_group
        }

app.dependency_overrides[get_azure_token_payload] = mocked_get_azure_token_payload

@pytest.mark.anyio
async def test_post_user(async_client: AsyncClient):
    """Tests the post_user endpoint of the API."""
    # with patch(
    #     "core.security.get_azure_token_payload", new_callable=AsyncMock
    # ) as mock_get_azure_token_payload:
    #     # , patch(
    #     #     "core.security.guards.current_token_has_scope_api_write", new_callable=AsyncMock
    #     # ) as mock_api_write:
    #     mock_get_azure_token_payload.return_value = {
    #         'oid': one_test_user["azure_user_id"],
    #         'tid': one_test_user["azure_tenant_id"],
    #         **token_payload_scope_api_write,
    #         **token_payload_roles_admin,
    #         **token_payload_group
    #         # **token_payload_scope_api_write,
    #         # **token_payload_roles_admin,
    #     }
        # mock_api_write.return_value = True
        # apparently another instance of Guard is getting called than the patched one.

    # Make a POST request to create the user
    response = await async_client.post(
        "/api/v1/user/",
        # headers={"Authorization": "Bearer myaccesstoken"},
        # json={key: str(value) for key, value in one_test_user.items()},
        json=one_test_user,
    )

    # print(mock_get_azure_token_payload.call_count)
    # mock_get_azure_token_payload.assert_called_once()
    # mock_api_write.assert_called_once()

    assert response.status_code == 201
    created_user = User(**response.json())
    assert created_user.azure_user_id == one_test_user["azure_user_id"]
    assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]

    # Verify that the user was created in the database
    async with UserCRUD() as crud:
        db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
    assert db_user is not None
    # print("=== db_user ===")
    # print(db_user)
    db_user_json = jsonable_encoder(db_user)
    # print("=== db_user ===")
    # print(db_user)
    assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
    assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]


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
