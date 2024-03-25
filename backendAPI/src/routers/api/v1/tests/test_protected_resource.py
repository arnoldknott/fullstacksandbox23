import pytest
from datetime import datetime, timedelta

from httpx import AsyncClient
from crud.protected_resource import ProtectedResourceCRUD
from crud.access import AccessPolicyCRUD, AccessLoggingCRUD
from models.protected_resource import ProtectedResource
from fastapi import FastAPI
from tests.utils import (
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_roles_admin,
    token_payload_roles_user,
    token_payload_scope_api_read_write,
    many_test_protected_resources,
)

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
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read_write,
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_post_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the user
    time_before_post = datetime.now()
    # time_before_post = time.time()
    response = await async_client.post(
        "/api/v1/protectedresource/",
        json=many_test_protected_resources[0],
    )
    time_after_post = datetime.now()
    # time_after_post = time.time()

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )
    async with ProtectedResourceCRUD() as crud:
        db_protected_resource = await crud.read_by_id(
            created_protected_resource.id,
            # current_test_user# Pass user information like this
        )
    assert db_protected_resource is not None
    assert db_protected_resource.last_accessed_at is not None
    # assert (
    #     db_protected_resource.last_accessed_at == created_protected_resource.created_at
    # )
    # assert (
    #     time_before_post - timedelta(seconds=25)
    #     < db_protected_resource.created_at  # datetime.fromisoformat(db_protected_resource.created_at)
    #     < time_after_post + timedelta(seconds=25)
    # )
    assert db_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        db_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # TBD: add tests for created access policy here!
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            resource_id=db_protected_resource.id,
            resource_type="ProtectedResource",
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == db_protected_resource.id
    assert policies[0].resource_type == "ProtectedResource"
    assert policies[0].identity_id == current_test_user.user_id
    assert policies[0].identity_type == "User"
    assert policies[0].action == "own"

    # Test for created logs:
    async with AccessLoggingCRUD() as crud:
        resource_log = await crud.read_log_by_resource(
            db_protected_resource.id,
            "ProtectedResource",
        )

    assert resource_log[0].resource_id == db_protected_resource.id
    assert resource_log[0].resource_type == "ProtectedResource"
    assert resource_log[0].identity_id == current_test_user.user_id
    assert resource_log[0].identity_type == "User"
    assert resource_log[0].action == "own"
    assert resource_log[0].status_code == 201
    assert resource_log[0].time >= time_before_post - timedelta(seconds=4)
    assert resource_log[0].time <= time_after_post + timedelta(seconds=4)


# TBD: add tests for get, get_by_id, put, delete endpoints of the protected resource API!

# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_get_azure_token_payload",
#     [
#         {
#             **token_payload_user_id,
#             **token_payload_tenant_id,
#             **token_payload_scope_api_read_write,
#             **token_payload_roles_admin,
#             **token_payload_one_group,
#         }
#     ],
#     indirect=True,
# )
# async def test_post_user_with_integer_user_id(
#     async_client: AsyncClient,
#     app_override_get_azure_payload_dependency: FastAPI,
# ):
#     """Tests posting a integer user_id to user_post endpoint fails"""
#     app_override_get_azure_payload_dependency

#     # Make a POST request to create the user
#     response = await async_client.post(
#         "/api/v1/user/",
#         json={**one_test_user, "user_id": 1},
#     )

#     assert response.status_code == 201
#     created_user = User(**response.json())
#     assert created_user.azure_user_id == one_test_user["azure_user_id"]
#     assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]

#     # Verify that the user was created in the database
#     async with UserCRUD() as crud:
#         db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
#     assert db_user is not None
#     db_user_json = jsonable_encoder(db_user)
#     assert db_user_json["id"] != 1


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_get_azure_token_payload",
#     [
#         {
#             **token_payload_user_id,
#             **token_payload_tenant_id,
#             **token_payload_scope_api_read_write,
#             **token_payload_roles_admin,
#             **token_payload_one_group,
#         }
#     ],
#     indirect=True,
# )
# async def test_post_user_with_uuid_user_id(
#     async_client: AsyncClient,
#     app_override_get_azure_payload_dependency: FastAPI,
# ):
#     """Tests the post_user endpoint of the API."""
#     app_override_get_azure_payload_dependency
#     test_uuid = str(uuid.uuid4())

#     # Make a POST request to create the user
#     response = await async_client.post(
#         "/api/v1/user/",
#         json={**one_test_user, "user_id": test_uuid},
#     )

#     assert response.status_code == 201
#     created_user = User(**response.json())
#     assert created_user.azure_user_id == one_test_user["azure_user_id"]
#     assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]

#     # Verify that the user was created in the database
#     async with UserCRUD() as crud:
#         db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
#     assert db_user is not None
#     # db_user_json = jsonable_encoder(db_user)
#     db_user = db_user.model_dump()
#     assert "last_accessed_at" in db_user
#     assert "last_accessed_at" != None
#     assert db_user["azure_user_id"] == uuid.UUID(one_test_user["azure_user_id"])
#     assert db_user["azure_tenant_id"] == uuid.UUID(one_test_user["azure_tenant_id"])
#     assert db_user["user_id"] != uuid.UUID(test_uuid)


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_get_azure_token_payload",
#     [
#         {
#             **token_payload_user_id,
#             **token_payload_tenant_id,
#             **token_payload_scope_api_read_write,
#             **token_payload_roles_user,
#             **token_payload_one_group,
#         }
#     ],
#     indirect=True,
# )
# async def test_user_posts_user(
#     async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
# ):
#     """Tests the post_user endpoint of the API."""
#     app_override_get_azure_payload_dependency

#     # Make a POST request to create the user
#     response = await async_client.post(
#         "/api/v1/user/",
#         json=one_test_user,
#     )

#     assert response.status_code == 403
#     assert response.text == '{"detail":"Access denied"}'

#     # this would allow other users to create users, which is not allowed - only self-sign-up!:
#     # assert response.status_code == 201
#     # created_user = User(**response.json())
#     # assert created_user.azure_user_id == one_test_user["azure_user_id"]
#     # assert created_user.azure_tenant_id == one_test_user["azure_tenant_id"]

#     # # Verify that the user was created in the database
#     # async with UserCRUD() as crud:
#     #     db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
#     # assert db_user is not None
#     # db_user_json = jsonable_encoder(db_user)
#     # assert "last_accessed_at" in db_user_json
#     # assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
#     # assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_get_azure_token_payload",
#     [
#         {
#             # **token_payload_scope_api_read_write,
#             **token_payload_scope_api_read,
#             **token_payload_roles_admin,
#         },
#         {
#             # **token_payload_scope_api_read_write,
#             **token_payload_scope_api_write,
#             **token_payload_roles_admin,
#         },
#         {
#             **token_payload_scope_api_read_write,
#             # **token_payload_roles_admin,
#         },
#         {},
#     ],
#     indirect=True,
# )
# async def test_post_user_invalid_token(
#     async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
# ):
#     """Tests the post_user endpoint of the API."""
#     app_override_get_azure_payload_dependency

#     # Make a POST request to create the user
#     response = await async_client.post(
#         "/api/v1/user/",
#         json=one_test_user,
#     )

#     assert response.status_code == 403
#     assert response.text == '{"detail":"Access denied"}'
