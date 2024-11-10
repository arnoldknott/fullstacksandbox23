import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models.category import Category
from tests.utils import (
    token_admin,
    token_admin_read_write,
    token_user1_read,
    token_user1_read_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_category(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests POST of a category."""

    app_override_provide_http_token_payload

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
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
@pytest.mark.anyio
async def test_post_category_name_too_long(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests POST of a category."""
    app_override_provide_http_token_payload

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
    "mocked_provide_http_token_payload",
    [
        token_admin,
        token_admin_read_write,
        token_user1_read,
        token_user1_read_write,
    ],
    indirect=True,
)
async def test_get_all_categories(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET all categories."""

    app_override_provide_http_token_payload
    categories = await add_test_categories(mocked_provide_http_token_payload)

    response = await async_client.get("/api/v1/category/")

    assert response.status_code == 200
    database_categories = response.json()
    assert len(database_categories) == 3

    for database_category, mocked_category in zip(database_categories, categories):
        assert database_category["name"] == mocked_category.name
        assert database_category["description"] == mocked_category.description
        assert database_category["id"] == str(mocked_category.id)
        # assert "id" in database_category
    # assert content["name"] == categories[0].name
    # assert content["description"] == categories[0].description
    # assert "id" in content
    # assert 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin, token_admin_read_write, token_user1_read, token_user1_read_write],
    indirect=True,
)
async def test_get_category_by_id(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET all categories."""

    app_override_provide_http_token_payload
    categories = await add_test_categories(mocked_provide_http_token_payload)
    response = await async_client.get(f"/api/v1/category/{str(categories[1].id)}")

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description
    assert "id" in content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin, token_admin_read_write, token_user1_read, token_user1_read_write],
    indirect=True,
)
async def test_get_category_by_invalid_id(
    async_client: AsyncClient, app_override_provide_http_token_payload: FastAPI
):
    """Tests GET of a category with invalid id."""

    app_override_provide_http_token_payload
    response = await async_client.get("/api/v1/category/invalid_id")
    assert response.status_code == 422
    # print("=== response.json() ===")
    # print(response.json())
    # content = response.json()
    # assert content["detail"] == "Invalid id."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_put_category(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of a category."""

    app_override_provide_http_token_payload
    categories = add_test_categories
    categories = await add_test_categories(mocked_provide_http_token_payload)
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
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_put_category_partial_update(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of a category."""

    app_override_provide_http_token_payload
    categories = await add_test_categories(mocked_provide_http_token_payload)
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
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_put_category_does_not_exist(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of a category."""

    app_override_provide_http_token_payload
    await add_test_categories(mocked_provide_http_token_payload)
    updated_category = {
        "name": "Test Cat",
        "description": "A new description for this category",
    }
    response = await async_client.put(
        f"/api/v1/category/{str(uuid.uuid4())}", json=updated_category
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Category not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_put_category_wrong_data(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of a category."""

    app_override_provide_http_token_payload
    categories = await add_test_categories(mocked_provide_http_token_payload)
    wrong_category_data = {
        "comments": "There is no field comments in category",
        "emoji": "❌",
        "fvoiaeofgjaf": "voainfvarfia",
        "number": 123,
    }
    response = await async_client.put(
        f"/api/v1/category/{str(categories[1].id)}", json=wrong_category_data
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description
    assert "id" in content
    for key in wrong_category_data:
        assert key not in content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_delete_category(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests DELETE of a category."""

    app_override_provide_http_token_payload
    categories = await add_test_categories(mocked_provide_http_token_payload)
    response = await async_client.get(f"/api/v1/category/{str(categories[1].id)}")

    # Check if category exists before deleting:
    # assert "This is failing, as 'own', does not include 'read' yet" == True
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(categories[1].id)
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description

    # Delete category:
    response = await async_client.delete(f"/api/v1/category/{str(categories[1].id)}")
    assert response.status_code == 200
    # content = response.json()
    # assert content["name"] == categories[1].name
    # assert content["description"] == categories[1].description

    # Check if category exists after deleting:
    response = await async_client.get(f"/api/v1/category/{str(categories[1].id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Category not found."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_delete_category_by_invalid_id(
    async_client: AsyncClient, app_override_provide_http_token_payload: FastAPI
):
    """Tests DELETE of a category with invalid id."""

    app_override_provide_http_token_payload
    response = await async_client.delete("/api/v1/category/invalid_id")

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_delete_category_does_not_exist(
    async_client: AsyncClient,
    add_test_categories: list[Category],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests DELETE of a category."""

    app_override_provide_http_token_payload
    await add_test_categories(mocked_provide_http_token_payload)
    response = await async_client.delete(f"/api/v1/category/{str(uuid.uuid4())}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Category not deleted."


# Moved to test_demo_resource.py
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin, token_admin_read_write, token_user1_read_write, token_user1_read],
#     indirect=True,
# )
# async def test_get_all_demo_resources_by_category_id(
#     async_client: AsyncClient,
#     add_test_demo_resources: list[DemoResource],
#     app_override_provide_http_token_payload: FastAPI,
#     mocked_provide_http_token_payload,
# ):
#     """Tests GET all demo resources by category id."""

#     app_override_provide_http_token_payload
#     resources = await add_test_demo_resources(mocked_provide_http_token_payload)

#     categories_response = await async_client.get("/api/v1/category/")
#     categories = categories_response.json()

#     response = await async_client.get(
#         f"/api/v1/category/{str(categories[1]['id'])}/demoresources"
#     )

#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     first_content = response.json()[0]
#     assert first_content["name"] == resources[0].name
#     assert first_content["description"] == resources[0].description
#     assert first_content["language"] == resources[0].language
#     assert "category_id" in first_content

#     second_content = response.json()[1]
#     assert second_content["name"] == resources[2].name
#     assert second_content["description"] == resources[2].description
#     assert second_content["language"] == resources[2].language
#     assert "category_id" in second_content


# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin, token_admin_read_write, token_user1_read_write, token_user1_read],
#     indirect=True,
# )
# async def test_get_demo_resources_for_lonely_category(
#     async_client: AsyncClient,
#     add_test_demo_resources: list[DemoResource],
#     app_override_provide_http_token_payload: FastAPI,
#     mocked_provide_http_token_payload,
# ):
#     """Tests GET error for category, that has no demo resources attached."""

#     app_override_provide_http_token_payload

#     await add_test_demo_resources(mocked_provide_http_token_payload)
#     # add_test_demo_resources
#     categories_response = await async_client.get("/api/v1/category/")
#     categories = categories_response.json()
#     response = await async_client.get(
#         f"/api/v1/category/{str(categories[2]['id'])}/demoresources"
#     )

#     assert response.status_code == 404
#     content = response.json()
#     assert content["detail"] == "No demo resources found"
