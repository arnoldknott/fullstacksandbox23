from typing import AsyncGenerator, Generator, List

import pytest
from core.databases import postgres_async_engine  # should be SQLite here only!
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from core.security import get_azure_token_payload, CurrentAccessToken
from core.types import CurrentUserData
from models.identity import User
from crud.identity import UserCRUD
from models.access import AccessPolicy, AccessPolicyRead
from crud.access import AccessPolicyCRUD
from tests.utils import (
    many_test_users,
    token_payload_many_groups,
    many_test_policies,
)


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
    """Provides a database session."""
    print("=== get_async_test_session started ===")
    async_session = async_sessionmaker(
        bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.close()
    print("=== get_async_test_session ended ===")


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
    app.dependency_overrides[get_azure_token_payload] = (
        lambda: mocked_get_azure_token_payload
    )
    yield app
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def current_test_user(mocked_get_azure_token_payload):
    """Returns the current test user."""
    token = CurrentAccessToken(mocked_get_azure_token_payload)
    return await token.provides_current_user()


# @pytest.fixture(scope="function")
# async def add_one_test_user(get_async_test_session: AsyncSession) -> User:
#     """Adds a test user to the database."""
#     session = get_async_test_session
#     user = User(**many_test_users[0])
#     session.add(user)
#     await session.commit()
#     await session.refresh(user)

#     yield user


# @pytest.fixture(scope="function")
# async def add_one_test_user_with_groups(get_async_test_session: AsyncSession) -> User:
#     """Adds a tst user with group membership to the database."""
#     async with UserCRUD() as crud:
#         user = await crud.create_azure_user_and_groups_if_not_exist(
#             many_test_users[0]["azure_user_id"],
#             many_test_users[0]["azure_tenant_id"],
#             token_payload_many_groups["groups"],
#         )

#     yield user


@pytest.fixture(scope="function")
async def add_many_test_users():
    """Adds many test users to the database."""
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


# @pytest.fixture(scope="function")
# async def add_many_test_users(get_async_test_session: AsyncSession):
#     """Adds test users to the database."""
#     session = get_async_test_session
#     users = []
#     for user in many_test_users:
#         this_user = User(**user)
#         session.add(this_user)
#         await session.commit()
#         await session.refresh(this_user)
#         users.append(this_user)

#     yield users


# @pytest.fixture(scope="function")
# async def add_many_test_users_with_groups() -> list[User]:
#     """Adds many test users with group membership to the database."""
#     async with UserCRUD() as crud:
#         users = []
#         for user in many_test_users:
#             added_user = await crud.create_azure_user_and_groups_if_not_exist(
#                 user["azure_user_id"],
#                 user["azure_tenant_id"],
#                 token_payload_many_groups["groups"],
#             )
#             users.append(added_user)

#     yield users


# @pytest.fixture(scope="function")
# async def current_test_user():
#     """Returns the current test user."""
#     yield CurrentUserData(**)


# TBD: refactor add_test_policies_for_resources from endpoint conftest file into this:
# also consider using the post functions for the actual creation of resources!
@pytest.fixture(scope="function")
async def add_test_access_policies():
    """Fixture for adding test policies."""

    async def _add_test_access_policies(access_policies: List[AccessPolicy]):
        """Adds test policies to the database."""

        policies = []
        async with AccessPolicyCRUD() as crud:
            mocked_admin_user = CurrentUserData(
                user_id=many_test_users[0]["azure_user_id"],
                roles=["Admin"],
            )
            for policy in access_policies:
                policy = await crud.create(AccessPolicy(**policy), mocked_admin_user)
                # session.add(policy)
                # await session.commit()
                # await session.refresh(policy)
                policies.append(policy)
            # await session.close()
        return policies

    yield _add_test_access_policies


@pytest.fixture(scope="function")
async def add_many_test_access_policies() -> list[AccessPolicyRead]:
    """Adds a category to the database."""
    mocked_admin_user = CurrentUserData(
        user_id=many_test_users[0]["azure_user_id"],
        roles=["Admin"],
    )
    async with AccessPolicyCRUD() as crud:
        policies = []
        for policy in many_test_policies:
            added_policy = await crud.create(AccessPolicy(**policy), mocked_admin_user)
            policies.append(added_policy)

    yield policies
