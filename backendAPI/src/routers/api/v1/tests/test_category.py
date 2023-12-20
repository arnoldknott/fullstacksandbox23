import pytest
from httpx import AsyncClient
from models.category import Category


@pytest.mark.anyio
async def test_post_category(async_client: AsyncClient):
    """Tests POST of a category."""
    resource = {
        "name": "Test Cat",
        "description": "Some description for this category",
    }
    response = await async_client.post("/api/v1/category/", json=resource)

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == resource["name"]
    assert content["description"] == resource["description"]
    assert "id" in content


@pytest.mark.anyio
async def test_post_category_name_too_long(async_client: AsyncClient):
    """Tests POST of a category."""
    resource = {
        "name": "Test Category Name That Is Too Long",
        "description": "Some description for this category",
    }
    response = await async_client.post("/api/v1/category/", json=resource)

    content = response.json()

    assert response.status_code == 422
    assert content["detail"][0]["type"] == "string_too_long"


@pytest.mark.anyio
async def test_get_all_categories(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests GET all categories."""
    categories = add_test_categories
    response = await async_client.get("/api/v1/category/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    content = response.json()[0]
    assert content["name"] == categories[0].name
    assert content["description"] == categories[0].description
    assert "id" in content


@pytest.mark.anyio
async def test_get_category_by_id(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests GET all categories."""
    categories = add_test_categories
    response = await async_client.get("/api/v1/category/2")

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description
    assert "id" in content


@pytest.mark.anyio
async def test_get_category_by_invalid_id(async_client: AsyncClient):
    """Tests GET of a category with invalid id."""

    response = await async_client.get("/api/v1/category/invalid_id")
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid category id"


@pytest.mark.anyio
async def test_put_category(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests PUT of a category."""
    add_test_categories
    updated_category = {
        "name": "Test Cat",
        "description": "A new description for this category",
    }
    response = await async_client.put("/api/v1/category/2", json=updated_category)

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
    response = await async_client.put("/api/v1/category/2", json=updated_category)

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
    response = await async_client.put("/api/v1/category/324", json=updated_category)

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_delete_category(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests DELETE of a category."""
    categories = add_test_categories
    id = 2
    response = await async_client.get(f"/api/v1/category/{id}")

    # Check if category exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == id
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description

    # Delete category:
    response = await async_client.delete(f"/api/v1/category/{id}")
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == categories[1].name
    assert content["description"] == categories[1].description

    # Check if category exists after deleting:
    response = await async_client.get(f"/api/v1/category/{id}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_delete_category_by_invalid_id(async_client: AsyncClient):
    """Tests DELETE of a category with invalid id."""
    response = await async_client.delete("/api/v1/category/invalid_id")

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid category id"


@pytest.mark.anyio
async def test_delete_category_does_not_exist(
    async_client: AsyncClient, add_test_categories: list[Category]
):
    """Tests DELETE of a category."""
    add_test_categories
    id = 5327
    response = await async_client.delete(f"/api/v1/category/{id}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"
