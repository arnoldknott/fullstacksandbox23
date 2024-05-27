import pytest
from uuid import UUID
from crud.access import AccessPolicyCRUD
from crud.category import CategoryCRUD
from crud.demo_resource import DemoResourceCRUD
from crud.protected_resource import (
    ProtectedResourceCRUD,
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
)
from core.types import CurrentUserData
from crud.public_resource import PublicResourceCRUD
from crud.tag import TagCRUD
from models.category import Category
from models.identity import User
from tests.utils import (
    many_test_categories,
    many_test_demo_resources,
    many_test_protected_resources,
    many_test_protected_child_resources,
    many_test_protected_grand_child_resources,
    many_test_public_resources,
    many_test_tags,
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
async def add_test_policy_for_resource(current_user_from_azure_token: User):
    """Adds a policy for a resource through CRUD to the database."""

    async def _add_test_policy_for_resource(policy, token_payload: dict = None):
        current_user = await current_user_from_azure_token(token_payload)
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
async def add_test_public_resources():
    """Adds public resources to the database."""
    public_resources_instances = []
    for public_resource in many_test_public_resources:
        async with PublicResourceCRUD() as crud:
            public_resource_instance = await crud.create(public_resource)
        public_resources_instances.append(public_resource_instance)

    yield public_resources_instances


@pytest.fixture(scope="function")
async def add_test_categories(
    current_user_from_azure_token: User,
):
    """Adds test categories through CRUD to the database."""

    # TBD: add checks if token payload is not provided!
    # could be a public resource then?
    # maybe just using the add_test_policies_for_resources fixture?
    # or just failing?
    async def _add_test_categories(token_payload: dict = None):
        category_instances = []
        current_user = await current_user_from_azure_token(token_payload)
        # TBD: refactor to use the post endpoint - the token should be mocked already here!
        for category in many_test_categories:
            async with CategoryCRUD() as crud:
                category_instance = await crud.create(category, current_user)
                # response = await async_client.post("/api/v1/category/", json=category)
                # category_instance = response.json()
                # print("=== category_instance ===")
                # print(category_instance)
            category_instances.append(category_instance)

        return category_instances

    yield _add_test_categories


@pytest.fixture(scope="function")
async def add_test_demo_resources(
    # get_async_test_session: AsyncSession,
    current_user_from_azure_token: User,
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
        current_user = await current_user_from_azure_token(token_payload)
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
    current_user_from_azure_token: User,
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
        current_user = await current_user_from_azure_token(token_payload)
        for tag in many_test_tags:
            async with TagCRUD() as crud:
                tag_instance = await crud.create_public(tag, current_user)
            tag_instances.append(tag_instance)

        return tag_instances

    yield _add_test_tags


@pytest.fixture(scope="function")
async def add_many_test_protected_resources(
    current_user_from_azure_token: User,
):
    """Adds test protected resources to the database."""

    async def _add_many_test_protected_resources(token_payload: dict = None):
        protected_resources = []
        for protected_resource in many_test_protected_resources:
            current_user = await current_user_from_azure_token(token_payload)
            async with ProtectedResourceCRUD() as crud:
                added_protected_resource = await crud.create(
                    protected_resource, current_user
                )
            protected_resources.append(added_protected_resource)

        return protected_resources

    yield _add_many_test_protected_resources


async def add_test_protected_child(
    current_user_from_azure_token: User,
    protected_child: dict,
    current_user: CurrentUserData = None,
    parent_id: UUID = None,
    inherit: bool = False,
):
    """Adds a test protected child to the database."""

    if not current_user:
        current_user = await current_user_from_azure_token()
    async with ProtectedChildCRUD() as crud:
        added_protected_child = await crud.create(
            protected_child, current_user, parent_id, inherit
        )

    return added_protected_child


@pytest.fixture(scope="function")
async def add_one_test_protected_child(
    current_user_from_azure_token: User,
):
    """Adds a test protected child to the database."""

    async def _add_one_test_protected_child(
        protected_child: dict,
        current_user: CurrentUserData = None,
        parent_id: UUID = None,
        inherit: bool = False,
    ):
        return await add_test_protected_child(
            current_user_from_azure_token,
            protected_child,
            current_user,
            parent_id,
            inherit,
        )

    yield _add_one_test_protected_child


# TBD: is this necessary at all?
@pytest.fixture(scope="function")
async def add_many_test_protected_children(
    current_user_from_azure_token: User,
):
    """Adds test protected children to the database."""

    async def _add_many_test_protected_children(token_payload: dict = None):
        protected_children = []
        for protected_child in many_test_protected_child_resources:
            current_user = await current_user_from_azure_token(token_payload)
            async with ProtectedChildCRUD() as crud:
                added_protected_child = await crud.create(protected_child, current_user)
            protected_children.append(added_protected_child)

        return protected_children

    yield _add_many_test_protected_children


# TBD: use the function for the endpoints ins the fixture here and create the family from those - top down
# Might need mocked data from multiple users / identities?
# @pytest.fixture(scope="function")
# async def add_protected_resource_family_with_access_policies():
#     """Adds a protected resource family with access policies to the database."""

#     async def _add_protected_resource_family_with_access_policies(
#         current_user_from_azure_token: User,
#         add_many_test_protected_resources,

#     ):
#         existing_test_protected_resources = await add_many_test_protected_resources()
