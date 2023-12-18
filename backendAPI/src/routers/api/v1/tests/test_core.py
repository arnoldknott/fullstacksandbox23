import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_system_health(async_client: AsyncClient):
    """Tests the health endpoint of the API."""
    response = await async_client.get("/api/v1/core/health")

    assert response.status_code == 200
    assert {"status": "ok"} == response.json()


@pytest.mark.anyio
async def test_get_keyvault_health(async_client: AsyncClient):
    """Test that the keyvault configuration got read and cached at system startup."""
    response = await async_client.get("/api/v1/core/keyvault")

    assert response.status_code == 200
    assert "Azure keyvault status" in response.json().keys()
    assert "ok" in response.json()["Azure keyvault status"]
