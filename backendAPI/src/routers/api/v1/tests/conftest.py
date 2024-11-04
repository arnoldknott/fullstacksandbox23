from os import path, remove
from uuid import UUID

import pytest
from fastapi import UploadFile

from core.types import CurrentUserData
from crud.access import AccessPolicyCRUD
from crud.category import CategoryCRUD
from crud.demo_file import DemoFileCRUD
from crud.demo_resource import DemoResourceCRUD
from crud.protected_resource import (
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
    ProtectedResourceCRUD,
)
from crud.public_resource import PublicResourceCRUD
from crud.tag import TagCRUD
from models.category import Category
from models.identity import User
from tests.utils import (
    many_test_categories,
    many_test_demo_resources,
    many_test_protected_child_resources,
    many_test_protected_grandchild_resources,
    many_test_protected_resources,
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
        categories = []
        current_user = await current_user_from_azure_token(token_payload)
        # TBD: refactor to use the post endpoint - the token should be mocked already here!
        for category in many_test_categories:
            async with CategoryCRUD() as crud:
                category_instance = await crud.create(category, current_user)
            categories.append(category_instance)

        categories = sorted(categories, key=lambda x: x.id)

        return categories

    yield _add_test_categories


@pytest.fixture(scope="function")
async def add_test_demo_resources(
    current_user_from_azure_token: User,
    add_test_categories: list[Category],
    # add_test_policies_for_resources: list[AccessPolicy],
):
    """Adds demo resources to the database."""
    # TBD, when refactoring add_test_demo_resources, the mocked token should be available here and
    # needs to be provided to to add_test_categories as well!

    async def _add_test_demo_resources(token_payload: dict = None):
        existing_test_categories = await add_test_categories(token_payload)
        many_test_demo_resources[0]["category_id"] = existing_test_categories[1].id
        many_test_demo_resources[1]["category_id"] = existing_test_categories[0].id
        many_test_demo_resources[2]["category_id"] = existing_test_categories[1].id

        demo_resources = []
        current_user = await current_user_from_azure_token(token_payload)
        for resource in many_test_demo_resources:
            async with DemoResourceCRUD() as crud:
                demo_resource_instance = await crud.create(resource, current_user)
            demo_resources.append(demo_resource_instance)

        demo_resources = sorted(demo_resources, key=lambda x: x.id)

        return demo_resources

    yield _add_test_demo_resources


@pytest.fixture(scope="function")
async def add_many_test_demo_files(
    current_user_from_azure_token: User,
):
    """Adds test demo files to the database and the appdata on disk."""

    demo_file_names = ["demo_file_01.txt", "demo_file_02.txt"]
    test_demo_files = []
    for demo_file_name in demo_file_names:
        test_demo_files.append(
            UploadFile(
                filename=demo_file_name,
                file=open(f"src/tests/{demo_file_name}", "rb"),
            )
        )

    async def _add_many_test_demo_files(token_payload: dict = None):
        demo_files_metadata = []
        for demo_file in test_demo_files:
            current_user = await current_user_from_azure_token(token_payload)
            async with DemoFileCRUD() as crud:
                added_demo_file = await crud.create_file(demo_file, current_user)
            demo_files_metadata.append(added_demo_file)

        demo_files_metadata = sorted(demo_files_metadata, key=lambda x: x.id)

        return demo_files_metadata

    yield _add_many_test_demo_files

    # Remove demo files from disk after the test:
    appdata_path = "/data/appdata/demo_files"
    for demo_file_name in demo_file_names:
        if path.exists(f"{appdata_path}/{demo_file_name}"):
            remove(f"{appdata_path}/{demo_file_name}")


@pytest.fixture(scope="function")
async def add_test_tags(
    current_user_from_azure_token: User,
):  # (get_async_test_session: AsyncSession):
    """Adds tags to the database."""

    async def _add_test_tags(token_payload: dict = None):
        tags = []
        current_user = await current_user_from_azure_token(token_payload)
        for tag in many_test_tags:
            async with TagCRUD() as crud:
                tag_instance = await crud.create_public(tag, current_user)
            tags.append(tag_instance)

        tags = sorted(tags, key=lambda x: x.id)

        return tags

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

        protected_resources = sorted(protected_resources, key=lambda x: x.id)

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

        protected_children = sorted(protected_children, key=lambda x: x.id)

        return protected_children

    yield _add_many_test_protected_children


async def add_test_protected_grandchild(
    current_user_from_azure_token: User,
    protected_grandchild: dict,
    current_user: CurrentUserData = None,
    parent_id: UUID = None,
    inherit: bool = False,
):
    """Adds a test protected grandchild to the database."""

    if not current_user:
        current_user = await current_user_from_azure_token()
    async with ProtectedChildCRUD() as crud:
        added_protected_grandchild = await crud.create(
            protected_grandchild, current_user, parent_id, inherit
        )

    return added_protected_grandchild


@pytest.fixture(scope="function")
async def add_one_test_protected_grandchild(
    current_user_from_azure_token: User,
):
    """Adds a test protected grandchild to the database."""

    async def _add_one_test_protected_grandchild(
        protected_grandchild: dict,
        current_user: CurrentUserData = None,
        parent_id: UUID = None,
        inherit: bool = False,
    ):
        return await add_test_protected_grandchild(
            current_user_from_azure_token,
            protected_grandchild,
            current_user,
            parent_id,
            inherit,
        )

    yield _add_one_test_protected_grandchild


@pytest.fixture(scope="function")
async def add_many_test_protected_grandchildren(
    current_user_from_azure_token: User,
):
    """Adds test protected grandchildren to the database."""

    async def _add_many_test_protected_grandchildren(token_payload: dict = None):
        protected_grandchildren = []
        for protected_grandchild in many_test_protected_grandchild_resources:
            current_user = await current_user_from_azure_token(token_payload)
            async with ProtectedGrandChildCRUD() as crud:
                added_protected_grandchild = await crud.create(
                    protected_grandchild, current_user
                )
            protected_grandchildren.append(added_protected_grandchild)

        protected_grandchildren = sorted(protected_grandchildren, key=lambda x: x.id)

        return protected_grandchildren

    yield _add_many_test_protected_grandchildren
