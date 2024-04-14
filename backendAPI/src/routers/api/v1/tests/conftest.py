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
    token_admin,
    many_test_categories,
    many_test_demo_resources,
    many_test_tags,
    many_test_users,
    many_test_protected_resources,
    many_test_public_resources,
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


# def create_access_policy(resource, identity, action, public) -> AccessPolicyCreate:
#     """Create an access policy."""
#     resource_id = resource["id"]
#     ResourceType(resource.__class__.__name__)
#     resource_type = resource.__class__.__name__
#     return AccessPolicyCreate()


@pytest.fixture(scope="function")
async def mock_current_user():
    """Returns a mock current user based on provided payload or admin."""

    async def _mock_current_user(token_payload: dict = None) -> User:
        current_user = None
        if token_payload is None:
            token_payload = token_admin
        token = CurrentAccessToken(token_payload)
        current_user = await token.provides_current_user()
        return current_user

    yield _mock_current_user


@pytest.fixture(scope="function")
async def add_test_policies_for_resources(get_async_test_session: AsyncSession):
    """Fixture for adding test policies for specific resources to the database."""
    session = get_async_test_session

    async def _add_test_policies_for_resources(
        resources: list[dict],
        actions: list[str],
        identities: Optional[list[dict]] = None,
        publics: Optional[list[bool]] = None,
    ):
        """Adds test policies to the database."""

        # Unnecessary, as the validation is done in the create model!
        if identities is None:
            if publics is None:
                raise Exception(
                    "Either identities or public must be provided for the policies!"
                )
            else:
                identities = [None] * len(resources)
        # async def _add_test_policies_for_resources(resources: list[dict]):
        #     """Adds test policies to the database."""

        # TBD: use a mapping for this?

        # Public vs. identity is taken care of in the create model validation through pydantic!
        # if public is not None:
        #     if len(resources) == len(identities) == len(actions) == len(public):
        #         pass
        #     else:
        #         raise Exception(
        #             "The number of resources, identities, actions and public must be the same!"
        #         )
        # else:
        #     if len(resources) == len(identities) == len(actions):
        #         pass
        #     else:
        #         raise Exception(
        #             "The number of resources, identities and actions must be the same!"
        #         )

        # print("=== add_test_policies - request ===")
        # print(resources)
        # TBD: create the policies based on the incoming resources, identity, action and overrides!
        created_policies = []
        # for resource, idx in resources:
        for resource, identity, action, public in zip(
            resources, identities, actions, publics
        ):
            # print("=== add_test_policies - policy ===")
            # print(policy)
            # TBD: add the CRUD here and write to AccessPolicy table!
            # policy = create_access_policy(
            #     resource, identities[idx], actions[idx], public[idx]
            # )
            # created_policies.append(AccessPolicy(**policy))
            resource_id = resource.id
            if resource.__class__.__name__ in ResourceType.list():
                resource_type = ResourceType(resource.__class__.__name__)
            elif resource.__class__.__name__ in IdentityType.list():
                resource_type = IdentityType(resource.__class__.__name__)
            else:
                raise ValueError(
                    f"{resource.__name__} is not a valid ResourceType or IdentityType"
                )
            # resource_type = ResourceType(resource.__class__.__name__)
            if identity is not None:
                identity_id = identity.id
                identity_type = IdentityType(identity.__class__.__name__)
            else:
                identity_id = None
                identity_type = None
            action = Action(action)
            public = public if public is not None else False
            access_policy_instance = AccessPolicy(
                resource_id=resource_id,
                resource_type=resource_type,
                identity_id=identity_id,
                identity_type=identity_type,
                action=action,
                public=public,
            )
            session.add(access_policy_instance)
            await session.commit()
            await session.refresh(access_policy_instance)
            created_policies.append(access_policy_instance)

        # print("=== created_policies ===")
        # print(created_policies)
        return created_policies

    yield _add_test_policies_for_resources

    # print("=== add_test_policies - request ===")
    # print(request)
    # created_policies = []
    # for policy in request:
    #     print("=== add_test_policies - policy ===")
    #     print(policy)
    #     created_policies.append(AccessPolicy(**policy))

    # yield created_policies

    # session = get_async_test_session

    # policy_instances = []
    # for policy in many_test_policies:
    #     policy_instance = AccessPolicy(**policy)
    #     session.add(policy_instance)
    #     await session.commit()
    #     await session.refresh(policy_instance)
    #     policy_instances.append(policy_instance)

    # yield policy_instances


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
        # print("=== _add_test_categories - mocked_token_payload ===")
        # print(mocked_token_payload)
        # TBD: refactor to use the post endpoint - the token should be mocked already here!
        for category in many_test_categories:
            # print("=== category ===")
            # print(category)
            # token = CurrentAccessToken(token_payload)
            # current_user = await token.provides_current_user()
            current_user = await mock_current_user(token_payload)
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
                current_user = await mock_current_user(token_payload)
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
        for tag in many_test_tags:
            current_user = await mock_current_user(token_payload)
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
