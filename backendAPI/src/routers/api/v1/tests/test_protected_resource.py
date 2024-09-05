from datetime import datetime, timedelta
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action, CurrentUserData, ResourceType
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD, ResourceHierarchyCRUD
from crud.protected_resource import (
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
    ProtectedResourceCRUD,
)
from models.access import ResourceHierarchyRead
from models.protected_resource import (
    ProtectedChild,
    ProtectedChildRead,
    ProtectedGrandChild,
    ProtectedGrandChildRead,
    ProtectedResource,
    ProtectedResourceRead,
)
from tests.utils import (
    current_user_data_admin,
    current_user_data_user2,
    many_test_protected_child_resources,
    many_test_protected_grandchild_resources,
    many_test_protected_resources,
    token_admin_read_write,
    token_user1_read_write,
)

# # temporarily only for debugging:
# from sqlmodel import select, or_
# from models.access import AccessPolicy

# region: ## endpoints tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_protected_resource_with_logs_and_policies(
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
async def test_get_all_protected_resources(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_protected_resources,
    mocked_get_azure_token_payload,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )

    # Make a GET request to get all protected resources
    time_before = datetime.now()
    response = await async_client.get(
        "/api/v1/protected/resource/",
    )
    time_after = datetime.now()
    assert response.status_code == 200
    read_protected_resources = response.json()
    assert len(read_protected_resources) == len(many_test_protected_resources)
    for read_resource, mocked_resource in zip(
        read_protected_resources, mocked_protected_resources
    ):
        modelled_protected_resource = ProtectedResourceRead(**read_resource)
        assert modelled_protected_resource.id == mocked_resource.id
        assert modelled_protected_resource.name == mocked_resource.name
        assert modelled_protected_resource.description == mocked_resource.description

    all_last_accessed_at = []
    async with AccessLoggingCRUD() as crud:
        for resource in mocked_protected_resources:
            last_accessed_at = await crud.read_resource_last_accessed_at(
                CurrentUserData(**current_user_data_admin),
                resource_id=resource.id,
            )
            all_last_accessed_at.append(last_accessed_at)

    current_test_user = current_test_user

    for last_accessed_at, mocked_resource in zip(
        all_last_accessed_at, mocked_protected_resources
    ):
        assert last_accessed_at.resource_id == mocked_resource.id
        assert last_accessed_at.identity_id == current_test_user.user_id
        assert last_accessed_at.action == Action.read
        assert last_accessed_at.time > time_before - timedelta(seconds=1)
        assert last_accessed_at.time < time_after + timedelta(seconds=1)
        assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_resource_by_id(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_protected_resources,
    mocked_get_azure_token_payload,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )

    # Make a GET request to get one protected resource by id
    time_before = datetime.now()
    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[3].id)}",
    )
    time_after = datetime.now()
    assert response.status_code == 200
    read_protected_resources = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resources)
    assert modelled_protected_resource.id == mocked_protected_resources[3].id
    assert modelled_protected_resource.name == mocked_protected_resources[3].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[3].description
    )

    async with AccessLoggingCRUD() as crud:
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=mocked_protected_resources[3].id,
        )

    current_test_user = current_test_user

    assert last_accessed_at.resource_id == mocked_protected_resources[3].id
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.read
    assert last_accessed_at.time > time_before - timedelta(seconds=1)
    assert last_accessed_at.time < time_after + timedelta(seconds=1)
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_put_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_protected_resources,
    mocked_get_azure_token_payload,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )

    new_data = {
        "description": "The updated description of the other resource.",
    }

    # Make a PUT request to update one protected resource
    time_before = datetime.now()
    response = await async_client.put(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[2].id)}",
        json=new_data,
    )
    time_after = datetime.now()

    assert response.status_code == 200
    read_protected_resources = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resources)
    assert modelled_protected_resource.id == mocked_protected_resources[2].id
    assert modelled_protected_resource.name == mocked_protected_resources[2].name
    assert modelled_protected_resource.description == new_data["description"]

    async with AccessLoggingCRUD() as crud:
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=mocked_protected_resources[2].id,
        )

    current_test_user = current_test_user

    assert last_accessed_at.resource_id == mocked_protected_resources[2].id
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.write
    assert last_accessed_at.time > time_before - timedelta(seconds=1)
    assert last_accessed_at.time < time_after + timedelta(seconds=1)
    assert last_accessed_at.status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_delete_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_many_test_protected_resources,
    mocked_get_azure_token_payload,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )

    # Make a DELETE request to delete one protected resource
    time_before = datetime.now()
    response = await async_client.delete(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[1].id)}",
    )
    time_after = datetime.now()

    assert response.status_code == 200

    async with AccessLoggingCRUD() as crud:
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=mocked_protected_resources[1].id,
        )

    current_test_user = current_test_user

    assert last_accessed_at.resource_id == mocked_protected_resources[1].id
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.own
    assert last_accessed_at.time > time_before - timedelta(seconds=1)
    assert last_accessed_at.time < time_after + timedelta(seconds=1)
    assert last_accessed_at.status_code == 200

    # Make a GET request to get deleted protected resource by id fails
    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[1].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "ProtectedResource not found."}

    try:
        async with AccessPolicyCRUD() as crud:
            await crud.read(
                current_test_user,
                resource_id=mocked_protected_resources[1].id,
            )
    except Exception as err:
        assert err.status_code == 404
        assert err.detail == "Access policy not found."
    else:
        pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_all_protected_child_endpoints(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_protected_children,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected child
    response = await async_client.post(
        "/api/v1/protected/child/",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )

    # add some more protected children:
    # note: the first one is going to be double with different id's
    mocked_protected_children = await add_many_test_protected_children(
        mocked_get_azure_token_payload
    )
    created_protected_child.id = UUID(created_protected_child.id)
    expected_protected_children = [created_protected_child] + mocked_protected_children
    expected_protected_children = sorted(
        expected_protected_children, key=lambda x: x.id
    )

    # Make a GET request to get all protected children
    response = await async_client.get(
        "/api/v1/protected/child/",
    )
    assert response.status_code == 200
    read_protected_children = response.json()
    assert len(read_protected_children) == len(expected_protected_children)
    for read_child, expected_child in zip(
        read_protected_children, expected_protected_children
    ):
        modelled_protected_child = ProtectedChildRead(**read_child)
        assert modelled_protected_child.id == expected_child.id
        assert modelled_protected_child.title == expected_child.title

    # Make a GET request to get one protected child by id
    response = await async_client.get(
        f"/api/v1/protected/child/{str(mocked_protected_children[2].id)}",
    )
    assert response.status_code == 200
    read_protected_child = response.json()
    modelled_protected_child = ProtectedChildRead(**read_protected_child)
    assert modelled_protected_child.id == mocked_protected_children[2].id
    assert modelled_protected_child.title == mocked_protected_children[2].title

    # Make a PUT request to update one protected child
    new_data = {"title": "The updated title of a child."}

    response = await async_client.put(
        f"/api/v1/protected/child/{str(mocked_protected_children[4].id)}",
        json=new_data,
    )
    assert response.status_code == 200
    read_protected_child = response.json()
    modelled_protected_child = ProtectedChildRead(**read_protected_child)
    assert modelled_protected_child.id == mocked_protected_children[4].id
    assert modelled_protected_child.title == new_data["title"]

    # Make a DELETE request to delete one protected child
    response = await async_client.delete(
        f"/api/v1/protected/child/{str(mocked_protected_children[3].id)}",
    )
    assert response.status_code == 200

    # Make a GET request to get deleted protected child by id fails
    response = await async_client.get(
        f"/api/v1/protected/child/{str(mocked_protected_children[3].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "ProtectedChild not found."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_all_protected_grandchild_endpoints(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_protected_grandchildren,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected child
    response = await async_client.post(
        "/api/v1/protected/grandchild/",
        json=many_test_protected_grandchild_resources[0],
    )

    assert response.status_code == 201
    created_protected_grandchild = ProtectedGrandChild(**response.json())
    assert (
        created_protected_grandchild.text
        == many_test_protected_grandchild_resources[0]["text"]
    )

    # add some more protected children:
    # note: the first one is going to be double with different id's
    mocked_protected_grandchildren = await add_many_test_protected_grandchildren(
        mocked_get_azure_token_payload
    )
    created_protected_grandchild.id = UUID(created_protected_grandchild.id)
    expected_protected_grandchildren = [
        created_protected_grandchild
    ] + mocked_protected_grandchildren
    expected_protected_grandchildren = sorted(
        expected_protected_grandchildren, key=lambda x: x.id
    )

    # Make a GET request to get all protected children
    response = await async_client.get(
        "/api/v1/protected/grandchild/",
    )
    assert response.status_code == 200
    read_protected_grandchildren = response.json()
    assert len(read_protected_grandchildren) == len(expected_protected_grandchildren)
    for read_grandchild, expected_grandchild in zip(
        read_protected_grandchildren, expected_protected_grandchildren
    ):
        modelled_protected_grandchild = ProtectedGrandChildRead(**read_grandchild)
        assert modelled_protected_grandchild.id == expected_grandchild.id
        assert modelled_protected_grandchild.text == expected_grandchild.text

    # Make a GET request to get one protected child by id
    response = await async_client.get(
        f"/api/v1/protected/grandchild/{str(mocked_protected_grandchildren[2].id)}",
    )
    assert response.status_code == 200
    read_protected_grandchild = response.json()
    modelled_protected_grandchild = ProtectedGrandChildRead(**read_protected_grandchild)
    assert modelled_protected_grandchild.id == mocked_protected_grandchildren[2].id
    assert modelled_protected_grandchild.text == mocked_protected_grandchildren[2].text

    # Make a PUT request to update one protected child
    new_data = {"text": "The updated text string for a grandchild."}

    response = await async_client.put(
        f"/api/v1/protected/grandchild/{str(mocked_protected_grandchildren[4].id)}",
        json=new_data,
    )
    assert response.status_code == 200
    read_protected_grandchild = response.json()
    modelled_protected_grandchild = ProtectedGrandChildRead(**read_protected_grandchild)
    assert modelled_protected_grandchild.id == mocked_protected_grandchildren[4].id
    assert modelled_protected_grandchild.text == new_data["text"]

    # Make a DELETE request to delete one protected child
    response = await async_client.delete(
        f"/api/v1/protected/grandchild/{str(mocked_protected_grandchildren[3].id)}",
    )
    assert response.status_code == 200

    # Make a GET request to get deleted protected child by id fails
    response = await async_client.get(
        f"/api/v1/protected/grandchild/{str(mocked_protected_grandchildren[3].id)}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "ProtectedGrandChild not found."}


# endregion ## endpoints tests

# region ## resource hierarchy tests:


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
    test_parent = [
        protected_resources
        for protected_resources in protected_resources
        if protected_resources.name == "First Protected Resource"
    ][0]

    # Make a POST request to create the protected child as a child of a protected resource
    before_time = datetime.now()
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={test_parent.id}",
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
            filters=[ProtectedResource.id == str(test_parent.id)],
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
            parent_id=test_parent.id,
            child_id=db_protected_child[0].id,
        )
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == test_parent.id
    assert hierarchy_entry[0].child_id == db_protected_child[0].id
    assert hierarchy_entry[0].inherit is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_adds_child_to_parent(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_protected_resources,
    add_many_test_protected_children,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children(
        mocked_get_azure_token_payload
    )

    response = await async_client.post(
        f"/api/v1/protected/child/{str(mocked_protected_children[0].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 201
    created_hierarchy = ResourceHierarchyRead(**response.json())
    assert created_hierarchy.parent_id == mocked_protected_resources[0].id
    assert created_hierarchy.child_id == mocked_protected_children[0].id
    assert created_hierarchy.inherit is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_adds_child_to_parent_without_access(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    # mocked_get_azure_token_payload,
    add_many_test_protected_resources,
    add_many_test_protected_children,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources()
    mocked_protected_children = await add_many_test_protected_children()

    response = await async_client.post(
        f"/api/v1/protected/child/{str(mocked_protected_children[0].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_adds_child_to_parent_without_access_to_parent(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_protected_resources,
    add_many_test_protected_children,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources()
    mocked_protected_children = await add_many_test_protected_children(
        mocked_get_azure_token_payload
    )

    response = await async_client.post(
        f"/api/v1/protected/child/{str(mocked_protected_children[0].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_adds_child_to_parent_without_access_to_child(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    add_many_test_protected_resources,
    add_many_test_protected_children,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    response = await async_client.post(
        f"/api/v1/protected/child/{str(mocked_protected_children[0].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_child_resource_from_a_parent_through_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests resource inheritance."""
    app_override_get_azure_payload_dependency

    current_user = current_test_user
    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )
    assert created_protected_child.id is not None

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_user,
            parent_id=created_protected_resource.id,
            child_id=created_protected_child.id,
        )
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == UUID(created_protected_resource.id)
    assert hierarchy_entry[0].child_id == UUID(created_protected_child.id)
    assert hierarchy_entry[0].inherit is True

    current_user2 = await register_current_user(current_user_data_user2)

    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    # Check for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            CurrentUserData(**current_user_data_admin),
            identity_id=current_user_data_user2["user_id"],
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == UUID(created_protected_resource.id)
    assert policies[0].identity_id == UUID(current_user_data_user2["user_id"])
    assert policies[0].action == Action.read

    # User2 should be able to read the child resource:
    async with ProtectedChildCRUD() as crud:
        db_protected_child = await crud.read_by_id(
            created_protected_child.id,
            current_user2,
        )

    assert db_protected_child.title == many_test_protected_child_resources[0]["title"]
    assert db_protected_child.id == UUID(created_protected_child.id)
    # Check if parent is returned with child:
    assert (
        db_protected_child.protected_resources[0].name
        == created_protected_resource.name
    )
    assert (
        db_protected_child.protected_resources[0].description
        == created_protected_resource.description
    )
    assert db_protected_child.protected_resources[0].id == UUID(
        created_protected_resource.id
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_child_resource_from_a_parent_through_inheritance_missing_parent_permission(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    current_user = current_test_user
    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )
    assert created_protected_child.id is not None

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_user,
            parent_id=created_protected_resource.id,
            child_id=created_protected_child.id,
        )
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == UUID(created_protected_resource.id)
    assert hierarchy_entry[0].child_id == UUID(created_protected_child.id)
    assert hierarchy_entry[0].inherit is True

    current_user2 = await register_current_user(current_user_data_user2)

    async with ProtectedChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_child_resource_from_a_parent_missing_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests if missing inheritance for child resource is handled correctly."""
    app_override_get_azure_payload_dependency

    current_user = current_test_user
    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=False",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )
    assert created_protected_child.id is not None

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_user,
            parent_id=created_protected_resource.id,
            child_id=created_protected_child.id,
        )
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == UUID(created_protected_resource.id)
    assert hierarchy_entry[0].child_id == UUID(created_protected_child.id)
    assert hierarchy_entry[0].inherit is False

    current_user2 = await register_current_user(current_user_data_user2)

    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    # Check for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            CurrentUserData(**current_user_data_admin),
            identity_id=current_user_data_user2["user_id"],
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == UUID(created_protected_resource.id)
    assert policies[0].identity_id == UUID(current_user_data_user2["user_id"])
    assert policies[0].action == Action.read

    async with ProtectedChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=True",
        json=many_test_protected_grandchild_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)

    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    async with ProtectedGrandChildCRUD() as crud:
        db_protected_grand_child = await crud.read_by_id(
            created_protected_grand_child.id,
            current_user2,
        )

    assert (
        db_protected_grand_child.text
        == many_test_protected_grandchild_resources[0]["text"]
    )
    assert db_protected_grand_child.id == UUID(created_protected_grand_child.id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent_missing_permission(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=True",
        json=many_test_protected_grandchild_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)

    async with ProtectedGrandChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_grand_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedGrandChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent_missing_child_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=False",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=True",
        json=many_test_protected_grandchild_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)
    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    async with ProtectedGrandChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_grand_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedGrandChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent_missing_grand_child_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=False",
        json=many_test_protected_grandchild_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)
    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    async with ProtectedGrandChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_grand_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedGrandChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write],
    indirect=True,
)
async def test_admin_adds_and_gets_protected_children_as_relationship_from_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    # mocked_get_azure_token_payload,
    add_many_test_protected_resources,
    add_many_test_protected_children,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources()
    mocked_protected_children = await add_many_test_protected_children()

    add_first_child = await async_client.post(
        f"/api/v1/protected/child/{str(mocked_protected_children[0].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert add_first_child.status_code == 201
    created_first_hierarchy = ResourceHierarchyRead(**add_first_child.json())
    assert created_first_hierarchy.parent_id == mocked_protected_resources[0].id
    assert created_first_hierarchy.child_id == mocked_protected_children[0].id
    assert created_first_hierarchy.inherit is False

    add_second_child = await async_client.post(
        f"/api/v1/protected/child/{str(mocked_protected_children[1].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert add_second_child.status_code == 201
    created_second_hierarchy = ResourceHierarchyRead(**add_second_child.json())
    assert created_second_hierarchy.parent_id == mocked_protected_resources[0].id
    assert created_second_hierarchy.child_id == mocked_protected_children[1].id
    assert created_second_hierarchy.inherit is False

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)
    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 2
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )
    assert (
        modelled_protected_resource.protected_children[1].id
        == mocked_protected_children[1].id
    )
    assert (
        modelled_protected_resource.protected_children[1].title
        == mocked_protected_children[1].title
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_gets_protected_children_with_access_to_all_as_relationship_from_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    current_test_user,
    add_many_test_protected_resources,
    add_many_test_protected_children,
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    current_test_user = current_test_user

    first_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[0].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert first_child.parent_id == mocked_protected_resources[0].id
    assert first_child.child_id == mocked_protected_children[0].id
    assert first_child.inherit is False

    policy_first_child = {
        "resource_id": str(first_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_first_child)

    second_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[1].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert second_child.parent_id == mocked_protected_resources[0].id
    assert second_child.child_id == mocked_protected_children[1].id
    assert second_child.inherit is False

    policy_second_child = {
        "resource_id": str(second_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_second_child)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)

    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 2
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )
    assert (
        modelled_protected_resource.protected_children[1].id
        == mocked_protected_children[1].id
    )
    assert (
        modelled_protected_resource.protected_children[1].title
        == mocked_protected_children[1].title
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_gets_only_protected_children_with_access_as_relationship_from_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    current_test_user,
    add_many_test_protected_resources,
    add_many_test_protected_children,
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    current_test_user = current_test_user

    first_child = await add_one_parent_child_resource_relationship(
        parent_id=mocked_protected_resources[0].id,
        child_id=mocked_protected_children[0].id,
        type=ResourceType.protected_child,
    )
    assert first_child.parent_id == mocked_protected_resources[0].id
    assert first_child.child_id == mocked_protected_children[0].id
    assert first_child.inherit is False

    policy_first_child = {
        "resource_id": str(first_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_first_child)

    second_child = await add_one_parent_child_resource_relationship(
        parent_id=mocked_protected_resources[0].id,
        child_id=mocked_protected_children[1].id,
        type=ResourceType.protected_child,
    )

    assert second_child.parent_id == mocked_protected_resources[0].id
    assert second_child.child_id == mocked_protected_children[1].id
    assert second_child.inherit is False

    # policy_second_child = {
    #     "resource_id": str(second_child.child_id),
    #     "identity_id": current_test_user.user_id,
    #     "action": "own",
    # }
    # await add_one_test_access_policy(policy_second_child)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)
    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 1

    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )
    modelled_protected_children_ids = [
        child.id for child in modelled_protected_resource.protected_children
    ]
    modelled_protected_children_titles = [
        child.title for child in modelled_protected_resource.protected_children
    ]
    assert mocked_protected_children[1].id not in modelled_protected_children_ids
    assert mocked_protected_children[1].title not in modelled_protected_children_titles


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_gets_only_protected_resource_and_none_of_the_existing_children_due_to_missing_of_access(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    current_test_user,
    add_many_test_protected_resources,
    add_many_test_protected_children,
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    current_test_user = current_test_user

    first_child = await add_one_parent_child_resource_relationship(
        parent_id=mocked_protected_resources[0].id,
        child_id=mocked_protected_children[0].id,
        type=ResourceType.protected_child,
    )
    assert first_child.parent_id == mocked_protected_resources[0].id
    assert first_child.child_id == mocked_protected_children[0].id
    assert first_child.inherit is False

    # policy_first_child = {
    #     "resource_id": str(first_child.child_id),
    #     "identity_id": current_test_user.user_id,
    #     "action": "own",
    # }
    # await add_one_test_access_policy(policy_first_child)

    second_child = await add_one_parent_child_resource_relationship(
        parent_id=mocked_protected_resources[0].id,
        child_id=mocked_protected_children[1].id,
        type=ResourceType.protected_child,
    )

    assert second_child.parent_id == mocked_protected_resources[0].id
    assert second_child.child_id == mocked_protected_children[1].id
    assert second_child.inherit is False

    # policy_second_child = {
    #     "resource_id": str(second_child.child_id),
    #     "identity_id": current_test_user.user_id,
    #     "action": "own",
    # }
    # await add_one_test_access_policy(policy_second_child)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)
    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_admin_removes_a_child_resource_from_a_parent_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    current_test_user,
    add_many_test_protected_resources,
    add_many_test_protected_children,
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    current_test_user = current_test_user

    first_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[0].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert first_child.parent_id == mocked_protected_resources[0].id
    assert first_child.child_id == mocked_protected_children[0].id
    assert first_child.inherit is False

    policy_first_child = {
        "resource_id": str(first_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_first_child)

    second_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[1].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert second_child.parent_id == mocked_protected_resources[0].id
    assert second_child.child_id == mocked_protected_children[1].id
    assert second_child.inherit is False

    policy_second_child = {
        "resource_id": str(second_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_second_child)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)

    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 2
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )
    assert (
        modelled_protected_resource.protected_children[1].id
        == mocked_protected_children[1].id
    )
    assert (
        modelled_protected_resource.protected_children[1].title
        == mocked_protected_children[1].title
    )

    # deleting second child:
    await async_client.delete(
        f"/api/v1/protected/child/{str(mocked_protected_children[1].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )

    # first child remains:
    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)

    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 1
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_removes_a_child_resource_from_a_parent_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    current_test_user,
    add_many_test_protected_resources,
    add_many_test_protected_children,
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    current_test_user = current_test_user

    first_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[0].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert first_child.parent_id == mocked_protected_resources[0].id
    assert first_child.child_id == mocked_protected_children[0].id
    assert first_child.inherit is False

    policy_first_child = {
        "resource_id": str(first_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_first_child)

    second_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[1].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert second_child.parent_id == mocked_protected_resources[0].id
    assert second_child.child_id == mocked_protected_children[1].id
    assert second_child.inherit is False

    policy_second_child = {
        "resource_id": str(second_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_second_child)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)

    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 2
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )
    assert (
        modelled_protected_resource.protected_children[1].id
        == mocked_protected_children[1].id
    )
    assert (
        modelled_protected_resource.protected_children[1].title
        == mocked_protected_children[1].title
    )

    # deleting second child:
    await async_client.delete(
        f"/api/v1/protected/child/{str(mocked_protected_children[1].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )

    # first child remains:
    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)

    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 1
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write],
    indirect=True,
)
async def test_user_removes_a_child_resource_from_a_parent_protected_resource_missing_access_to_child(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
    current_test_user,
    add_many_test_protected_resources,
    add_many_test_protected_children,
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    mocked_protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )
    mocked_protected_children = await add_many_test_protected_children()

    current_test_user = current_test_user

    first_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[0].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert first_child.parent_id == mocked_protected_resources[0].id
    assert first_child.child_id == mocked_protected_children[0].id
    assert first_child.inherit is False

    policy_first_child = {
        "resource_id": str(first_child.child_id),
        "identity_id": current_test_user.user_id,
        "action": "own",
    }
    await add_one_test_access_policy(policy_first_child)

    second_child = await add_one_parent_child_resource_relationship(
        child_id=mocked_protected_children[1].id,
        parent_id=mocked_protected_resources[0].id,
        type=ResourceType.protected_child,
    )
    assert second_child.parent_id == mocked_protected_resources[0].id
    assert second_child.child_id == mocked_protected_children[1].id
    assert second_child.inherit is False

    # policy_second_child = {
    #     "resource_id": str(second_child.child_id),
    #     "identity_id": current_test_user.user_id,
    #     "action": "own",
    # }
    # await add_one_test_access_policy(policy_second_child)

    response = await async_client.get(
        f"/api/v1/protected/resource/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 200
    read_protected_resource = response.json()
    modelled_protected_resource = ProtectedResourceRead(**read_protected_resource)

    assert modelled_protected_resource.id == mocked_protected_resources[0].id
    assert modelled_protected_resource.name == mocked_protected_resources[0].name
    assert (
        modelled_protected_resource.description
        == mocked_protected_resources[0].description
    )
    assert len(modelled_protected_resource.protected_children) == 1
    assert (
        modelled_protected_resource.protected_children[0].id
        == mocked_protected_children[0].id
    )
    assert (
        modelled_protected_resource.protected_children[0].title
        == mocked_protected_children[0].title
    )

    # deleting second child fails:
    response = await async_client.delete(
        f"/api/v1/protected/child/{str(mocked_protected_children[1].id)}/parent/{str(mocked_protected_resources[0].id)}",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Hierarchy not found."


# endregion ## resource hierarchy tests


# region ## identity inheritance tests:


# endregion ## identity inheritance tests


# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Tests for the protected resource family API:
# ✔︎ User and Admin creates a protected resource: gets logged and access policy created
# ✔︎ User and Admin reads all protected resources: gets logged
# ✔︎ User and Admin reads a protected resource by id: gets logged
# ✔︎ User and Admin updates a protected resource: gets logged
# ✔︎ User and Admin deletes a protected resource: gets logged and access policy deleted
# ✔︎ User and Admin access all endpoints for child resource
# ✔︎ User and Admin access all endpoints for grand child resource

# Tests for resource hierarchy used by protected resource family API:
# ✔︎ User creates a child resource for a protected resource: hierarchy entry gets created
# ✔︎ User adds a child to parent resource
# ✔︎ User adds a child to parent resource without access to parent and child
# ✔︎ User adds a child to parent resource without access to parent
# ✔︎ User adds a child to parent resource without access to child
# ✔︎ User and Admin reads a child protected resource, where resource inherits access from parent
# ✔︎ User and Admin reads a child protected resource, where resource inherits access from parent but user has no access to parent
# ✔︎ User and Admin reads a child protected resource, where resource does not inherit access from parent but user has access to parent
# ✔︎ User reads a grand child protected resource, where user inherits access from grand parent (which is a protected resource)
# ✔︎ User reads a grand child protected resource, where user inherits access from grand parent (which is a protected resource) missing permission
# ✔︎ User reads a grand child protected resource, where user inherits access from grand parent (which is a protected resource) missing child inheritance
# ✔︎ User reads a grand child protected resource, where user inherits access from grand parent (which is a protected resource) missing grand child inheritance
# ✔︎ Admin reads  protected resource and gets all children through relationship
# ✔︎ User reads a protected resource and gets all children through relationship with access to all children
# ✔︎ User reads a protected resource and gets only children with access through relationship
# ✔︎ User reads all protected resource: only the protected resources and child resources, that the user has access to are returned
# ✔︎ User reads protected resource and gets only parent but none of the existing children due to missing access policies
# ✔︎ Admin removes a child from parent resource
# ✔︎ User removes a child from parent resource
# ✔︎ User removes a child from parent resource fails due to missing access to child

# - User reads a protected resource: children and grand children get returned as well - but only the ones the user has access to
# ? more grand child tests?

# Tests for identity hierarchy:
# X User2 reads child and grand child where access to the parent resource through is inherited through subsubgroup / subgroup / group to parent resource
# - User reads a protected resource, where user inherits access from a group
# - User reads a protected resource, where user is in a sub_sub_group and inherits access from membership in a group
# - User reads a protected resource fails, where inheritance is set to false (resource inheritance)
# - User reads a protected resource fails, where inheritance is set to false (group inheritance)
# - User updates a protected resource: with inherited write access from parent / grand parent (resource inheritance)
# - User updates a protected resource: with inherited write access from group, where user is in group / sub-group / sub-sub-group (group inheritance)
# - User deletes a protected resource: with inherited owner access from parent / grand parent (resource inheritance)
# - User deletes a protected resource: with inherited owner access from group, where user is in group / sub-group / sub-sub-group (group inheritance)
