from datetime import datetime, timedelta

import uuid
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from models.demo_resource import DemoResource
from models.access import AccessPolicy
from models.tag import Tag

from tests.utils import (
    one_test_demo_resource,
    token_user1_read,
    token_user1_read_write,
    token_admin,
    token_admin_read,
    token_admin_read_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_post_demo_resource(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests POST of a demo_resource."""

    app_override_get_azure_payload_dependency

    resource = one_test_demo_resource
    time_before_post = datetime.now()
    response = await async_client.post("/api/v1/demoresource/", json=resource)
    time_after_post = datetime.now()

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == one_test_demo_resource["name"]
    assert content["description"] == one_test_demo_resource["description"]
    # TBD: implement an AccessLog view,
    # to check if the access was logged correctly
    # and remove this!
    assert (
        time_before_post - timedelta(seconds=25)
        < datetime.fromisoformat(content["created_at"])
        < time_after_post + timedelta(seconds=25)
    )
    assert "id" in content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_post_demo_resource_with_nonexisting_category(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests POST of a demo_resource."""

    app_override_get_azure_payload_dependency

    resource = one_test_demo_resource
    resource["category_id"] = str(uuid.uuid4())
    # print("=== resource ===")
    # print(resource)
    # get_async_test_session
    response = await async_client.post("/api/v1/demoresource/", json=resource)
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not found"


# TBD: add a test, that checks if the category_id is existing in the database!


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user1_read_write,
        token_admin,
        token_admin_read,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_get_all_demo_resources(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests GET all demo resources."""
    app_override_get_azure_payload_dependency
    resources = await add_test_demo_resources(mocked_get_azure_token_payload)
    response = await async_client.get("/api/v1/demoresource/")

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
        assert "id" in response_item

    # assert 0


@pytest.mark.anyio
async def test_get_all_public_demo_resources(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Tests GET all demo resources."""
    resources = await add_test_demo_resources()
    for resource in resources:
        policy = {
            "resource_id": resource.id,
            "resource_type": "DemoResource",
            "action": "read",
            "public": True,
        }
        await add_test_policy_for_resource(policy)
    response = await async_client.get("/api/v1/demoresource/")

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
        assert "id" in response_item


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read, token_user1_read_write, token_admin, token_admin_read],
    indirect=True,
)
async def test_get_demo_resource_by_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests GET of a demo resources."""
    app_override_get_azure_payload_dependency
    resources = await add_test_demo_resources(mocked_get_azure_token_payload)

    # time_before_get_call = datetime.now()
    response = await async_client.get(f"/api/v1/demoresource/{resources[0].id}")
    # time_after_get_call = datetime.now()
    # print("== test_get_demo_resource_by_id - get call time ===")
    # print((time_after_get_call - time_before_get_call).total_seconds())
    # solution with SQLModel back_population of tables: about 0.07 - 0.14 seconds
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert "id" in content
    assert "tags" in content
    assert "category" in content

    # assert 0


@pytest.mark.anyio
async def test_get_public_demo_resource_by_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    add_test_policy_for_resource: AccessPolicy,
):
    """Tests GET of a demo resources."""
    resources = await add_test_demo_resources()
    policy = {
        "resource_id": resources[0].id,
        "resource_type": "DemoResource",
        "action": "read",
        "public": True,
    }
    await add_test_policy_for_resource(policy)

    # time_before_get_call = datetime.now()
    response = await async_client.get(f"/api/v1/demoresource/{resources[0].id}")
    # time_after_get_call = datetime.now()
    # print("== test_get_demo_resource_by_id - get call time ===")
    # print((time_after_get_call - time_before_get_call).total_seconds())
    # solution with SQLModel back_population of tables: about 0.07 - 0.14 seconds
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert "id" in content
    assert "tags" in content
    assert "category" in content

    # assert 0


@pytest.mark.anyio
async def test_get_demo_resource_by_invalid_id_type(async_client: AsyncClient):
    """Tests GET of a demo resources with invalid id."""

    response = await async_client.get("/api/v1/demoresource/invalid_id")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_demo_resource_by_nonexisting_uuid(async_client: AsyncClient):
    """Tests GET of a demo resources with invalid id."""

    response = await async_client.get(f"/api/v1/demoresource/{str(uuid.uuid4())}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not found."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests PUT of a demo resource."""

    app_override_get_azure_payload_dependency

    resources = await add_test_demo_resources(mocked_get_azure_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "language": "es-ES",
        # "timezone": "UTC+9",
    }
    time_before_crud = datetime.now()
    response = await async_client.put(
        f"/api/v1/demoresource/{resources[0].id}", json=updated_resource
    )
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


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource_partial_update(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests PUT of a demo resource, where not all fields are updated."""

    app_override_get_azure_payload_dependency

    resources = await add_test_demo_resources(mocked_get_azure_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        # "timezone": "UTC+10",
    }
    response = await async_client.put(
        f"/api/v1/demoresource/{resources[0].id}", json=updated_resource
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    # print("=== resources[0].language ===")
    # print(resources[0].language)
    # print("=== content['language'] ===")
    # print(content["language"])
    assert content["language"] == resources[0].language  # this one is not updated!


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource_by_invalid_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests PUT of a demo resources with invalid id."""

    app_override_get_azure_payload_dependency

    await add_test_demo_resources(mocked_get_azure_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        # "timezone": "UTC+10",
    }
    response = await async_client.put(
        "/api/v1/demoresource/not_an_integer", json=updated_resource
    )

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource_by_resource_does_not_exist(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests PUT of nonexisting demo resources."""

    app_override_get_azure_payload_dependency

    await add_test_demo_resources(mocked_get_azure_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        # "timezone": "UTC+10",
    }
    response = await async_client.put(
        f"/api/v1/demoresource/{str(uuid.uuid4())}", json=updated_resource
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not updated."


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
#     response = await async_client.put("/api/v1/demoresource/1", json=updated_resource)

#     assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_delete_demo_resource(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests DELETE of a demo resource."""

    app_override_get_azure_payload_dependency

    resources = await add_test_demo_resources(mocked_get_azure_token_payload)
    response = await async_client.get(f"/api/v1/demoresource/{str(resources[0].id)}")

    # Check if resource exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(resources[0].id)
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language

    # Delete resource:
    response = await async_client.delete(f"/api/v1/demoresource/{str(resources[0].id)}")
    assert response.status_code == 200
    content = response.json()
    # assert "Deleted resource ${id}." in content["detail"]
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language

    # Check if resource exists after deleting:
    response = await async_client.get(f"/api/v1/demoresource/{str(resources[0].id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not found."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_delete_demo_resource_by_invalid_id(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests DELETE of a demo resources with invalid id."""

    app_override_get_azure_payload_dependency

    response = await async_client.delete("/api/v1/demoresource/invalid_id")

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_delete_demo_resource_by_resource_does_not_exist(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests GET of a demo resources."""

    app_override_get_azure_payload_dependency

    response = await async_client.delete(f"/api/v1/demoresource/{str(uuid.uuid4())}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not deleted."


@pytest.mark.anyio
async def test_attach_tag_to_demo_resource(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    add_test_tags: list[Tag],
):
    """Tests POST of a tag to a demo resource."""
    resources = await add_test_demo_resources()
    tags = await add_test_tags()
    response = await async_client.post(
        f"/api/v1/demoresource/{str(resources[1].id)}/tag/?tag_ids={str(tags[0].id)}&tag_ids={str(tags[2].id)}"
    )
    # for tag_id in tag_ids:
    #     response = await async_client.post(
    #         f"/api/v1/demoresource/{resource_id}/tag/{tag_id}"
    #     )

    assert response.status_code == 200
    content = response.json()
    assert len(content["tags"]) == 2
    assert content["tags"][0]["name"] in [
        tags[0].name,
        tags[2].name,
    ]
    assert content["tags"][1]["name"] in [
        tags[0].name,
        tags[2].name,
    ]
