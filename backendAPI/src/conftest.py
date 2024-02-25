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
from models.user import User
from crud.user import UserCRUD
from tests.utils import one_test_user, many_test_users, token_payload_many_groups


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


@pytest.fixture(scope="function")
def mocked_get_azure_token_payload(request):
    """Returns a mocked token payload."""
    return request.param

    # def inner():
    #     # if request:
    #     #     return request.param
    #     # else:
    #     #     return {}
    #     return {**request.param}

    # return inner


@pytest.fixture(scope="function")
def app_override_get_azure_payload_dependency(mocked_get_azure_token_payload):
    """Returns the FastAPI app with dependency pverride for get_azure_token_payload."""
    app.dependency_overrides[
        get_azure_token_payload
    ] = lambda: mocked_get_azure_token_payload
    yield app
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def add_one_test_user(get_async_test_session: AsyncSession) -> User:
    """Adds a category to the database."""
    session = get_async_test_session
    user = User(**one_test_user)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    yield user


@pytest.fixture(scope="function")
async def add_one_test_user_with_groups(get_async_test_session: AsyncSession) -> User:
    """Adds a category to the database."""
    async with UserCRUD() as crud:
        user = await crud.create_azure_user_and_groups_if_not_exist(
            one_test_user["azure_user_id"],
            one_test_user["azure_tenant_id"],
            token_payload_many_groups["groups"],
        )

    yield user


@pytest.fixture(scope="function")
async def add_many_test_users(
    get_async_test_session: AsyncSession,
) -> list[User]:
    """Adds a category to the database."""
    async with UserCRUD() as crud:
        users = []
        for user in many_test_users:
            added_user = await crud.create_azure_user_and_groups_if_not_exist(
                user["azure_user_id"],
                user["azure_tenant_id"],
            )
            users.append(added_user)

    yield users


@pytest.fixture(scope="function")
async def add_many_test_users_with_groups(
    get_async_test_session: AsyncSession,
) -> list[User]:
    """Adds a category to the database."""
    async with UserCRUD() as crud:
        users = []
        for user in many_test_users:
            added_user = await crud.create_azure_user_and_groups_if_not_exist(
                user["azure_user_id"],
                user["azure_tenant_id"],
                token_payload_many_groups["groups"],
            )
            users.append(added_user)

    yield users
