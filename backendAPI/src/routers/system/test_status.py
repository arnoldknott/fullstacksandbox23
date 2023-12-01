import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_system_health(async_client: AsyncClient):
    """Test that we can get all posts."""
    response = await async_client.get("/system/health")

    assert response.status_code == 200
    assert {"status": "ok"} == response.json()
