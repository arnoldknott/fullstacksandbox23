import pytest

from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from core.types import ResourceType, Action, IdentityType
from core.security import CurrentAccessToken
from models.access import AccessPolicy
from models.category import Category

# from models.demo_resource import DemoResource
from models.public_resource import PublicResource
from models.tag import Tag
from models.identity import User
from crud.protected_resource import ProtectedResourceCRUD
from crud.category import CategoryCRUD
from crud.access import AccessPolicyCRUD
from crud.demo_resource import DemoResourceCRUD
from crud.tag import TagCRUD
from models.protected_resource import ProtectedResource

from tests.utils import (
    many_test_categories,
    many_test_demo_resources,
    many_test_tags,
    many_test_protected_resources,
    many_test_public_resources,
)


# @pytest.fixture(scope="function")
# async def add_test_demo_resources(get_async_test_session: AsyncSession):
#     """Adds a demo resource to the database."""
#     session = get_async_test_session

#     demo_resource_instances = []
#     for resource in demo_resource_test_inputs:
#         demo_resource_instance = DemoResource(**resource)
#         session.add(demo_resource_instance)
#         await session.commit()
#         await session.refresh(demo_resource_instance)
#         demo_resource_instances.append(demo_resource_instance)

#     yield demo_resource_instances

# @pytest.fixture(scope="function")
# def admin_token():
#     """Returns a mock admin token."""
#     return generate_mock_token(is_admin=True)


# @pytest.fixture(scope="function")
# def valid_user_token():
#     """Returns a mock user token."""
#     return generate_mock_token(is_admin=False)


# @pytest.fixture(scope="function")
# def valid_user_token_with_one_group():
#     """Returns a mock user token."""
#     return generate_mock_token(is_admin=False, groups=[uuid4()])


# @pytest.fixture(scope="function")
# def valid_user_token_with_groups():
#     """Returns a mock user token."""
#     return generate_mock_token(is_admin=False, groups=[uuid4(), uuid4(), uuid4()])


# @pytest.fixture(scope="function")
# def expired_token():
#     """Returns a mock expired token."""
#     return generate_mock_token(expired=True)


@pytest.fixture(scope="function")
async def add_test_policy_for_resource(mock_current_user: User):
    """Adds a policy for a resource through CRUD to the database."""

    async def _add_test_policy_for_resource(policy, token_payload: dict = None):
        current_user = await mock_current_user(token_payload)
        async with AccessPolicyCRUD() as crud:
            added_policy = await crud.create(policy, current_user)

        return added_policy

    yield _add_test_policy_for_resource


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


@pytest.fixture(scope="function")
async def add_test_public_resources(get_async_test_session: AsyncSession):
    """Adds public resources to the database."""
    session = get_async_test_session
    public_resources_instances = []
    for public_resource in many_test_public_resources:
        public_resource_instance = PublicResource(**public_resource)
        session.add(public_resource_instance)
        await session.commit()
        await session.refresh(public_resource_instance)
        public_resources_instances.append(public_resource_instance)

    yield public_resources_instances


@pytest.fixture(scope="function")
async def add_test_categories(
    mock_current_user: User,
):  # get_async_test_session: AsyncSession):
    """Adds test categories through CRUD to the database."""
    # session = get_async_test_session

    # TBD: add checks if token payload is not provided!
    # could be a public resource then?
    # maybe just using the add_test_policies_for_resources fixture?
    # or just failing?
    async def _add_test_categories(token_payload: dict = None):
        category_instances = []
        current_user = await mock_current_user(token_payload)
        # print("=== _add_test_categories - mocked_token_payload ===")
        # print(mocked_token_payload)
        # TBD: refactor to use the post endpoint - the token should be mocked already here!
        for category in many_test_categories:
            # print("=== category ===")
            # print(category)
            # token = CurrentAccessToken(token_payload)
            # current_user = await token.provides_current_user()
            async with CategoryCRUD() as crud:
                category_instance = await crud.create(category, current_user)
            # response = await async_client.post("/api/v1/category/", json=category)
            # category_instance = response.json()
            # print("=== category_instance ===")
            # print(category_instance)
            category_instances.append(category_instance)
            # category_instance = Category(**category)
            # session.add(category_instance)
            # await session.commit()
            # await session.refresh(category_instance)
            # category_instances.append(category_instance)

        return category_instances

    yield _add_test_categories
    # print("=== add_test_categories - request.param ===")
    # print(request.param)
    # print("=== add_test_categories - request - all attributes ===")
    # for attr in dir(request):
    #     print(f"=== {attr} ==")
    #     print(getattr(request, attr))
    # for category in many_test_categories:
    #     category_instance = Category(**category)
    #     session.add(category_instance)
    #     await session.commit()
    #     await session.refresh(category_instance)
    #     category_instances.append(category_instance)

    # yield category_instances


