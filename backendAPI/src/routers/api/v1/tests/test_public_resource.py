import secrets
import uuid

import pytest
from httpx import AsyncClient

from models.public_resource import PublicResource


@pytest.mark.anyio
async def test_post_public_resource(async_client: AsyncClient):
    """Tests POST of a public_resource."""
    public_resource = {
        "comment": "TestPublicResource",
    }
    response = await async_client.post("/api/v1/publicresource/", json=public_resource)

    assert response.status_code == 201
    content = response.json()
    assert content["comment"] == public_resource["comment"]
    assert "id" in content


@pytest.mark.anyio
async def test_post_public_resource_comment_too_long(async_client: AsyncClient):
    """Tests POST of too long public_resource."""
    public_resource = {
        "comment": "TestPublicResource with more than 500 characters"
        + secrets.token_hex(250),
    }
    response = await async_client.post("/api/v1/publicresource/", json=public_resource)

    content = response.json()

    assert response.status_code == 422
    assert content["detail"][0]["type"] == "string_too_long"


@pytest.mark.anyio
async def test_get_all_public_resources(
    async_client: AsyncClient,
    add_test_public_resources: list[PublicResource],
):
    """Tests GET all public_resources."""
    public_resources = add_test_public_resources
    response = await async_client.get("/api/v1/publicresource/")

    assert response.status_code == 200
    assert len(response.json()) == 4
    content = response.json()[3]
    assert content["comment"] == public_resources[3].comment
    assert "id" in content


@pytest.mark.anyio
async def test_get_public_resource_by_id(
    async_client: AsyncClient, add_test_public_resources: list[PublicResource]
):
    """Tests GET all public_resources."""
    public_resources = add_test_public_resources
    response = await async_client.get(
        f"/api/v1/publicresource/{str(public_resources[1].id)}"
    )

    assert response.status_code == 200
    content = response.json()
    assert content["comment"] == public_resources[1].comment
    assert "id" in content


@pytest.mark.anyio
async def test_get_public_resource_by_invalid_id(async_client: AsyncClient):
    """Tests GET of a public_resource with invalid id."""

    response = await async_client.get("/api/v1/publicresource/invalid_id")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_put_public_resource(
    async_client: AsyncClient, add_test_public_resources: list[PublicResource]
):
    """Tests PUT of a ta."""
    public_resources = add_test_public_resources
    updated_public_resource = {
        "comment": "NewPublicResource",
    }
    response = await async_client.put(
        f"/api/v1/publicresource/{str(public_resources[1].id)}",
        json=updated_public_resource,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["comment"] == updated_public_resource["comment"]


@pytest.mark.anyio
async def test_put_public_resource_does_not_exist(
    async_client: AsyncClient, add_test_public_resources: list[PublicResource]
):
    """Tests PUT of a public_resource."""
    add_test_public_resources
    updated_public_resource = {
        "comment": "update public resource",
    }
    response = await async_client.put(
        f"/api/v1/publicresource/{str(uuid.uuid4())}", json=updated_public_resource
    )

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_delete_public_resource(
    async_client: AsyncClient, add_test_public_resources: list[PublicResource]
):
    """Tests DELETE of a public_resource."""
    public_resources = add_test_public_resources
    response = await async_client.get(
        f"/api/v1/publicresource/{str(public_resources[1].id)}"
    )

    # Check if public_resource exists before deleting:
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(public_resources[1].id)
    assert content["comment"] == public_resources[1].comment

    # Delete public_resource:
    response = await async_client.delete(
        f"/api/v1/publicresource/{str(public_resources[1].id)}"
    )
    assert response.status_code == 200
    content = response.json()
    assert content["comment"] == public_resources[1].comment

    # Check if public_resource exists after deleting:
    response = await async_client.get(
        f"/api/v1/publicresource/{str(public_resources[1].id)}"
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"


@pytest.mark.anyio
async def test_delete_public_resource_by_invalid_id(async_client: AsyncClient):
    """Tests DELETE of a public_resource with invalid id."""
    response = await async_client.delete("/api/v1/publicresource/invalid_id")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_delete_public_resource_does_not_exist(
    async_client: AsyncClient, add_test_public_resources: list[PublicResource]
):
    """Tests DELETE of a public_resource."""
    add_test_public_resources
    response = await async_client.delete(f"/api/v1/publicresource/{str(uuid.uuid4())}")

    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Object not found"
