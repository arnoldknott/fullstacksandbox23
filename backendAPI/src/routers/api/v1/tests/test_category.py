import pytest
import uuid
from httpx import AsyncClient
from fastapi import FastAPI
from models.access import AccessPolicy
from models.category import Category
from models.demo_resource import DemoResource
from tests.utils import (
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_roles_admin,
    token_payload_roles_user,
    token_payload_scope_api_read_write,
    token_payload_scope_api_read,
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
async def test_post_category(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests POST of a category."""

    app_override_get_azure_payload_dependency

    category = {
        "name": "Test Cat",
        "description": "Some description for this category",
    }
    response = await async_client.post("/api/v1/category/", json=category)

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == category["name"]
    assert content["description"] == category["description"]
    assert "id" in content


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
@pytest.mark.anyio
async def test_post_category_name_too_long(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests POST of a category."""
    app_override_get_azure_payload_dependency

    category = {
        "name": "Test Category Name That Is Too Long",
        "description": "Some description for this category",
    }
    response = await async_client.post("/api/v1/category/", json=category)

    content = response.json()

    assert response.status_code == 422
    assert content["detail"][0]["type"] == "string_too_long"


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
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_get_all_categories(
    async_client: AsyncClient,
    add_test_policies_for_resources: list[AccessPolicy],
    add_test_categories: list[Category],
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET all categories."""

    app_override_get_azure_payload_dependency
    categories = add_test_categories
    await add_test_policies_for_resources(
        resources=categories,
        actions=["read"] * len(categories),
        publics=[True] * len(categories),
    )
    # print(
    #     "=== test-category - test_get_all_categories - public_policies_for_test_categories ==="
    # )
    # print(public_policies_for_test_categories)

    # print(
    #     "=== test-category - test_get_all_categories - type(categories[0].model_dump()) ==="
    # )
    # print(type(categories[0].model_dump()))
    # print(
    #     "=== test-category - test_get_all_categories - categories[0].model_dump() ==="
    # )
    # print(categories[0].model_dump())

    # access_policies = [
    #     {
    #         # "identity_id": str(uuid.uuid4()),# needs to be from the user, that is mocked in the test - for successful tests
    #         # "identity_type": IdentityType.user,
    #         "resource_id": categories[0].id,
    #         "resource_type": ResourceType.category,
    #         "action": Action.read,
    #         "public": True,
    #     },
    #     {
    #         # "identity_id": str(uuid.uuid4()),# needs to be from the user, that is mocked in the test - for successful tests
    #         # "identity_type": IdentityType.user,
    #         "resource_id": categories[1].id,
    #         "resource_type": ResourceType.category,
    #         "action": Action.read,
    #         "public": True,
    #     },
    #     {
    #         # "identity_id": str(uuid.uuid4()),# needs to be from the user, that is mocked in the test - for successful tests
    #         # "identity_type": IdentityType.user,
    #         "resource_id": categories[2].id,
    #         "resource_type": ResourceType.category,
    #         "action": Action.read,
    #         "public": True,
    #     },
    # ]
    # print("=== test-category - test_get_all_categories - type(ResourceType) ===")
    # print(type(ResourceType))
    # print(
    #     "=== test-category - test_get_all_categories - type(ResourceType.category) ==="
    # )
    # print(type(ResourceType.category))
    # print(ResourceType.category)
    # print(ResourceType.category.name)
    # print(ResourceType.category.value)
    # print("=== test-category - test_get_all_categories - category[0] ===")
    # print(categories[0])
    # print(categories[0].__class__.__name__)
    # # This is brilliant! It works:
    # print(ResourceType(categories[0].__class__.__name__))

    # # Now ready to pass to the fixture:
    # actions = ["read"] * len(categories)
    # public = True * len(categories)

    # TBD: goal is to just call the fixture for creating the policies with
    # - a list of resources,
    # - a list of action and
    # - either list of identities or public override! - rethink that one!

    # policies = await add_test_policies_for_resources(access_policies)
    # print("=== test-category - test_get_all_categories - policies ===")
    # print(policies)

    response = await async_client.get("/api/v1/category/")

    assert response.status_code == 200
    assert len(response.json()) == 3
    content = response.json()[0]
    assert content["name"] == categories[0].name
    assert content["description"] == categories[0].description
    assert "id" in content
    # assert 1 == 2


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
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_get_category_by_id(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    add_test_policies_for_resources: list[AccessPolicy],
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET all categories."""

    app_override_get_azure_payload_dependency
    categories = add_test_categories
    # TBD: consider moving this into the add_test_categories fixture with action argument on it and default public or override with optional identity
    await add_test_policies_for_resources(
        resources=categories,
        actions=["read"] * len(categories),
        publics=[True] * len(categories),
    )
    print("=== categories[1].id ===")
    print(categories[1].id)
    response = await async_client.get(f"/api/v1/category/{str(categories[1].id)}")

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description
    assert "id" in content


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
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_get_category_by_invalid_id(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests GET of a category with invalid id."""

    app_override_get_azure_payload_dependency
    response = await async_client.get("/api/v1/category/invalid_id")
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid category id"


@pytest.mark.anyio
async def test_put_category(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests PUT of a category."""
    categories = add_test_categories
    updated_category = {
        "name": "Test Cat",
        "description": "A new description for this category",
    }
    response = await async_client.put(
        f"/api/v1/category/{str(categories[1].id)}", json=updated_category
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_category["name"]
    assert content["description"] == updated_category["description"]


@pytest.mark.anyio
async def test_put_category_partial_update(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests PUT of a category."""
    categories = add_test_categories
    updated_category = {
        "description": "An updated description for this category",
    }
    response = await async_client.put(
        f"/api/v1/category/{str(categories[1].id)}", json=updated_category
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == updated_category["description"]


@pytest.mark.anyio
async def test_put_category_does_not_exist(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests PUT of a category."""
    add_test_categories
    updated_category = {
        "name": "Test Cat",
        "description": "A new description for this category",
    }
    response = await async_client.put(
        f"/api/v1/category/{str(uuid.uuid4())}", json=updated_category
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


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
async def test_delete_category(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests DELETE of a category."""

    app_override_get_azure_payload_dependency
    categories = add_test_categories
    response = await async_client.get(f"/api/v1/category/{str(categories[1].id)}")

    # Check if category exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(categories[1].id)
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description

    # Delete category:
    response = await async_client.delete(f"/api/v1/category/{str(categories[1].id)}")
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description

    # Check if category exists after deleting:
    response = await async_client.get(f"/api/v1/category/{str(categories[1].id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


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
async def test_delete_category_by_invalid_id(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests DELETE of a category with invalid id."""

    app_override_get_azure_payload_dependency
    response = await async_client.delete("/api/v1/category/invalid_id")

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid category id"


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
async def test_delete_category_does_not_exist(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests DELETE of a category."""

    app_override_get_azure_payload_dependency
    add_test_categories
    response = await async_client.delete(f"/api/v1/category/{str(uuid.uuid4())}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


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
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_get_all_demo_resources_by_category_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET all demo resources by category id."""

    app_override_get_azure_payload_dependency
    resources = add_test_demo_resources
    categories_response = await async_client.get("/api/v1/category/")
    categories = categories_response.json()
    response = await async_client.get(
        f"/api/v1/category/{str(categories[1]['id'])}/demo_resources"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    first_content = response.json()[0]
    assert first_content["name"] == resources[0].name
    assert first_content["description"] == resources[0].description
    assert first_content["language"] == resources[0].language
    assert "category_id" in first_content

    second_content = response.json()[1]
    assert second_content["name"] == resources[2].name
    assert second_content["description"] == resources[2].description
    assert second_content["language"] == resources[2].language
    assert "category_id" in second_content


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
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_read,
            **token_payload_roles_admin,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
        },
    ],
    indirect=True,
)
async def test_get_demo_resources_for_lonely_category(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET error for category, that has no demo resources attached."""

    app_override_get_azure_payload_dependency

    add_test_demo_resources
    categories_response = await async_client.get("/api/v1/category/")
    categories = categories_response.json()
    response = await async_client.get(
        f"/api/v1/category/{str(categories[2]['id'])}/demo_resources"
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "No demo resources found"
