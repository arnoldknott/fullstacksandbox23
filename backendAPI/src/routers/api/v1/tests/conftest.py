import pytest
from models.category import Category
from models.demo_resource import DemoResource
from models.tag import Tag
from models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from tests.utils import (
    many_test_categories,
    many_test_demo_resources,
    many_test_tags,
    many_test_users,
)

# def generate_mock_token(
#     is_admin: bool = False,
#     expired: bool = False,
#     groups: Optional[List[str]] = None,
# ) -> str:
#     """Generate a mock JWT token for testing."""

#     # Set the issued at time (iat) to the current time
#     iat = time.time()

#     # Set the not before time (nbf) to the current time
#     nbf = iat

#     # If the token should be expired, set the expiration time (exp) to a time in the past
#     # Otherwise, set it to a time in the future
#     exp = iat - 100 if expired else iat + 3600

#     # Set the roles based on the is_admin flag
#     roles = ["Admin"] if is_admin else ["User"]

#     # Set the groups
#     groups = groups or []

#     # Create the payload
#     payload = {
#         "iat": iat,
#         "nbf": nbf,
#         "exp": exp,
#         "roles": roles,
#         "groups": groups,
#     }

#     # Encode the payload into a JWT token
#     token = jwt.encode(
#         payload, "needs to be a PEM file", algorithm="RS256", headers={"kid": "mykidstring"}
#     )

#     return token


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
async def add_many_test_users(get_async_test_session: AsyncSession):
    """Adds a category to the database."""
    session = get_async_test_session
    users = []
    for user in many_test_users:
        this_user = User(**user)
        session.add(this_user)
        await session.commit()
        await session.refresh(this_user)
        users.append(this_user)

    yield users


@pytest.fixture(scope="function")
async def add_test_categories(get_async_test_session: AsyncSession):
    """Adds a category to the database."""
    session = get_async_test_session
    category_instances = []
    for category in many_test_categories:
        category_instance = Category(**category)
        session.add(category_instance)
        await session.commit()
        await session.refresh(category_instance)
        category_instances.append(category_instance)

    yield category_instances


@pytest.fixture(scope="function")
async def add_test_demo_resources(
    get_async_test_session: AsyncSession,
    add_test_categories: list[Category],
):
    """Adds a demo resource to the database."""
    # print("=== add_test_demo_resources started ===")
    session = get_async_test_session
    add_test_categories
    # print("=== add_test_demo_resources after add_test_categories ===")

    demo_resource_instances = []
    for resource in many_test_demo_resources:
        # print("=== resource ===")
        # print(resource)
        # if "category_id" in resource:
        #     category = await session.get(Category, resource["category_id"])
        #     resource["category"] = category
        #     del resource["category_id"]
        demo_resource_instance = DemoResource(**resource)
        session.add(demo_resource_instance)
        await session.commit()
        await session.refresh(demo_resource_instance)
        demo_resource_instances.append(demo_resource_instance)

    yield demo_resource_instances


@pytest.fixture(scope="function")
async def add_test_tags(get_async_test_session: AsyncSession):
    """Adds a tags to the database."""
    session = get_async_test_session
    tag_instances = []
    for tag in many_test_tags:
        tag_instance = Tag(**tag)
        session.add(tag_instance)
        await session.commit()
        await session.refresh(tag_instance)
        tag_instances.append(tag_instance)

    yield tag_instances
