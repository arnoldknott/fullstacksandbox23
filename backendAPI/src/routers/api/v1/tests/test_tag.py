import pytest
from httpx import AsyncClient
from models.tag import Tag


@pytest.mark.anyio
async def test_post_tag(async_client: AsyncClient):
    """Tests POST of a tag."""
    tag = {
        "name": "TestTag",
    }
    response = await async_client.post("/api/v1/tag/", json=tag)

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == tag["name"]
    assert "id" in content


@pytest.mark.anyio
async def test_post_tag_name_too_long(async_client: AsyncClient):
    """Tests POST of too long tag."""
    tag = {
        "name": "TestTag  with more than 10 characters",
    }
    response = await async_client.post("/api/v1/tag/", json=tag)

    content = response.json()

    assert response.status_code == 422
    assert content["detail"][0]["type"] == "string_too_long"


@pytest.mark.anyio
async def test_get_all_tags(async_client: AsyncClient, add_test_tags: list[Tag]):
    """Tests GET all tags."""
    tags = add_test_tags
    response = await async_client.get("/api/v1/tag/")

    assert response.status_code == 200
    assert len(response.json()) == 4
    content = response.json()[3]
    assert content["name"] == tags[3].name
    assert "id" in content


@pytest.mark.anyio
async def test_get_tag_by_id(async_client: AsyncClient, add_test_tags: list[Tag]):
    """Tests GET all tags."""
    tags = add_test_tags
    response = await async_client.get("/api/v1/tag/2")

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == tags[1].name
    assert "id" in content


@pytest.mark.anyio
async def test_get_tag_by_invalid_id(async_client: AsyncClient):
    """Tests GET of a tag with invalid id."""

    response = await async_client.get("/api/v1/tag/invalid_id")
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid tag id"


@pytest.mark.anyio
async def test_put_tag(async_client: AsyncClient, add_test_tags: list[Tag]):
    """Tests PUT of a ta."""
    add_test_tags
    updated_tag = {
        "name": "NewTag",
    }
    response = await async_client.put("/api/v1/tag/2", json=updated_tag)

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_tag["name"]


@pytest.mark.anyio
async def test_put_tag_does_not_exist(
    async_client: AsyncClient, add_test_tags: list[Tag]
):
    """Tests PUT of a tag."""
    add_test_tags
    updated_tag = {
        "name": "Uptag",
    }
    response = await async_client.put("/api/v1/tag/324", json=updated_tag)

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_delete_tag(async_client: AsyncClient, add_test_tags: list[Tag]):
    """Tests DELETE of a tag."""
    tags = add_test_tags
    id = 2
    response = await async_client.get(f"/api/v1/tag/{id}")

    # Check if tag exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == id
    assert content["name"] == tags[1].name

    # Delete tag:
    response = await async_client.delete(f"/api/v1/tag/{id}")
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == tags[1].name

    # Check if tag exists after deleting:
    response = await async_client.get(f"/api/v1/tag/{id}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_delete_tag_by_invalid_id(async_client: AsyncClient):
    """Tests DELETE of a tag with invalid id."""
    response = await async_client.delete("/api/v1/tag/invalid_id")

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid tag id"


@pytest.mark.anyio
async def test_delete_tag_does_not_exist(
    async_client: AsyncClient, add_test_tags: list[Tag]
):
    """Tests DELETE of a tag."""
    add_test_tags
    id = 5327
    response = await async_client.delete(f"/api/v1/tag/{id}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


# @pytest.mark.anyio
# async def test_get_all_demo_resources_by_category_id(
#     async_client: AsyncClient,
#     add_test_demo_resources_with_category: list[DemoResource],
# ):
#     """Tests GET all demo resources by category id."""
#     resources = add_test_demo_resources_with_category
#     response = await async_client.get("/api/v1/category/2/demo_resources")

#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     first_content = response.json()[0]
#     assert first_content["name"] == resources[0].name
#     assert first_content["description"] == resources[0].description
#     assert first_content["language"] == resources[0].language
#     assert "id" in first_content

#     second_content = response.json()[1]
#     assert second_content["name"] == resources[2].name
#     assert second_content["description"] == resources[2].description
#     assert second_content["language"] == resources[2].language
#     assert "id" in second_content


# @pytest.mark.anyio
# async def test_get_demo_resources_for_lonely_category(
#     async_client: AsyncClient,
#     add_test_demo_resources_with_category: list[DemoResource],
# ):
#     """Tests GET error for category, that has no demo resources attached."""
#     print("=== test_get_no_demo_resources_for_unlinked_category ===")
#     add_test_demo_resources_with_category
#     response = await async_client.get("/api/v1/category/3/demo_resources")

#     print(response.json())
#     assert response.status_code == 404
#     content = response.json()
#     assert content["detail"] == "No demo resources found"
