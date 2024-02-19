from typing import AsyncGenerator, Generator

import pytest
from core.databases import postgres_async_engine  # should be SQLite here only!
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from core.security import get_azure_token_payload


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for pytest."""
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    """Returns a TestClient instance."""
    yield TestClient(app)


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    """Returns an AsyncClient instance."""
    async with AsyncClient(app=app, base_url=client.base_url) as async_client:
        yield async_client


@pytest.fixture(scope="function", autouse=True)
async def run_migrations():
    """Runs the migrations before each test function."""
    async with postgres_async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    yield

    async with postgres_async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await postgres_async_engine.dispose()


@pytest.fixture(scope="function")
async def get_async_test_session() -> AsyncSession:
    """Returns a database session."""
    print("=== get_async_test_session started ===")
    async_session = async_sessionmaker(
        bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def mocked_get_azure_token_payload(request):
    """Returns a mocked token payload."""

    def inner():
        return {
            "tid": "mocked_tid",
            "groups": "mocked_groups",
            **request.param,
        }

    return inner


# @pytest.fixture
# def mocked_get_azure_token_payload(request):
#     '''Returns an app with mocked access token payload.'''
#     print ("=== mocked_get_azure_token_payload - request ===")
#     print (request.param)
#     app.dependency_overrides[get_azure_token_payload] = request.param
#     return app


@pytest.fixture
def app_override_get_azure_payload_dependency(mocked_get_azure_token_payload):
    """Returns the FastAPI app with dependency pverride for get_azure_token_payload."""
    app.dependency_overrides[get_azure_token_payload] = mocked_get_azure_token_payload
    return app
