from typing import AsyncGenerator, Generator

import pytest
from core.databases import postgres_async_engine
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


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
        # for table in SQLModel.metadata.tables.values():
        #     await connection.execute(
        #         f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1"
        #     )

    yield

    async with postgres_async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        # for table in SQLModel.metadata.tables.values():
        #     await connection.execute(
        #         f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1"
        #     )
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
        # await session.rollback()
