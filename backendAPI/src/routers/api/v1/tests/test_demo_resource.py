import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action
from crud.access import AccessLoggingCRUD
from models.access import AccessLogRead, AccessPolicy
from models.demo_resource import DemoResource, DemoResourceRead
from models.tag import Tag
from tests.utils import (
    one_test_demo_resource,
    token_admin,
    token_admin_read,
    token_admin_read_write,
    token_user1_read,
    token_user1_read_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_post_demo_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    current_user_from_azure_token,
    mocked_provide_http_token_payload,
):
    """Tests POST of a demo_resource."""

    app_override_provide_http_token_payload

    resource = one_test_demo_resource
    before_time = datetime.now()
    response = await async_client.post("/api/v1/demoresource/", json=resource)
    after_time = datetime.now()

    assert response.status_code == 201
    content = response.json()
    assert uuid.UUID(content["id"])
    assert content["name"] == one_test_demo_resource["name"]
    assert content["description"] == one_test_demo_resource["description"]

    access_log_response = await async_client.get(
        f"/api/v1/access/log/{content['id']}/last-accessed"
    )

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    assert access_log_response.status_code == 200
    last_accessed_at = AccessLogRead(**access_log_response.json())

    assert last_accessed_at.time > before_time - timedelta(seconds=1)
    assert last_accessed_at.time < after_time + timedelta(seconds=1)
    assert last_accessed_at.resource_id == uuid.UUID(content["id"])
    assert last_accessed_at.identity_id == current_user.user_id
    assert last_accessed_at.action == Action.own


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_post_demo_resource_with_nonexisting_category(
    async_client: AsyncClient, app_override_provide_http_token_payload: FastAPI
):
    """Tests POST of a demo_resource."""

    app_override_provide_http_token_payload

    resource = one_test_demo_resource
    resource["category_id"] = str(uuid.uuid4())
    response = await async_client.post("/api/v1/demoresource/", json=resource)
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "DemoResource - Forbidden."


