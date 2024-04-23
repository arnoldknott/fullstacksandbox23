from typing import AsyncGenerator, Generator, List, Optional

from uuid import UUID
import pytest
from core.databases import postgres_async_engine  # should be SQLite here only!
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from pprint import pprint
from core.security import get_azure_token_payload, CurrentAccessToken, Guards
from core.types import CurrentUserData, ResourceType
from models.identity import User, UserRead
from models.protected_resource import ProtectedResource
from crud.identity import UserCRUD
from crud.base import BaseCRUD
from models.access import (
    AccessPolicyCreate,
    AccessPolicy,
    AccessPolicyRead,
    IdentityTypeLink,
)
from crud.access import AccessPolicyCRUD
from tests.utils import (
    many_test_azure_users,
    current_user_data_admin,
    many_current_users_data,
    many_resource_ids,
    token_admin,
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
    # print("=== conftest - mocked_get_azure_token_payload - request ===")
    # pprint(request.param)
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


@pytest.fixture(scope="function")
def mock_guards():
    """Mocks the guards for the routes."""

    def _mock_guards(
        scopes: Optional[list[str]] = [],
        roles: Optional[list[str]] = [],
        groups: Optional[list[str]] = [],
    ):
        return Guards(scopes=scopes, roles=roles, groups=groups)

    yield _mock_guards


# @pytest.fixture(scope="function")
# async def add_one_test_user(get_async_test_session: AsyncSession) -> User:
#     """Adds a test user to the database."""
#     session = get_async_test_session
#     user = User(**many_test_azure_users[0])
#     session.add(user)
#     await session.commit()
#     await session.refresh(user)

#     yield user


# @pytest.fixture(scope="function")
# async def add_one_test_user_with_groups(get_async_test_session: AsyncSession) -> User:
#     """Adds a tst user with group membership to the database."""
#     async with UserCRUD() as crud:
#         user = await crud.create_azure_user_and_groups_if_not_exist(
#             many_test_azure_users[0]["azure_user_id"],
#             many_test_azure_users[0]["azure_tenant_id"],
#             token_payload_many_groups["groups"],
#         )

#     yield user


# Converts from the identity provider (azure) to current_user in application and adds user to database
@pytest.fixture(scope="function")
async def current_user_from_azure_token():
    """Returns a mock current user based on provided payload and adds to user database."""

    async def _current_user_from_azure_token(
        token_payload: dict = None,
    ) -> CurrentUserData:
        current_user = None
        if token_payload is None:
            token_payload = token_admin
        token = CurrentAccessToken(token_payload)
        current_user = await token.provides_current_user()
        return current_user

    yield _current_user_from_azure_token


async def register_current_users_to_identity_link_table(
    current_users_data: List[CurrentUserData],
):
    """Registers the current user to the identity link table."""
    async with UserCRUD() as crud:
        for current_user_data in current_users_data:
            crud._add_identity_type_link_to_session(current_user_data.user_id)
        await crud.session.commit()

    return


# mocks the current user and registers in identity link table
@pytest.fixture(scope="function")
async def register_current_user():
    """Returns a mock current user and registers in identity link table."""

    async def _register_current_user(current_user_data: dict = None) -> CurrentUserData:

        current_user_data = CurrentUserData(**current_user_data)
        await register_current_users_to_identity_link_table([current_user_data])
        # async with UserCRUD() as crud:
        #     crud._add_identity_type_link_to_session(current_user_data.user_id)
        #     await crud.session.commit()
        #     # identity_link = await crud.session.get(
        #     #     IdentityTypeLink, current_user_data.user_id
        #     # )
        #     # print("=== conftest - register_current_user - identity_link ===")
        #     # pprint(identity_link)
        return current_user_data

    yield _register_current_user


# # mocks the admin user and registers in identity link table
# @pytest.fixture(scope="function")
# async def register_current_admin_user():
#     """Returns the mocked admin current user and registers in identity link table."""

#     current_user_data = CurrentUserData(**current_user_data_admin)
#     register_current_users_to_identity_link_table([current_user_data])
#     # async with UserCRUD() as crud:
#     #     crud._add_identity_type_link_to_session(current_user_data.user_id)
#     #     await crud.session.commit()
#     #     # identity_link = await crud.session.get(
#     #     #     IdentityTypeLink, current_user_data.user_id
#     #     # )
#     #     # print("=== conftest - register_current_admin_user - identity_link ===")
#     #     # pprint(identity_link)
#     #     # await crud.session.refresh()
#     #     yield current_user_data


# mocks the current user and registers in identity link table
@pytest.fixture(scope="function")
async def register_many_current_users():
    """Returns a mock current user and registers in identity link table."""

    # print("=== conftest - register_many_current_users - many_current_users_data ===")
    # pprint(many_current_users_data)

    current_users = []
    for current_user_data in many_current_users_data:
        current_user_data = CurrentUserData(**current_user_data)
        await register_current_users_to_identity_link_table([current_user_data])
        current_users.append(current_user_data)

    # print("=== conftest - register_many_current_users - current_users ===")
    # pprint(current_users)

    yield current_users

    # async def _register_many_current_users(
    #     current_user_data: dict = None,
    # ) -> CurrentUserData:

    #     current_user_data = CurrentUserData(**current_user_data)
    #     async with UserCRUD() as crud:
    #         crud._add_identity_type_link_to_session(current_user_data.user_id)
    #         await crud.session.commit()
    #         # identity_link = await crud.session.get(
    #         #     IdentityTypeLink, current_user_data.user_id
    #         # )
    #         # print("=== conftest - register_current_user - identity_link ===")
    #         # pprint(identity_link)
    #     return current_user_data

    # yield _register_many_current_users


async def register_resource_to_resource_link_table(
    resource_id: UUID, model: ResourceType = ProtectedResource
):
    """Registers the resources to the resource link table."""
    async with BaseCRUD(model) as crud:
        statement = crud._add_resource_type_link_to_session(resource_id)
        await crud.session.exec(statement)
        await crud.session.commit()

    return


@pytest.fixture(scope="function")
async def register_one_resource():
    """Registers a resource id and its type in the database."""

    async def _register_one_resource(
        resource_id: UUID, model: ResourceType = ProtectedResource
    ):
        """Registers a resource id and its type in the database."""
        print("=== conftest - register_one_resource - type(resource_id) ===")
        print(type(resource_id))
        await register_resource_to_resource_link_table(resource_id, model)
        return resource_id

        # async with BaseCRUD(model) as crud:
        #     crud._add_resource_type_link_to_session(resource_id)
        #     await crud.session.commit()
        #     # resource_link = await crud.session.get(
        #     #     IdentityTypeLink, resource_id
        #     # )
        #     # print("=== conftest - register_one_resource - resource_link ===")
        #     # pprint(resource_link)
        # return resource_id

    yield _register_one_resource


@pytest.fixture(scope="function")
async def register_many_protected_resources():
    """Registers many resources with id and its type in the database."""

    for resource_id in many_resource_ids:
        await register_resource_to_resource_link_table(resource_id, ProtectedResource)

    yield many_resource_ids

    # async def _register_many_resources(model: ResourceType = ProtectedResource):
    #     for resource_id in many_resource_ids:
    #         await register_resource_to_resource_link_table(resource_id, model)
    #     # for resource in resource_id:
    #     #     await register_resource_to_resource_link_table(resource, model)
    #     print("=== conftest - register_many_resources - resource_id ===")
    #     pprint(resource_id)
    #     return resource_id

    #     # async with BaseCRUD(model) as crud:

    #     #     crud._add_resource_type_link_to_session(resource_id)
    #     #     await crud.session.commit()
    #     #     # resource_link = await crud.session.get(
    #     #     #     IdentityTypeLink, resource_id
    #     #     # )
    #     #     # print("=== conftest - register_one_resource - resource_link ===")
    #     #     # pprint(resource_link)
    #     # return resource_id

    # yield _register_many_resources


# Adds a test user based on identity provider token payload to database and returns the user
@pytest.fixture(scope="function")
# async def add_one_azure_test_user(current_user_from_azure_token: User):
async def add_one_azure_test_user(current_user_from_azure_token: User):
    """Adds many test users to the database."""

    # async def _add_one_azure_test_user(
    #     user_number: int = None, token_payload: dict = None
    # ) -> UserRead:
    async def _add_one_azure_test_user(user_number: int = None) -> UserRead:
        # current_user = await current_user_from_azure_token(token_payload)
        async with UserCRUD() as crud:
            user = await crud.create_azure_user_and_groups_if_not_exist(
                **many_test_azure_users[user_number]
            )
        return user

    yield _add_one_azure_test_user


# Adds many test users based on identity provider token payloads to database and returns the users
@pytest.fixture(scope="function")
async def add_many_azure_test_users():
    """Adds many test users to the database."""

    async def _add_many_azure_test_users() -> List[UserRead]:
        users = []
        for user in many_test_azure_users:
            async with UserCRUD() as crud:
                user = await crud.create_azure_user_and_groups_if_not_exist(**user)
            users.append(user)
        return users

    yield _add_many_azure_test_users


# @pytest.fixture(scope="function")
# async def add_test_tags(
#     mock_current_user: User,
# ):  # (get_async_test_session: AsyncSession):
#     """Adds tags to the database."""
#     # session = get_async_test_session
#     # tag_instances = []
#     # for tag in many_test_tags:
#     #     tag_instance = Tag(**tag)
#     #     session.add(tag_instance)
#     #     await session.commit()
#     #     await session.refresh(tag_instance)
#     #     tag_instances.append(tag_instance)

#     # yield tag_instances

#     async def _add_test_tags(token_payload: dict = None):
#         tag_instances = []
#         for tag in many_test_tags:
#             current_user = await mock_current_user(token_payload)
#             async with TagCRUD() as crud:
#                 tag_instance = await crud.create_public(tag, current_user)
#             tag_instances.append(tag_instance)

#         return tag_instances

#     yield _add_test_tags

# @pytest.fixture(scope="function")
# async def add_many_test_azure_users(get_async_test_session: AsyncSession):
#     """Adds test users to the database."""
#     session = get_async_test_session
#     users = []
#     for user in many_test_azure_users:
#         this_user = User(**user)
#         session.add(this_user)
#         await session.commit()
#         await session.refresh(this_user)
#         users.append(this_user)

#     yield users


# @pytest.fixture(scope="function")
# async def add_many_test_azure_users_with_groups() -> list[User]:
#     """Adds many test users with group membership to the database."""
#     async with UserCRUD() as crud:
#         users = []
#         for user in many_test_azure_users:
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
async def add_test_access_policy():
    """Fixture for adding test policies."""

    async def _add_test_access_policy(
        policy: dict, current_user: CurrentUserData = None
    ):
        """Adds test policies to the database."""

        # policies = []
        async with AccessPolicyCRUD() as crud:
            if current_user is None:
                current_user = CurrentUserData(**current_user_data_admin)
            # for policy in access_policies:
            print("=== conftest - add_test_access_policy - policy ===")
            pprint(policy)
            await register_resource_to_resource_link_table(
                policy["resource_id"], ProtectedResource
            )
            policy = await crud.create(AccessPolicyCreate(**policy), current_user)
            # session.add(policy)
            # await session.commit()
            # await session.refresh(policy)
            # policies.append(policy)
            # await session.close()
            # return policies
            return policy

    yield _add_test_access_policy


@pytest.fixture(scope="function")
async def add_many_test_access_policies(
    register_many_current_users,
    register_many_protected_resources,
) -> list[AccessPolicyRead]:
    """Adds a category to the database."""
    mocked_admin_user = CurrentUserData(**current_user_data_admin)
    async with AccessPolicyCRUD() as crud:
        policies = []
        for policy in many_test_policies:
            added_policy = await crud.create(
                AccessPolicyCreate(**policy), mocked_admin_user
            )
            # print("=== conftest - add_many_test_access_policies - added_policy ===")
            # pprint(added_policy)
            policies.append(added_policy)

    yield policies
