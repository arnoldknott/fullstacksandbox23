from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from models.demo_resource import DemoResource
from models.tag import Tag
from tests.utils import one_test_demo_resource


@pytest.mark.anyio
async def test_post_demo_resource(async_client: AsyncClient):
    """Tests POST of a demo_resource."""
    resource = one_test_demo_resource
    # get_async_test_session
    time_before_crud = datetime.now()
    response = await async_client.post("/api/v1/demo_resource/", json=resource)
    time_after_crud = datetime.now()

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == one_test_demo_resource["name"]
    assert content["description"] == one_test_demo_resource["description"]
    assert (
        time_before_crud - timedelta(seconds=18)
        < datetime.fromisoformat(content["created_at"])
        < time_after_crud + timedelta(seconds=18)
    )
    assert "demo_resource_id" in content


@pytest.mark.anyio
async def test_post_demo_resource_with_nonexisting_category(async_client: AsyncClient):
    """Tests POST of a demo_resource."""
    resource = one_test_demo_resource
    resource["category_id"] = 100
    print("=== resource ===")
    print(resource)
    # get_async_test_session
    response = await async_client.post("/api/v1/demo_resource/", json=resource)
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


# TBD: add a test, that checks if the category_is is existing in the database!


@pytest.mark.anyio
async def test_get_demo_resource(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests GET all demo resources."""
    resources = add_test_demo_resources
    # print("=== demo resources ===")
    # print(resources)
    response = await async_client.get("/api/v1/demo_resource/")

    assert response.status_code == 200
    assert len(response.json()) == 4
    for response_item in response.json():
        assert response_item["name"] in [
            resources[0].name,
            resources[1].name,
            resources[2].name,
            resources[3].name,
        ]
        assert response_item["description"] in [
            resources[0].description,
            resources[1].description,
            resources[2].description,
            resources[3].description,
        ]
        assert response_item["language"] in [
            resources[0].language,
            resources[1].language,
            resources[2].language,
            resources[3].language,
        ]
        # assert response_item["timezone"] in [
        #     resources[0].timezone,
        #     resources[1].timezone,
        # ]
        assert "demo_resource_id" in response_item


@pytest.mark.anyio
async def test_get_demo_resource_by_id(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests GET of a demo resources."""
    resources = add_test_demo_resources

    time_before_get_call = datetime.now()
    response = await async_client.get("/api/v1/demo_resource/1")
    time_after_get_call = datetime.now()
    print("== test_get_demo_resource_by_id - get call time ===")
    print((time_after_get_call - time_before_get_call).total_seconds())
    # solution with SQLModel back_population of tables: about 0.07 - 0.14 seconds
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert "demo_resource_id" in content
    assert "tags" in content
    assert "category" in content

    # assert 1 == 2


@pytest.mark.anyio
async def test_get_demo_resource_by_invalid_id(async_client: AsyncClient):
    """Tests GET of a demo resources with invalid id."""

    response = await async_client.get("/api/v1/demo_resource/invalid_id")
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid resource id"


@pytest.mark.anyio
async def test_put_demo_resource(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests PUT of a demo resource."""
    add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "language": "es-ES",
        # "timezone": "UTC+9",
    }
    time_before_crud = datetime.now()
    response = await async_client.put("/api/v1/demo_resource/1", json=updated_resource)
    time_after_crud = datetime.now()

    assert response.status_code == 200
    content = response.json()
    # print("=== last_updated_at ===")
    # print(datetime.fromisoformat(content["last_updated_at"]))
    # print(type(datetime.fromisoformat(content["last_updated_at"])))
    # print("=== time_before_crud ===")
    # print(time_before_crud)
    # print(type(time_before_crud))
    assert (
        time_before_crud - timedelta(seconds=8)
        < datetime.fromisoformat(content["last_updated_at"])
        < time_after_crud + timedelta(seconds=8)
    )
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    assert content["language"] == updated_resource["language"]
    # assert content["timezone"] == updated_resource["timezone"]


@pytest.mark.anyio
async def test_put_demo_resource_partial_update(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests PUT of a demo resource, where not all fields are updated."""
    resources = add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        # "timezone": "UTC+10",
    }
    response = await async_client.put("/api/v1/demo_resource/1", json=updated_resource)

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    # print("=== resources[0].language ===")
    # print(resources[0].language)
    # print("=== content['language'] ===")
    # print(content["language"])
    assert content["language"] == resources[0].language  # this one is not updatged!
    # assert content["timezone"] == updated_resource["timezone"]


@pytest.mark.anyio
async def test_put_demo_resource_by_invalid_id(
    async_client: AsyncClient, add_test_demo_resources: list[DemoResource]
):
    """Tests PUT of a demo resources with invalid id."""
    add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        # "timezone": "UTC+10",
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
    """Tests PUT of nonexisting demo resources."""
    add_test_demo_resources
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        # "timezone": "UTC+10",
    }
    response = await async_client.put(
        "/api/v1/demo_resource/100", json=updated_resource
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


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
    assert content["demo_resource_id"] == id
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language
    # assert content["timezone"] == resources[0].timezone

    # Delete resource:
    response = await async_client.delete(f"/api/v1/demo_resource/{id}")
    assert response.status_code == 200
    content = response.json()
    # print("=== content ===")
    # print(content)
    # assert "Deleted resource ${id}." in content["detail"]
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language
    # assert content["timezone"] == resources[0].timezone

    # Check if resource exists after deleting:
    response = await async_client.get(f"/api/v1/demo_resource/{id}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Demo resource not found"


@pytest.mark.anyio
async def test_delete_demo_resource_by_invalid_id(async_client: AsyncClient):
    """Tests DELETE of a demo resources with invalid id."""
    response = await async_client.delete("/api/v1/demo_resource/invalid_id")

    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Invalid resource id"


@pytest.mark.anyio
async def test_delete_demo_resource_by_resource_does_not_exist(
    async_client: AsyncClient,
):
    """Tests GET of a demo resources."""
    response = await async_client.delete("/api/v1/demo_resource/100")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_attach_tag_to_demo_resource(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    add_test_tags: list[Tag],
):
    """Tests POST of a tag to a demo resource."""
    add_test_demo_resources
    tags = add_test_tags
    resource_id = 2
    tag_ids = [1, 3]
    response = await async_client.post(
        f"/api/v1/demo_resource/{resource_id}/tag/?tag_ids={tag_ids[0]}&tag_ids={tag_ids[1]}"
    )
    # for tag_id in tag_ids:
    #     response = await async_client.post(
    #         f"/api/v1/demo_resource/{resource_id}/tag/{tag_id}"
    #     )

    assert response.status_code == 200
    content = response.json()
    print("=== content ===")
    print(content)
    assert len(content["tags"]) == 2
    assert content["tags"][0]["name"] in [
        tags[0].name,
        tags[2].name,
    ]
    assert content["tags"][1]["name"] in [
        tags[0].name,
        tags[2].name,
    ]
