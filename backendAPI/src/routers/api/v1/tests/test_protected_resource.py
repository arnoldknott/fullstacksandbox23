from datetime import datetime, timedelta
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action, CurrentUserData
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD, ResourceHierarchyCRUD
from crud.protected_resource import ProtectedChildCRUD, ProtectedResourceCRUD
from models.protected_resource import ProtectedChild, ProtectedResource
from tests.utils import (
    current_user_data_admin,
    many_test_protected_child_resources,
    many_test_protected_resources,
    token_admin_read_write,
    token_user1_read_write,
)

# region: ## POST tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    before_time = datetime.now()
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Test for created logs:
    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_resource.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_resource.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.resource_id == UUID(created_protected_resource.id)
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.own
    assert last_accessed_at.time == created_at
    assert last_accessed_at.status_code == 201

    async with ProtectedResourceCRUD() as crud:
        db_protected_resource = await crud.read(
            current_test_user,
            filters=[ProtectedResource.id == created_protected_resource.id],
        )
    assert len(db_protected_resource) == 1
    assert db_protected_resource[0].name == many_test_protected_resources[0]["name"]
    assert (
        db_protected_resource[0].description
        == many_test_protected_resources[0]["description"]
    )

    # Test for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            current_test_user,
            resource_id=db_protected_resource[0].id,
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == db_protected_resource[0].id
    assert policies[0].identity_id == current_test_user.user_id
    assert policies[0].action == Action.own


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_protected_child_resource_and_add_to_parent(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    add_many_test_protected_resources,
    mocked_get_azure_token_payload,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )

    # Make a POST request to create the protected child as a child of a protected resource
    before_time = datetime.now()
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={protected_resources[0].id}",
        json=many_test_protected_child_resources[0],
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )

    # Check for created logs:
    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_child.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_child.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.resource_id == UUID(created_protected_child.id)
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.own
    assert last_accessed_at.time == created_at
    assert last_accessed_at.status_code == 201

    # Check if the parent was updated in database and contains the protected child:
    async with ProtectedResourceCRUD() as crud:
        db_protected_resource = await crud.read(
            current_test_user,
            filters=[ProtectedResource.id == protected_resources[0].id],
        )
    assert len(db_protected_resource) == 1
    assert db_protected_resource[0].name == many_test_protected_resources[0]["name"]
    assert (
        db_protected_resource[0].description
        == many_test_protected_resources[0]["description"]
    )
    assert len(db_protected_resource[0].protected_children) == 1
    assert db_protected_resource[0].protected_children[0].id == UUID(
        created_protected_child.id
    )
    assert (
        db_protected_resource[0].protected_children[0].title
        == many_test_protected_child_resources[0]["title"]
    )

    # Check if the child was created in database:
    async with ProtectedChildCRUD() as crud:
        db_protected_child = await crud.read(
            current_test_user,
            filters=[ProtectedChild.id == created_protected_child.id],
        )
    assert len(db_protected_child) == 1
    assert (
        db_protected_child[0].title == many_test_protected_child_resources[0]["title"]
    )

    # Check for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            current_test_user,
            resource_id=db_protected_child[0].id,
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == db_protected_child[0].id
    assert policies[0].identity_id == current_test_user.user_id
    assert policies[0].action == Action.own

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_test_user,
            parent_id=protected_resources[0].id,
            child_id=db_protected_child[0].id,
        )
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == protected_resources[0].id
    assert hierarchy_entry[0].child_id == db_protected_child[0].id
    assert hierarchy_entry[0].inherit is False


# endregion ## POST tests

# AccessPolicy and AccessLog tests not necessary in all tests! Just in one post, one read, one update and one delete test!


# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Tests to implement for the protected resource family API:
# ✔︎ User and Admin creates a protected resource: gets logged and access policy created
# ✔︎ User creates a child resource for a protected resource: hierarchy entry gets created
# X User reads all protected resource: only the protected resources and child resources, that the user has access to are returned
# X User reads a protected resource by id: gets logged
# - User reads a protected resource: children and grand children get returned as well - but only the ones the user has access to
# - User reads a child protected resource, where user inherits access from parent
# - User reads a grand child protected resource, where user inherits access from grand parent (which is a protected resource)
# - User reads a protected resource, where user inherits access from a group
# - User reads a protected resource, where user is in a sub_sub_group and inherits access from membership in a group
# - User reads a protected resource fails, where inheritance is set to false (resource inheritance)
# - User reads a protected resource fails, where inheritance is set to false (group inheritance)
# X User updates a protected resource: gets logged
# - User updates a protected resource: with inherited write access from parent / grand parent (resource inheritance)
# - User updates a protected resource: with inherited write access from group, where user is in group / sub-group / sub-sub-group (group inheritance)
# X User deletes a protected resource: gets logged
# - User deletes a protected resource: with inherited owner access from parent / grand parent (resource inheritance)
# - User deletes a protected resource: with inherited owner access from group, where user is in group / sub-group / sub-sub-group (group inheritance)
