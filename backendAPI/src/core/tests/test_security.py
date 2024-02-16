# from unittest.mock import AsyncMock, patch

# import pytest
# from crud.user import UserCRUD
# from fastapi.encoders import jsonable_encoder
# from core.security import guards, get_azure_token_payload
# from main import app
# from tests.utils import (
#     token_payload_roles_user,
#     token_payload_scope_api_write,
#     one_test_user,
# )

# # TBD: move to conftest:
# def mocked_get_azure_token_payload():
#     """ Returns a mocked token payload. """
#     return {
#         'groups': 'mocked_groups',
#         # TBD: configure the token in conftest and use different mocking functions.
#         **token_payload_scope_api_write,
#         **token_payload_roles_user
#         }

# @pytest.mark.anyio
# async def test_azure_user_self_signup():
#     """ Tests if a new user can sign up by themselves. """
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

#     app.dependency_overrides[get_azure_token_payload] = mocked_get_azure_token_payload()

#     # call the guard function, which executes self-signup for the user:
#     # guards = Guards()
#     current_user = await guards.current_azure_user_in_database()

#     # mock_get_azure_token_payload.assert_called_once()

#     assert current_user.azure_user_id == one_test_user["azure_user_id"]
#     assert current_user.azure_tenant_id == one_test_user["azure_tenant_id"]

#     # Verify that the user was created in the database
#     async with UserCRUD() as crud:
#         db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
#     assert db_user is not None
#     db_user_json = jsonable_encoder(db_user)
#     assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
#     assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]
