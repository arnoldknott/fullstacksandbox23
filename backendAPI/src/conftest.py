from typing import AsyncGenerator, Generator

import pytest
from core.databases import postgres_async_engine
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from sqlmodel import SQLModel


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
    # api_url = str(client.base_url).rstrip("/") + global_prefix
    # async with AsyncClient(app=app, base_url=api_url) as async_client:
    #     yield async_client
    async with AsyncClient(app=app, base_url=client.base_url) as async_client:
        yield async_client


# postgres_async_engine = create_async_engine(config.POSTGRES_URL.unicode_string())
# print(config.POSTGRES_URL.unicode_string())

# Using an extra session for the test - this also works!
# postgres_async_test_engine = create_async_engine(config.POSTGRES_URL.unicode_string())
# # scope="session"
# @pytest.fixture()
# async def get_async_test_session() -> AsyncSession:
#     """Returns a database session."""
#     async_session = async_sessionmaker(
#         bind=postgres_async_test_engine, class_=AsyncSession, expire_on_commit=False
#     )
#     async with async_session() as session:
#         async with postgres_async_test_engine.begin() as connection:
#             await connection.run_sync(SQLModel.metadata.create_all)
#             yield session
#             await connection.run_sync(SQLModel.metadata.drop_all)

#     await postgres_async_test_engine.dispose()

# Wrong: test functions don't need a database session - that's part of the program code
# HOWEVER: the test environment needs to configure the database (do the migrations)
# and reset the database after all sessions are done!
# # scope="session"
# @pytest.fixture(scope="function")
# async def get_async_test_session() -> AsyncSession:
#     """Returns a database session."""
#     async_session = async_sessionmaker(
#         bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
#     )
#     print("=== type of async_session ===")
#     print(type(async_session))
#     async with async_session() as session:
#         async with postgres_async_engine.begin() as connection:
#             await connection.run_sync(SQLModel.metadata.create_all)
#             yield session
#             await connection.run_sync(SQLModel.metadata.drop_all)

#     await postgres_async_engine.dispose()


@pytest.fixture(scope="session", autouse=True)  # , autouse=True
async def run_migrations():
    """Runs the migrations before each test function."""
    async with postgres_async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    yield

    async with postgres_async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
        await postgres_async_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def clear_tables():
    async with postgres_async_engine.begin() as connection:
        for tabled in reversed(SQLModel.metadata.sorted_tables):
            await connection.execute(tabled.delete())

    yield

    # async_session = get_async_session()
    # async with async_session() as session:
    # SQLModel.metadata.create_all(postgres_async_engine)
    # yield
    # SQLModel.metadata.drop_all(postgres_async_engine)
    # ==============
    # async with postgres_async_engine.begin() as connection:
    #     await connection.run_sync(SQLModel.metadata.create_all)
    #     yield
    #     await connection.run_sync(SQLModel.metadata.drop_all)
    # ==============
    # await SQLModel.metadata.create_all(postgres_async_engine)
    # yield
    # await SQLModel.metadata.drop_all(postgres_async_engine)
    # session = get_async_session()
    # async with session:
    #     await connection.run_sync(SQLModel.metadata.create_all)
    #     yield
    #     await connection.run_sync(SQLModel.metadata.drop_all)
