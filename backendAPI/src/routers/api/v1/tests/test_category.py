import pytest
from httpx import AsyncClient


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
