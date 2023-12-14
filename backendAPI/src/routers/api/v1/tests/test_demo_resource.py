import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import demo_resource_test_input


# , get_async_test_session: AsyncSession
@pytest.mark.anyio
# @pytest.mark.usefixtures("get_async_test_session")
async def test_post_demo_resource(
    async_client: AsyncClient, get_async_test_session: AsyncSession
):
    """Tests POST of a demo_resource."""
    resource = demo_resource_test_input
    # await get_async_test_session()
    response = await async_client.post("/api/v1/demo_resource/", json=resource)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == demo_resource_test_input["name"]
    assert content["description"] == demo_resource_test_input["description"]
    assert "id" in content


# TBD: check for correct data in response
# @pytest.mark.anyio
# async def test_get_demo_resource(async_client: AsyncClient):
#     """Tests GET all demo resources."""
#     response = await async_client.get("/api/v1/demo_resource/")

#     assert response.status_code == 200
#     assert len(response.json()) == 1
#     assert response.json()[0]["description"] == "ok"
#     assert "id" in response.json()[0]
#     # assert DemoResource == [
#     #     DemoResource(**item).model_dump() for item in response.json()
#     # ]


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