# TBD: add a test, that checks if the category_id is existing in the database!


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
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
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET all demo resources."""
    app_override_provide_http_token_payload
    resources = await add_test_demo_resources(mocked_provide_http_token_payload)
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
    "mocked_provide_http_token_payload",
    [token_user1_read, token_user1_read_write, token_admin, token_admin_read],
    indirect=True,
)
async def test_get_demo_resource_by_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET of a demo resources."""
    app_override_provide_http_token_payload
    resources = await add_test_demo_resources(mocked_provide_http_token_payload)

    # before_time = datetime.now()
    response = await async_client.get(f"/api/v1/demoresource/{resources[0].id}")
    # after_time = datetime.now()
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert "id" in content
    assert "tags" in content
    assert "category" in content


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
        # "resource_type": "DemoResource",
        "action": "read",
        "public": True,
    }
    await add_test_policy_for_resource(policy)

    # before_time = datetime.now()
    response = await async_client.get(f"/api/v1/demoresource/{resources[0].id}")
    # after_time = datetime.now()
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert "id" in content
    assert "tags" in content
    assert "category" in content


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
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_user_from_azure_token,
):
    """Tests PUT of a demo resource."""

    app_override_provide_http_token_payload

    resources = await add_test_demo_resources(mocked_provide_http_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
        "language": "es-ES",
    }
    time_before_crud = datetime.now()
    response = await async_client.put(
        f"/api/v1/demoresource/{resources[0].id}", json=updated_resource
    )
    time_after_crud = datetime.now()

    assert response.status_code == 200
    content = response.json()

    current_user = await current_user_from_azure_token(
        mocked_provide_http_token_payload
    )

    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            current_user, resource_id=content["id"]
        )

    assert (
        time_before_crud - timedelta(seconds=1)
        < created_at
        < time_after_crud + timedelta(seconds=1)
    )
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    assert content["language"] == updated_resource["language"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource_partial_update(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of a demo resource, where not all fields are updated."""

    app_override_provide_http_token_payload

    resources = await add_test_demo_resources(mocked_provide_http_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
    }
    response = await async_client.put(
        f"/api/v1/demoresource/{resources[0].id}", json=updated_resource
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_resource["name"]
    assert content["description"] == updated_resource["description"]
    assert content["language"] == resources[0].language  # this one is not updated!


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource_by_invalid_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of a demo resources with invalid id."""

    app_override_provide_http_token_payload

    await add_test_demo_resources(mocked_provide_http_token_payload)
    updated_resource = {
        "name": "Updated Name",
        "description": "Updated Description",
    }
    response = await async_client.put(
        "/api/v1/demoresource/not_an_integer", json=updated_resource
    )

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_put_demo_resource_by_resource_does_not_exist(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests PUT of nonexisting demo resources."""

    app_override_provide_http_token_payload

    await add_test_demo_resources(mocked_provide_http_token_payload)
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
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_delete_demo_resource(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    current_test_user
):
    """Tests DELETE of a demo resource."""

    app_override_provide_http_token_payload

    resources = await add_test_demo_resources(mocked_provide_http_token_payload)
    current_user = current_test_user

    # Check if resource exists before deleting:
    response = await async_client.get(f"/api/v1/demoresource/{str(resources[0].id)}")
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(resources[0].id)
    assert content["name"] == resources[0].name
    assert content["description"] == resources[0].description
    assert content["language"] == resources[0].language

    # Check if access policy for resource is present before delete
    response_access_before = await async_client.get(f"/api/v1/access/policy/resource/{str(resources[0].id)}")
    assert response_access_before.status_code == 200
    access_policies_before = response_access_before.json()
    assert len(access_policies_before) == 1
    assert access_policies_before[0]["resource_id"] == str(resources[0].id)
    assert access_policies_before[0]["identity_id"] == str(current_user.user_id)
    assert access_policies_before[0]["action"] == Action.own
    assert access_policies_before[0]["public"] == False

    # Delete resource:
    response = await async_client.delete(f"/api/v1/demoresource/{str(resources[0].id)}")
    assert response.status_code == 200
    # content = response.json()
    # # assert "Deleted resource ${id}." in content["detail"]
    # assert content["name"] == resources[0].name
    # assert content["description"] == resources[0].description
    # assert content["language"] == resources[0].language

    # Check if resource exists after deleting:
    response = await async_client.get(f"/api/v1/demoresource/{str(resources[0].id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not found."

    # Check if access policy for resource is deleted after deleting the demo resource
    response_access_after = await async_client.get(f"/api/v1/access/policy/resource/{str(resources[0].id)}")
    assert response_access_after.status_code == 200
    access_policies_after = response_access_after.json()
    assert len(access_policies_after) == 0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_admin_read_write],
    indirect=True,
)
async def test_delete_demo_resource_by_invalid_id(
    async_client: AsyncClient, app_override_provide_http_token_payload: FastAPI
):
    """Tests DELETE of a demo resources with invalid id."""

    app_override_provide_http_token_payload

    response = await async_client.delete("/api/v1/demoresource/invalid_id")

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_delete_demo_resource_by_resource_does_not_exist(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
):
    """Tests GET of a demo resources."""

    app_override_provide_http_token_payload

    response = await async_client.delete(f"/api/v1/demoresource/{str(uuid.uuid4())}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "DemoResource not deleted."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_attach_tag_to_demo_resource(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    add_test_demo_resources: list[DemoResource],
    mocked_provide_http_token_payload,
    add_test_tags: list[Tag],
):
    """Tests POST of a tag to a demo resource."""

    app_override_provide_http_token_payload

    resources = await add_test_demo_resources(mocked_provide_http_token_payload)
    tags = await add_test_tags(mocked_provide_http_token_payload)
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


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin, token_admin_read_write, token_user1_read_write, token_user1_read],
    indirect=True,
)
async def test_get_all_demo_resources_by_category_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET all demo resources by category id."""

    app_override_provide_http_token_payload
    resources = await add_test_demo_resources(mocked_provide_http_token_payload)

    categories = await async_client.get("/api/v1/category/")
    categories = categories.json()

    response = await async_client.get(
        f"/api/v1/demoresource/category/{str(categories[1]['id'])}"
    )

    assert response.status_code == 200
    database_demo_resources = response.json()
    resources = [
        resource
        for resource in resources
        if resource.category_id == uuid.UUID(categories[1]["id"])
    ]
    assert len(database_demo_resources) == 2
    first_content = database_demo_resources[0]
    assert first_content["name"] == resources[0].name
    assert first_content["description"] == resources[0].description
    assert first_content["language"] == resources[0].language
    assert "category_id" in first_content

    second_content = database_demo_resources[1]
    assert second_content["name"] == resources[1].name
    assert second_content["description"] == resources[1].description
    assert second_content["language"] == resources[1].language
    assert "category_id" in second_content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin, token_admin_read_write, token_user1_read_write, token_user1_read],
    indirect=True,
)
async def test_get_demo_resources_for_lonely_category(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET error for category, that has no demo resources attached."""

    app_override_provide_http_token_payload

    await add_test_demo_resources(mocked_provide_http_token_payload)
    # add_test_demo_resources
    categories_response = await async_client.get("/api/v1/category/")
    categories = categories_response.json()
    response = await async_client.get(
        f"/api/v1/demoresource/category/{str(categories[2]['id'])}"
    )

    assert response.status_code == 200
    content = response.json()
    assert content == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_user1_read_write,
    ],  # , token_user1_read],
    indirect=True,
)
# TBD: check if this is circumventing the access policies for the demo resources in the CRUD?
async def test_get_all_demo_resources_by_tag_id(
    async_client: AsyncClient,
    add_test_demo_resources: list[DemoResource],
    add_test_tags: list[Tag],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    # current_test_user,
    # add_one_test_access_policy,
):
    """Tests GET all demo resources by category id."""

    app_override_provide_http_token_payload
    resources = await add_test_demo_resources(mocked_provide_http_token_payload)
    tags = await add_test_tags(mocked_provide_http_token_payload)

    # current_user = current_test_user

    # for tag in tags:
    #     await add_one_test_access_policy(
    #         {
    #             "resource_id": str(tag.id),
    #             "resource_type": "DemoResource",
    #             "action": "own",
    #             "identity_id": current_user.user_id,
    #         }
    #     )

    # for resource in resources:
    #     await add_one_test_access_policy(
    #         {
    #             "resource_id": str(resource.id),
    #             "resource_type": "DemoResource",
    #             "action": "write",
    #             "identity_id": current_user.user_id,
    #         }
    #     )

    await async_client.post(
        f"/api/v1/demoresource/{str(resources[0].id)}/tag/?&tag_ids={str(tags[1].id)}"
    )
    await async_client.post(
        f"/api/v1/demoresource/{str(resources[1].id)}/tag/?tag_ids={str(tags[0].id)}&tag_ids={str(tags[2].id)}"
    )
    await async_client.post(
        f"/api/v1/demoresource/{str(resources[3].id)}/tag/?&tag_ids={str(tags[2].id)}"
    )

    response = await async_client.get(f"/api/v1/demoresource/tag/{str(tags[2].id)}")

    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2
    first_content = content[0]
    demo_resource_1 = DemoResourceRead.model_validate(first_content)
    assert demo_resource_1.name == resources[1].name
    assert demo_resource_1.description == resources[1].description
    assert demo_resource_1.language == resources[1].language
    assert "category_id" in first_content
    # print("=== first_content['tags'][0] ===")
    # print(first_content["tags"][0])
    # print("=== tags[0] ===")
    # print(tags[0])
    # # Print the tags of demo_resource_1 before the assertions
    # print()
    # print("=== demo_resource_1 ===")
    # print(demo_resource_1)
    # print([tag.name for tag in demo_resource_1.tags])
    demo_resource_1_tag_names = [tag.name for tag in demo_resource_1.tags]
    assert tags[0].name in demo_resource_1_tag_names
    assert tags[1].name not in demo_resource_1_tag_names
    assert tags[2].name in demo_resource_1_tag_names
    # assert tags[0].name in demo_resource_1.tags.name  # [0]["name"]
    # assert tags[1].name not in demo_resource_1.tags.name  # [0]["name"]
    # assert tags[2].name in demo_resource_1.tags.name  # [0]["name"]
    # assert tags[0].name in first_content["tags"][]  # [0]["name"]
    # assert tags[1].name not in first_content["tags"]  # [0]["name"]
    # assert tags[2].name in first_content["tags"]  # [0]["name"]

    second_content = content[1]
    demo_resource_3 = DemoResourceRead.model_validate(second_content)
    assert demo_resource_3.name == resources[3].name
    assert demo_resource_3.description == resources[3].description
    assert demo_resource_3.language == resources[3].language
    assert "category_id" in second_content
    demo_resource_3_tag_names = [tag.name for tag in demo_resource_3.tags]
    assert tags[0].name not in demo_resource_3_tag_names
    assert tags[1].name not in demo_resource_3_tag_names
    assert tags[2].name in demo_resource_3_tag_names
