import pytest
from httpx import AsyncClient
from models.demo_resource import DemoResource
from utils import demo_resource_test_input


@pytest.mark.anyio
async def test_post_demo_resource(async_client: AsyncClient):
    """Tests POST of a demo_resource."""
    resource = demo_resource_test_input
    # get_async_test_session
    response = await async_client.post("/api/v1/demo_resource/", json=resource)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == demo_resource_test_input["name"]
    assert content["description"] == demo_resource_test_input["description"]
    assert "id" in content


@pytest.mark.anyio
async def test_get_demo_resource(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests GET all demo resources."""
    resources = add_test_demo_resources
    print("=== demo resources ===")
    print(resources)
    response = await async_client.get("/api/v1/demo_resource/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    for response_item in response.json():
        assert response_item["name"] in [
            resources[0].name,
            resources[1].name,
        ]
        assert response_item["description"] in [
            resources[0].description,
            resources[1].description,
        ]
        assert response_item["language"] in [
            resources[0].language,
            resources[1].language,
        ]
        assert response_item["timezone"] in [
            resources[0].timezone,
            resources[1].timezone,
        ]
        assert "id" in response_item


@pytest.mark.anyio
async def test_get_demo_resource_by_id(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests GET of a demo resources."""
    resources = add_test_demo_resources

    response = await async_client.get("/api/v1/demo_resource/1")
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert "id" in content


@pytest.mark.anyio
async def test_get_demo_resource_by_invalid_id(async_client: AsyncClient):
    """Tests GET of a demo resources."""

    response = await async_client.get("/api/v1/demo_resource/invalid_id")
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid resource id"


@pytest.mark.anyio
async def test_put_demo_resource(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests PUT of a demo resource."""
    resources = add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "language": "es-ES",
        "timezone": "UTC+9",
    }
    response = await async_client.put("/api/v1/demo_resource/1", json=updated_resource)

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    assert content["language"] == updated_resource["language"]
    assert content["timezone"] == updated_resource["timezone"]


@pytest.mark.anyio
async def test_put_demo_resource_not_all_updated(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests PUT of a demo resource."""
    resources = add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "timezone": "UTC+10",
    }
    response = await async_client.put("/api/v1/demo_resource/1", json=updated_resource)

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    print("=== resources[0].language ===")
    print(resources[0].language)
    print("=== content['language'] ===")
    print(content["language"])
    assert content["language"] == resources[0].language  # this one is not updatged!
    assert content["timezone"] == updated_resource["timezone"]


@pytest.mark.anyio
async def test_put_demo_resource_by_invalid_id(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests GET of a demo resources."""
    add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "timezone": "UTC+10",
    }
    response = await async_client.put(
        "/api/v1/demo_resource/not_an_integer", json=updated_resource
    )

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid resource id"


@pytest.mark.anyio
async def test_put_demo_resource_by_resource_does_not_exist(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests GET of a demo resources."""
    add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "timezone": "UTC+10",
    }
    response = await async_client.put(
        "/api/v1/demo_resource/100", json=updated_resource
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Resource not found"


# TBD: This is not checked - up to the user for now, to get the input correct. Wrong input does not change anything.
# @pytest.mark.anyio
# async def test_put_demo_resource_wrong_input(
#     async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
# ):
#     """Tests PUT of a demo resource."""
#     add_test_demo_resources
#     updated_resource = {
#         "title": "Some title",
#         "category": 42,
#     }
#     response = await async_client.put("/api/v1/demo_resource/1", json=updated_resource)

#     assert response.status_code == 400


@pytest.mark.anyio
async def test_delete_demo_resource(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests DELETE of a demo resource."""
    resources = add_test_demo_resources
    id = 1
    response = await async_client.get(f"/api/v1/demo_resource/{id}")

    # Check if resource exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == id
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language
    assert content["timezone"] == resources[0].timezone

    # Delete resource:
    response = await async_client.delete(f"/api/v1/demo_resource/{id}")
    assert response.status_code == 200
    content = response.json()
    print("=== content ===")
    print(content)
    # assert "Deleted resource ${id}." in content["detail"]
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language
    assert content["timezone"] == resources[0].timezone

    # Check if resource exists after deleting:
    response = await async_client.get(f"/api/v1/demo_resource/{id}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Resource not found"


#     assert response.status_code == 200
#     assert {"status": "ok"} == response.json()
