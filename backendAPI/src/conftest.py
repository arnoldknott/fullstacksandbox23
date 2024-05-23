from typing import AsyncGenerator, Generator, List, Optional, Union
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import postgres_async_engine  # should be SQLite here only!
from core.security import CurrentAccessToken, Guards, get_azure_token_payload
from core.types import CurrentUserData, IdentityType, ResourceType
from crud.access import (
    AccessLoggingCRUD,
    AccessPolicyCRUD,
    IdentityHierarchyCRUD,
    ResourceHierarchyCRUD,
)
from crud.base import BaseCRUD
from crud.identity import UserCRUD
from main import app
from models.access import (
    AccessLogCreate,
    AccessLogRead,
    AccessPolicyCreate,
    AccessPolicyRead,
    IdentifierTypeLink,
)
from models.identity import Group, User, UserRead
from models.protected_resource import ProtectedResource
from tests.utils import (
    current_user_data_admin,
    identity_id_group2,
    many_current_users_data,
    many_entity_type_links,
    many_resource_ids,
    many_test_access_logs,
    many_test_azure_users,
    many_test_child_identities,
    many_test_child_resource_entities,
    many_test_policies,
    resource_id3,
    token_admin,
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
    app.dependency_overrides[
        get_azure_token_payload
    ] = lambda: mocked_get_azure_token_payload
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


async def register_entity_to_identity_type_link_table(
    entity_id: UUID, model: Union["ResourceType", "IdentityType"] = ProtectedResource
):
    """Registers an identity to the identifier link table."""
    async with BaseCRUD(model) as crud:
        statement = crud._add_identifier_type_link_to_session(entity_id)
        await crud.session.exec(statement)
        await crud.session.commit()

    return


# @pytest.fixture(scope="function")
# async def register_many_entities():
#     """Registers many entities (resources and identities) with id and their type in the database."""

#     print("=== register_many_entities - many_entity_type_links ===")
#     pprint(many_entity_type_links)

#     for entity_id, entity_type in many_entity_type_links:
#         await register_entity_to_identity_type_link_table(UUID(entity_id), entity_type)

#     yield many_entity_type_links


# mocks the current user and registers in identity link table
@pytest.fixture(scope="function")
async def register_current_user():
    """Returns a mock current user and registers in identity link table."""

    async def _register_current_user(current_user_data: dict = None) -> CurrentUserData:
        current_user_data = CurrentUserData(**current_user_data)
        await register_entity_to_identity_type_link_table(
            current_user_data.user_id, User
        )
        return current_user_data

    yield _register_current_user


# mocks the many current user and registers in identity link table
@pytest.fixture(scope="function")
async def register_many_current_users():
    """Returns a mock current user and registers in identity link table."""

    current_users = []
    for current_user_data in many_current_users_data:
        current_user_data = CurrentUserData(**current_user_data)
        await register_entity_to_identity_type_link_table(
            current_user_data.user_id, User
        )
        current_users.append(current_user_data)

    yield current_users


# TBD: turn input into dict? But what about the model?
@pytest.fixture(scope="function")
async def register_one_resource():
    """Registers a resource id and its type in the database."""

    async def _register_one_resource(
        resource_id: UUID, model: ResourceType = ProtectedResource
    ):
        """Registers a resource id and its type in the database."""
        await register_entity_to_identity_type_link_table(resource_id, model)
        return resource_id

    yield _register_one_resource


@pytest.fixture(scope="function")
async def register_many_resources():
    """Registers many protected resources with id and its type in the database."""

    for resource_id in many_resource_ids:
        await register_entity_to_identity_type_link_table(
            UUID(resource_id), ProtectedResource
        )

    yield many_resource_ids


# TBD: turn input into dict?
@pytest.fixture(scope="function")
async def register_one_identity():
    """Registers a resource id and its type in the database."""

    async def _register_one_identity(identity_id: UUID, model: IdentityType = Group):
        """Registers a resource id and its type in the database."""
        await register_entity_to_identity_type_link_table(identity_id, model)
        return identity_id

    yield _register_one_identity


# @pytest.fixture(scope="function")
# async def register_many_identities():
#     """Registers many protected resources with id and its type in the database."""

#     many_registered_identity_ids = []
#     for identity in many_identity_ids:
#         await register_entity_to_identity_type_link_table(
#             UUID(identity["id"]), IdentityType.get_model(identity["type"])
#         )
#         many_registered_identity_ids.append(UUID(identity["id"]))

#     yield many_registered_identity_ids


@pytest.fixture(scope="function")
async def register_many_entities(get_async_test_session: AsyncSession):
    """Registers many protected resources with id and its type in the database."""

    session = get_async_test_session

    identity_type_links = []
    for entity in many_entity_type_links:
        entity_instance = IdentifierTypeLink(**entity)
        session.add(entity_instance)
        await session.commit()
        await session.refresh(entity_instance)
        identity_type_links.append(entity_instance)

    yield identity_type_links


# def get_model(resource_type: ResourceType) -> Type[SQLModel]:
#     """Returns the model based on the model enum."""
#     return models[model_enum.value]


# for entity in many_entity_type_links:
#     await register_entity_to_identity_type_link_table(
#         UUID(entity["id"]), entity["type"]
#     )

# yield many_entity_type_links


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
async def add_one_test_access_policy():
    """Fixture for adding test policies."""

    async def _add_one_test_access_policy(
        policy: dict, current_user: CurrentUserData = None
    ):
        """Adds test policies to the database."""

        async with AccessPolicyCRUD() as crud:
            if current_user is None:
                current_user = CurrentUserData(**current_user_data_admin)
            await register_entity_to_identity_type_link_table(
                UUID(policy["resource_id"]), ProtectedResource
            )
            policy = await crud.create(AccessPolicyCreate(**policy), current_user)
            return policy

    yield _add_one_test_access_policy


@pytest.fixture(scope="function")
async def add_many_test_access_policies(
    register_many_current_users,
    register_many_resources,
) -> list[AccessPolicyRead]:
    """Adds a category to the database."""
    mocked_admin_user = CurrentUserData(**current_user_data_admin)
    async with AccessPolicyCRUD() as crud:
        policies = []
        for policy in many_test_policies:
            added_policy = await crud.create(
                AccessPolicyCreate(**policy), mocked_admin_user
            )
            policies.append(added_policy)

    yield policies


async def add_test_access_log(access_log: dict) -> AccessLogRead:
    """Adds a test access log to the database."""
    async with AccessLoggingCRUD() as crud:
        access_log_instance = AccessLogCreate(**access_log)
        created_access_log = await crud.create(access_log_instance)
        return created_access_log


@pytest.fixture(scope="function")
async def add_one_test_access_log():
    """Adds a test access log to the database."""

    async def _add_one_test_access_log(access_log: dict) -> AccessLogRead:
        access_log_instance = await add_test_access_log(access_log)
        return access_log_instance

    yield _add_one_test_access_log


@pytest.fixture(scope="function")
async def add_many_test_access_logs(
    register_many_current_users,
    register_many_resources,
) -> list[AccessLogRead]:
    """Adds many test access logs to the database."""

    access_logs = []
    for access_log in many_test_access_logs:
        access_log_instance = await add_test_access_log(access_log)
        access_logs.append(access_log_instance)

    yield access_logs


async def add_parent_child_resource_relationship(
    parent_id: UUID,
    child_id: UUID,
    child_type: ResourceType = ResourceType.protected_child,
):
    """Adds a parent-child relationship to the resource hierarchy table."""
    await register_entity_to_identity_type_link_table(
        child_id
    )  # TBD: pass the model here - or refactor register_entity_to_identity_type_link_table() to use type
    async with ResourceHierarchyCRUD() as crud:
        created_relationship = await crud.create(
            current_user=CurrentUserData(**current_user_data_admin),
            parent_id=parent_id,
            child_type=child_type,
            child_id=child_id,
        )
    return created_relationship


@pytest.fixture(scope="function")
async def add_one_parent_child_resource_relationship(
    register_many_resources: list[UUID],
):
    """Adds a parent-child resource relationship to the database."""

    registered_resources = register_many_resources

    async def _add_one_parent_child_resource_relationship(
        child_id: UUID,
        parent_id: UUID = registered_resources[0],
        type: ResourceType = ResourceType.protected_child,
    ):
        """Adds a parent-child relationship to the database."""
        return await add_parent_child_resource_relationship(parent_id, child_id, type)

    yield _add_one_parent_child_resource_relationship


@pytest.fixture(scope="function")
async def add_many_parent_child_resource_relationships(
    register_many_resources: list[UUID],
):
    """Adds many parent-child relationships to the resource hierarchy table."""

    parent_id = resource_id3
    relationships = []
    for child in many_test_child_resource_entities:
        relationship = await add_parent_child_resource_relationship(
            parent_id, UUID(child["id"]), child["type"]
        )
        relationships.append(relationship)
    yield relationships


async def add_parent_child_identity_relationship(
    parent_id: UUID,
    child_id: UUID,
    child_type: IdentityType = IdentityType.sub_group,
):
    """Adds a parent-child relationship to the identity hierarchy table."""
    await register_entity_to_identity_type_link_table(
        child_id, IdentityType.get_model(child_type)
    )

    async with IdentityHierarchyCRUD() as crud:
        created_relationship = await crud.create(
            current_user=CurrentUserData(**current_user_data_admin),
            parent_id=parent_id,
            child_type=child_type,
            child_id=child_id,
        )
    return created_relationship


@pytest.fixture(scope="function")
async def add_one_parent_child_identity_relationship(
    register_many_entities: list[{UUID, str}],
):
    """Adds a parent-child identity relationship to the database."""

    registered_identities = register_many_entities[10:]
    parent_id = registered_identities[1].id

    async def _add_one_parent_child_identity_relationship(
        child_id: UUID,
        parent_id: UUID = parent_id,
        type: IdentityType = IdentityType.sub_group,
    ):
        """Adds a parent-child relationship to the database."""
        return await add_parent_child_identity_relationship(parent_id, child_id, type)

    yield _add_one_parent_child_identity_relationship


@pytest.fixture(scope="function")
async def add_many_parent_child_identity_relationships(
    register_many_entities: list[{UUID, str}],
):
    """Adds many parent-child relationships to the identity hierarchy table."""

    parent_id = identity_id_group2
    relationships = []
    children_for_group = [
        many_test_child_identities[0],
        many_test_child_identities[3],
        many_test_child_identities[4],
        many_test_child_identities[8],
    ]
    for child in children_for_group:
        relationship = await add_parent_child_identity_relationship(
            parent_id, UUID(child["id"]), child["type"]
        )
        relationships.append(relationship)
    # TBD: add more hierarchy levels!
    yield relationships
