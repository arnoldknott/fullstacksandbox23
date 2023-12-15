import pytest
from httpx import AsyncClient
from utils import demo_resource_test_input, demo_resource_test_inputs


# , get_async_test_session: AsyncSession
@pytest.mark.anyio
# @pytest.mark.usefixtures("run_migrations")
# @pytest.mark.usefixtures("get_async_test_session")
# async def test_post_demo_resource(async_client: AsyncClient, get_async_test_session):
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
async def test_get_demo_resource(async_client: AsyncClient):
    """Tests GET all demo resources."""
    resources = demo_resource_test_inputs
    for resource in resources:
        response = await async_client.post("/api/v1/demo_resource/", json=resource)
        assert response.status_code == 201
    response = await async_client.get("/api/v1/demo_resource/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    for response_item in response.json():
        assert response_item["name"] in [
            resources[0]["name"],
            resources[1]["name"],
        ]
        assert response_item["description"] in [
            resources[0]["description"],
            resources[1]["description"],
        ]
        assert response_item["language"] in [
            resources[0]["language"],
            resources[1]["language"],
        ]
        assert response_item["timezone"] in [
            resources[0]["timezone"],
            resources[1]["timezone"],
        ]
        assert "id" in response_item


@pytest.mark.anyio
async def test_get_demo_resource_by_id(async_client: AsyncClient):
    """Tests GET of a demo resources."""
    # TBD: turn into fixture, that puts in data into the database for testing.
    resource = demo_resource_test_inputs
    response = await async_client.post("/api/v1/demo_resource/", json=resource[0])
    response = await async_client.post("/api/v1/demo_resource/", json=resource[1])
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == demo_resource_test_inputs[1]["name"]
    assert content["description"] == demo_resource_test_inputs[1]["description"]
    assert "id" in content

    response = await async_client.get("/api/v1/demo_resource/2")
    # assert response.status_code == 200
    # assert response.json()["name"] == demo_resource_test_input["name"]
    # assert response.json()["description"] == demo_resource_test_input["description"]
    # assert "id" in response.json()


# @pytest.mark.anyio
# async def test_get_demo_resource_by_id(async_client: AsyncClient):
#     """Tests GET of a demo resources."""
#     response = await async_client.get("/api/v1/demo_resource/1")

#     assert response.status_code == 200
#     assert {"status": "ok"} == response.json()


# @pytest.mark.anyio
# async def test_put_demo_resource(async_client: AsyncClient):
#     """Tests PUT of a demo resource."""
#     response = await async_client.get("/demo_resource/1")

#     assert response.status_code == 200
#     assert {"status": "ok"} == response.json()


# @pytest.mark.anyio
# async def test_delete_demo_resource(async_client: AsyncClient):
#     """Tests DELETE of a demo resource."""
#     response = await async_client.get("/demo_resource/1")

#     assert response.status_code == 200
#     assert {"status": "ok"} == response.json()
