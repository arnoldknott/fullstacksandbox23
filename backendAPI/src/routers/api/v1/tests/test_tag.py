import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models.tag import Tag
from tests.utils import (
    token_admin,
    token_admin_read,
    token_admin_read_write,
    token_admin_write,
    token_user1_read,
    token_user1_read_write,
    token_user1_write,
    token_user2_read,
    token_user2_read_write,
    token_user2_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_post_tag(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests POST of a tag."""

    app_override_get_azure_payload_dependency

    tag = {
        "name": "TestTag",
    }
    response = await async_client.post("/api/v1/tag/", json=tag)

    assert response.status_code == 201
    content = response.json()
    assert content["name"] == tag["name"]
    assert "id" in content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_post_tag_name_too_long(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests POST of too long tag."""

    app_override_get_azure_payload_dependency

    tag = {
        "name": "TestTag  with more than 10 characters",
    }
    response = await async_client.post("/api/v1/tag/", json=tag)

    content = response.json()

    assert response.status_code == 422
    assert content["detail"][0]["type"] == "string_too_long"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user1_read_write,
        token_user2_read,
        token_user2_read_write,
        token_admin,
        token_admin_read,
    ],
    indirect=True,
)
async def test_get_all_tags(
    async_client: AsyncClient,
    add_test_tags: list[Tag],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload: dict,
):
    """Tests GET all tags."""
    app_override_get_azure_payload_dependency
    tags = await add_test_tags(mocked_get_azure_token_payload)
    response = await async_client.get("/api/v1/tag/")

    assert response.status_code == 200
    database_tags = response.json()
    assert len(database_tags) == 4
    for database_tag, mocked_tag in zip(database_tags, tags):
        assert database_tag["name"] == mocked_tag.name
        assert database_tag["id"] == str(mocked_tag.id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user1_read_write,
        token_user2_read,
        token_user2_read_write,
        token_admin,
        token_admin_read,
    ],
    indirect=True,
)
async def test_get_tag_by_id(
    async_client: AsyncClient,
    add_test_tags: list[Tag],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload: dict,
):
    """Tests GET all tags."""
    app_override_get_azure_payload_dependency
    tags = await add_test_tags(mocked_get_azure_token_payload)

    response = await async_client.get(f"/api/v1/tag/{str(tags[1].id)}")

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == tags[1].name
    assert "id" in content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_read,
        token_user1_read_write,
        token_user2_read,
        token_user2_read_write,
        token_admin,
        token_admin_read,
    ],
    indirect=True,
)
async def test_get_tag_by_invalid_id(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests GET of a tag with invalid id."""
    app_override_get_azure_payload_dependency
    response = await async_client.get("/api/v1/tag/invalid_id")
    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_put_tag(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_test_tags: list[Tag],
    mocked_get_azure_token_payload: dict,
):
    """Tests PUT of a tag."""

    app_override_get_azure_payload_dependency

    tags = await add_test_tags(mocked_get_azure_token_payload)

    updated_tag = {
        "name": "NewTag",
    }
    response = await async_client.put(
        f"/api/v1/tag/{str(tags[1].id)}", json=updated_tag
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == updated_tag["name"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_put_tag_does_not_exist(
    async_client: AsyncClient,
    add_test_tags: list[Tag],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload: dict,
):
    """Tests PUT of a tag."""

    app_override_get_azure_payload_dependency

    await add_test_tags(mocked_get_azure_token_payload)

    updated_tag = {
        "name": "Uptag",
    }
    response = await async_client.put(
        f"/api/v1/tag/{str(uuid.uuid4())}", json=updated_tag
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Tag not updated."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_delete_tag(
    async_client: AsyncClient,
    add_test_tags: list[Tag],
    # add_test_policy_for_resource: AccessPolicy,
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload: dict,
):
    """Tests DELETE of a tag."""

    app_override_get_azure_payload_dependency

    tags = await add_test_tags(mocked_get_azure_token_payload)
    # the get endpoints are public, so no current user is passed -
    # that means all tags need a public access policy in the fine grained access control!
    # TBD: should this be solved in the tags_CRUD, create method;
    # potentially implement a create_public method, which calls the create method
    # and adds the public access policy
    # for tag in tags:
    #     policy = {
    #         "resource_id": tag.id,
    #         "resource_type": "Tag",
    #         "action": "read",
    #         "public": True,
    #     }
    #     await add_test_policy_for_resource(policy)
    response = await async_client.get(f"/api/v1/tag/{str(tags[1].id)}")

    # Check if tag exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(tags[1].id)
    assert content["name"] == tags[1].name

    # Delete tag:
    response = await async_client.delete(f"/api/v1/tag/{str(tags[1].id)}")
    assert response.status_code == 200
    # content = response.json()
    # assert content["name"] == tags[1].name

    # Check if tag exists after deleting:
    response = await async_client.get(f"/api/v1/tag/{str(tags[1].id)}")
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Tag not found."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_delete_tag_by_invalid_id(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests DELETE of a tag with invalid id."""

    app_override_get_azure_payload_dependency

    response = await async_client.delete("/api/v1/tag/invalid_id")

    assert response.status_code == 422


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_user1_write,
        token_user1_read_write,
        token_user2_write,
        token_user2_read_write,
        token_admin_write,
        token_admin_read_write,
    ],
    indirect=True,
)
async def test_delete_tag_does_not_exist(
    async_client: AsyncClient,
    add_test_tags: list[Tag],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload: dict,
):
    """Tests DELETE of a tag."""

    app_override_get_azure_payload_dependency

    await add_test_tags(mocked_get_azure_token_payload)
    response = await async_client.delete(f"/api/v1/tag/{str(uuid.uuid4())}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Tag not deleted."


# @pytest.mark.anyio
# async def test_get_all_demo_resources_by_category_id(
#     async_client: AsyncClient,
#     add_test_demo_resources_with_category: list[DemoResource],
# ):
#     """Tests GET all demo resources by category id."""
#     resources = add_test_demo_resources_with_category
#     response = await async_client.get("/api/v1/category/2/demoresources")

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
#     response = await async_client.get("/api/v1/category/3/demoresources")

#     print(response.json())
#     assert response.status_code == 404
#     content = response.json()
#     assert content["detail"] == "No demo resources found"