@pytest.fixture(scope="function")
async def add_test_demo_resources(
    # get_async_test_session: AsyncSession,
    mock_current_user: User,
    add_test_categories: list[Category],
    # add_test_policies_for_resources: list[AccessPolicy],
):
    """Adds demo resources to the database."""
    # print("=== add_test_demo_resources started ===")
    # session = get_async_test_session
    # TBD, when refactoring add_test_demo_resources, the mocked token should be available here and
    # needs to be provided to to add_test_categories as well!

    async def _add_test_demo_resources(token_payload: dict = None):
        existing_test_categories = await add_test_categories(token_payload)
        # await add_test_policies_for_resources(
        #     resources=existing_test_categories,
        #     actions=["read"] * len(existing_test_categories),
        #     publics=[True] * len(existing_test_categories),
        # )
        # print("=== add_test_demo_resources after add_test_categories ===")
        many_test_demo_resources[0]["category_id"] = existing_test_categories[1].id
        many_test_demo_resources[1]["category_id"] = existing_test_categories[0].id
        many_test_demo_resources[2]["category_id"] = existing_test_categories[1].id

        demo_resource_instances = []
        current_user = await mock_current_user(token_payload)
        for resource in many_test_demo_resources:
            # print("=== resource ===")
            # print(resource)
            # if "category_id" in resource:
            #     category = await session.get(Category, resource["category_id"])
            #     resource["category"] = category
            #     del resource["category_id"]
            # demo_resource_instance = DemoResource(**resource)
            # session.add(demo_resource_instance)
            # await session.commit()
            # await session.refresh(demo_resource_instance)
            async with DemoResourceCRUD() as crud:
                # token = CurrentAccessToken(token_payload)
                # current_user = await token.provides_current_user()
                demo_resource_instance = await crud.create(resource, current_user)
            demo_resource_instances.append(demo_resource_instance)

        # yield demo_resource_instances
        # for demo_resource_instance in demo_resource_instances:
        #     print("=== add_test_demo_resources - demo_resource_instance ===")
        #     print(demo_resource_instance)
        return demo_resource_instances

    yield _add_test_demo_resources


@pytest.fixture(scope="function")
async def add_test_tags(
    mock_current_user: User,
):  # (get_async_test_session: AsyncSession):
    """Adds tags to the database."""
    # session = get_async_test_session
    # tag_instances = []
    # for tag in many_test_tags:
    #     tag_instance = Tag(**tag)
    #     session.add(tag_instance)
    #     await session.commit()
    #     await session.refresh(tag_instance)
    #     tag_instances.append(tag_instance)

    # yield tag_instances

    async def _add_test_tags(token_payload: dict = None):
        tag_instances = []
        current_user = await mock_current_user(token_payload)
        for tag in many_test_tags:
            async with TagCRUD() as crud:
                tag_instance = await crud.create_public(tag, current_user)
            tag_instances.append(tag_instance)

        return tag_instances

    yield _add_test_tags


@pytest.fixture(scope="function")
async def add_many_test_protected_resources(
    mocked_current_user: User,
):
    """Adds test protected resources to the database."""

    async def _add_many_test_protected_resources(token_payload: dict = None):
        protected_resources = []
        for protected_resource in many_test_protected_resources:
            current_user = await mocked_current_user(token_payload)
            async with ProtectedResourceCRUD() as crud:
                added_protected_resource = await crud.create(
                    protected_resource, current_user
                )
            protected_resources.append(added_protected_resource)

        return protected_resources

    yield _add_many_test_protected_resources

    # async with ProtectedResourceCRUD() as crud:
    #     protected_resources = []
    #     for protected_resource in many_test_protected_resources:
    #         added_protected_resource = await crud.create(protected_resource)
    #         protected_resources.append(added_protected_resource)

    # yield protected_resources
