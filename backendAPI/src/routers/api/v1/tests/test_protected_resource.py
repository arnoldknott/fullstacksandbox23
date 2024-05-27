from datetime import datetime, timedelta
from uuid import UUID
from pprint import pprint
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.types import Action, CurrentUserData
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD, ResourceHierarchyCRUD
from crud.protected_resource import (
    ProtectedResourceCRUD,
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
)
from models.protected_resource import (
    ProtectedResource,
    ProtectedChild,
    ProtectedGrandChild,
)
from tests.utils import (
    current_user_data_admin,
    many_test_protected_resources,
    many_test_protected_child_resources,
    many_test_protected_grand_child_resources,
    token_admin_read_write,
    token_user1_read_write,
    current_user_data_user2,
)

# # temporarily only for debugging:
# from sqlmodel import select, or_
# from models.access import AccessPolicy

# region: ## POST tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_protected_resource(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    before_time = datetime.now()
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Test for created logs:
    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_resource.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_resource.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.resource_id == UUID(created_protected_resource.id)
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.own
    assert last_accessed_at.time == created_at
    assert last_accessed_at.status_code == 201

    async with ProtectedResourceCRUD() as crud:
        db_protected_resource = await crud.read(
            current_test_user,
            filters=[ProtectedResource.id == created_protected_resource.id],
        )
    assert len(db_protected_resource) == 1
    assert db_protected_resource[0].name == many_test_protected_resources[0]["name"]
    assert (
        db_protected_resource[0].description
        == many_test_protected_resources[0]["description"]
    )

    # Test for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            current_test_user,
            resource_id=db_protected_resource[0].id,
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == db_protected_resource[0].id
    assert policies[0].identity_id == current_test_user.user_id
    assert policies[0].action == Action.own


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_protected_child_resource_and_add_to_parent(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    add_many_test_protected_resources,
    mocked_get_azure_token_payload,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency
    protected_resources = await add_many_test_protected_resources(
        mocked_get_azure_token_payload
    )

    # Make a POST request to create the protected child as a child of a protected resource
    before_time = datetime.now()
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={protected_resources[0].id}",
        json=many_test_protected_child_resources[0],
    )
    after_time = datetime.now()

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )

    # Check for created logs:
    async with AccessLoggingCRUD() as crud:
        created_at = await crud.read_resource_created_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_child.id,
        )
        last_accessed_at = await crud.read_resource_last_accessed_at(
            CurrentUserData(**current_user_data_admin),
            resource_id=created_protected_child.id,
        )

    assert created_at > before_time - timedelta(seconds=1)
    assert created_at < after_time + timedelta(seconds=1)
    assert last_accessed_at.resource_id == UUID(created_protected_child.id)
    assert last_accessed_at.identity_id == current_test_user.user_id
    assert last_accessed_at.action == Action.own
    assert last_accessed_at.time == created_at
    assert last_accessed_at.status_code == 201

    # Check if the parent was updated in database and contains the protected child:
    async with ProtectedResourceCRUD() as crud:
        db_protected_resource = await crud.read(
            current_test_user,
            filters=[ProtectedResource.id == protected_resources[0].id],
        )
    assert len(db_protected_resource) == 1
    assert db_protected_resource[0].name == many_test_protected_resources[0]["name"]
    assert (
        db_protected_resource[0].description
        == many_test_protected_resources[0]["description"]
    )
    assert len(db_protected_resource[0].protected_children) == 1
    assert db_protected_resource[0].protected_children[0].id == UUID(
        created_protected_child.id
    )
    assert (
        db_protected_resource[0].protected_children[0].title
        == many_test_protected_child_resources[0]["title"]
    )

    # Check if the child was created in database:
    async with ProtectedChildCRUD() as crud:
        db_protected_child = await crud.read(
            current_test_user,
            filters=[ProtectedChild.id == created_protected_child.id],
        )
    assert len(db_protected_child) == 1
    assert (
        db_protected_child[0].title == many_test_protected_child_resources[0]["title"]
    )

    # Check for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            current_test_user,
            resource_id=db_protected_child[0].id,
        )
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == db_protected_child[0].id
    assert policies[0].identity_id == current_test_user.user_id
    assert policies[0].action == Action.own

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_test_user,
            parent_id=protected_resources[0].id,
            child_id=db_protected_child[0].id,
        )
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == protected_resources[0].id
    assert hierarchy_entry[0].child_id == db_protected_child[0].id
    assert hierarchy_entry[0].inherit is False


# endregion ## POST tests

# region: ## GET tests:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_child_resource_and_from_a_parent_through_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests resource inheritance."""
    app_override_get_azure_payload_dependency

    current_user = current_test_user
    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )
    assert created_protected_child.id is not None

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_user,
            parent_id=created_protected_resource.id,
            child_id=created_protected_child.id,
        )
    # print("=== hierarchy_entry ===")
    # pprint(hierarchy_entry)
    # print("\n")
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == UUID(created_protected_resource.id)
    assert hierarchy_entry[0].child_id == UUID(created_protected_child.id)
    assert hierarchy_entry[0].inherit is True

    current_user2 = await register_current_user(current_user_data_user2)

    # Give read access to the user2 for the parent resource:
    # print("=== current_user2 ===")
    # pprint(current_user2)
    # print("\n")
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    # Check for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            CurrentUserData(**current_user_data_admin),
            identity_id=current_user_data_user2["user_id"],
        )
    # print("=== policies ===")
    # pprint(policies)
    # print("\n")
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == UUID(created_protected_resource.id)
    assert policies[0].identity_id == UUID(current_user_data_user2["user_id"])
    assert policies[0].action == Action.read

    # async with get_async_test_session as session:
    #     base_resource_ids = select(AccessPolicy.resource_id).where(
    #         AccessPolicy.action.in_(["read", "write", "own"]),
    #         or_(
    #             # TBD: add in later:
    #             # AccessPolicy.identity_id.in_(
    #             #     select(identity_hierarchy_cte.c.identity_id)
    #             # ),  # omit the or_ and this line if no current_user (for public resources)
    #             AccessPolicy.identity_id == current_user2.user_id,
    #             AccessPolicy.public,
    #         ),
    #     )

    #     response_results_base_resource_ids = await session.exec(base_resource_ids)
    #     results_base_resource_ids = response_results_base_resource_ids.all()
    #     print("=== base_resource_ids ===")
    #     pprint(results_base_resource_ids)
    #     print("\n")

    #     access_policy_CRUD = AccessPolicyCRUD()
    #     resource_hierarchy_cte = (
    #         access_policy_CRUD._get_resource_inheritance_common_table_expression(
    #             base_resource_ids
    #         )
    #     )
    #     print("=== resource_hierarchy_cte ===")
    #     print(resource_hierarchy_cte.compile())
    #     print(resource_hierarchy_cte.compile().params)
    #     print("\n")

    #     response_resource_cte = await session.exec(
    #         select("*").select_from(resource_hierarchy_cte)
    #     )
    #     results_resource_cte = response_resource_cte.all()

    #     print("=== results_resource_cte ===")
    #     pprint(results_resource_cte)
    #     print("\n")

    #     # get the accessible resource ids:
    #     subquery = select(AccessPolicy.resource_id).where(
    #         AccessPolicy.action.in_(["read", "write", "own"]),
    #         or_(
    #             # TBD: add in later
    #             # AccessPolicy.identity_id.in_(
    #             #     select(identity_hierarchy_cte.c.identity_id)
    #             # ),  # omit the or_ and this line if no current_user (for public resources)
    #             AccessPolicy.identity_id == current_user2.user_id,
    #             AccessPolicy.public,
    #         ),
    #         or_(
    #             AccessPolicy.resource_id.in_(
    #                 select(resource_hierarchy_cte.c.resource_id)
    #             ),
    #             AccessPolicy.resource_id.in_(base_resource_ids),
    #         ),
    #     )

    #     print("=== subquery ===")
    #     print(subquery.compile())
    #     print(subquery.compile().params)
    #     print("\n")

    #     response_results_subquery = await session.exec(subquery)
    #     results_subquery = response_results_subquery.all()

    #     print("=== results_subquery ===")
    #     pprint(results_subquery)
    #     print("\n")

    #     assert 0

    # User2 should be able to read the child resource:

    # print("=== created_protected_child.id ===")
    # print(created_protected_child.id)
    # print("\n")

    async with ProtectedChildCRUD() as crud:
        db_protected_child = await crud.read_by_id(
            created_protected_child.id,
            current_user2,
        )

    assert db_protected_child.title == many_test_protected_child_resources[0]["title"]
    assert db_protected_child.id == UUID(created_protected_child.id)
    # Check if parent is returned with child:
    assert (
        db_protected_child.protected_resources[0].name
        == created_protected_resource.name
    )
    assert (
        db_protected_child.protected_resources[0].description
        == created_protected_resource.description
    )
    assert db_protected_child.protected_resources[0].id == UUID(
        created_protected_resource.id
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_child_resource_and_from_a_parent_through_inheritance_missing_parent_permission(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests if missing permission for parent resource is handled correctly."""
    app_override_get_azure_payload_dependency

    current_user = current_test_user
    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        # f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=False",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )
    assert created_protected_child.id is not None

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_user,
            parent_id=created_protected_resource.id,
            child_id=created_protected_child.id,
        )
    # print("=== hierarchy_entry ===")
    # pprint(hierarchy_entry)
    # print("\n")
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == UUID(created_protected_resource.id)
    assert hierarchy_entry[0].child_id == UUID(created_protected_child.id)
    assert hierarchy_entry[0].inherit is True

    current_user2 = await register_current_user(current_user_data_user2)

    # # Give read access to the user2 for the parent resource:
    # # print("=== current_user2 ===")
    # # pprint(current_user2)
    # # print("\n")
    # policy = {
    #     "resource_id": created_protected_resource.id,
    #     "identity_id": current_user_data_user2["user_id"],
    #     "action": "read",
    # }
    # await add_one_test_access_policy(policy)

    # # Check for created access policies:
    # async with AccessPolicyCRUD() as crud:
    #     policies = await crud.read(
    #         CurrentUserData(**current_user_data_admin),
    #         identity_id=current_user_data_user2["user_id"],
    #     )
    # # print("=== policies ===")
    # # pprint(policies)
    # # print("\n")
    # assert len(policies) == 1
    # assert policies[0].id is not None
    # assert policies[0].resource_id == UUID(created_protected_resource.id)
    # assert policies[0].identity_id == UUID(current_user_data_user2["user_id"])
    # assert policies[0].action == Action.read

    # async with get_async_test_session as session:
    #     base_resource_ids = select(AccessPolicy.resource_id).where(
    #         AccessPolicy.action.in_(["read", "write", "own"]),
    #         or_(
    #             # TBD: add in later:
    #             # AccessPolicy.identity_id.in_(
    #             #     select(identity_hierarchy_cte.c.identity_id)
    #             # ),  # omit the or_ and this line if no current_user (for public resources)
    #             AccessPolicy.identity_id == current_user2.user_id,
    #             AccessPolicy.public,
    #         ),
    #     )

    #     response_results_base_resource_ids = await session.exec(base_resource_ids)
    #     results_base_resource_ids = response_results_base_resource_ids.all()
    #     print("=== base_resource_ids ===")
    #     pprint(results_base_resource_ids)
    #     print("\n")

    #     access_policy_CRUD = AccessPolicyCRUD()
    #     resource_hierarchy_cte = (
    #         access_policy_CRUD._get_resource_inheritance_common_table_expression(
    #             base_resource_ids
    #         )
    #     )
    #     print("=== resource_hierarchy_cte ===")
    #     print(resource_hierarchy_cte.compile())
    #     print(resource_hierarchy_cte.compile().params)
    #     print("\n")

    #     response_resource_cte = await session.exec(
    #         select("*").select_from(resource_hierarchy_cte)
    #     )
    #     results_resource_cte = response_resource_cte.all()

    #     print("=== results_resource_cte ===")
    #     pprint(results_resource_cte)
    #     print("\n")

    #     # get the accessible resource ids:
    #     subquery = select(AccessPolicy.resource_id).where(
    #         AccessPolicy.action.in_(["read", "write", "own"]),
    #         or_(
    #             # TBD: add in later
    #             # AccessPolicy.identity_id.in_(
    #             #     select(identity_hierarchy_cte.c.identity_id)
    #             # ),  # omit the or_ and this line if no current_user (for public resources)
    #             AccessPolicy.identity_id == current_user2.user_id,
    #             AccessPolicy.public,
    #         ),
    #         or_(
    #             AccessPolicy.resource_id.in_(
    #                 select(resource_hierarchy_cte.c.resource_id)
    #             ),
    #             AccessPolicy.resource_id.in_(base_resource_ids),
    #         ),
    #     )

    #     print("=== subquery ===")
    #     print(subquery.compile())
    #     print(subquery.compile().params)
    #     print("\n")

    #     response_results_subquery = await session.exec(subquery)
    #     results_subquery = response_results_subquery.all()

    #     print("=== results_subquery ===")
    #     pprint(results_subquery)
    #     print("\n")

    #     assert 0

    # User2 should be able to read the child resource:

    # print("=== created_protected_child.id ===")
    # print(created_protected_child.id)
    # print("\n")

    async with ProtectedChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_child_resource_and_from_a_parent_missing_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests if missing inheritance for child resource is handled correctly."""
    app_override_get_azure_payload_dependency

    current_user = current_test_user
    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=False",
        json=many_test_protected_child_resources[0],
    )

    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response.json())
    assert (
        created_protected_child.title == many_test_protected_child_resources[0]["title"]
    )
    assert created_protected_child.id is not None

    # Check for created hierarchy entry:
    async with ResourceHierarchyCRUD() as crud:
        hierarchy_entry = await crud.read(
            current_user,
            parent_id=created_protected_resource.id,
            child_id=created_protected_child.id,
        )
    # print("=== hierarchy_entry ===")
    # pprint(hierarchy_entry)
    # print("\n")
    assert len(hierarchy_entry) == 1
    assert hierarchy_entry[0].parent_id == UUID(created_protected_resource.id)
    assert hierarchy_entry[0].child_id == UUID(created_protected_child.id)
    assert hierarchy_entry[0].inherit is False

    current_user2 = await register_current_user(current_user_data_user2)

    # Give read access to the user2 for the parent resource:
    # print("=== current_user2 ===")
    # pprint(current_user2)
    # print("\n")
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    # Check for created access policies:
    async with AccessPolicyCRUD() as crud:
        policies = await crud.read(
            CurrentUserData(**current_user_data_admin),
            identity_id=current_user_data_user2["user_id"],
        )
    # print("=== policies ===")
    # pprint(policies)
    # print("\n")
    assert len(policies) == 1
    assert policies[0].id is not None
    assert policies[0].resource_id == UUID(created_protected_resource.id)
    assert policies[0].identity_id == UUID(current_user_data_user2["user_id"])
    assert policies[0].action == Action.read

    # async with get_async_test_session as session:
    #     base_resource_ids = select(AccessPolicy.resource_id).where(
    #         AccessPolicy.action.in_(["read", "write", "own"]),
    #         or_(
    #             # TBD: add in later:
    #             # AccessPolicy.identity_id.in_(
    #             #     select(identity_hierarchy_cte.c.identity_id)
    #             # ),  # omit the or_ and this line if no current_user (for public resources)
    #             AccessPolicy.identity_id == current_user2.user_id,
    #             AccessPolicy.public,
    #         ),
    #     )

    #     response_results_base_resource_ids = await session.exec(base_resource_ids)
    #     results_base_resource_ids = response_results_base_resource_ids.all()
    #     print("=== base_resource_ids ===")
    #     pprint(results_base_resource_ids)
    #     print("\n")

    #     access_policy_CRUD = AccessPolicyCRUD()
    #     resource_hierarchy_cte = (
    #         access_policy_CRUD._get_resource_inheritance_common_table_expression(
    #             base_resource_ids
    #         )
    #     )
    #     print("=== resource_hierarchy_cte ===")
    #     print(resource_hierarchy_cte.compile())
    #     print(resource_hierarchy_cte.compile().params)
    #     print("\n")

    #     response_resource_cte = await session.exec(
    #         select("*").select_from(resource_hierarchy_cte)
    #     )
    #     results_resource_cte = response_resource_cte.all()

    #     print("=== results_resource_cte ===")
    #     pprint(results_resource_cte)
    #     print("\n")

    #     # get the accessible resource ids:
    #     subquery = select(AccessPolicy.resource_id).where(
    #         AccessPolicy.action.in_(["read", "write", "own"]),
    #         or_(
    #             # TBD: add in later
    #             # AccessPolicy.identity_id.in_(
    #             #     select(identity_hierarchy_cte.c.identity_id)
    #             # ),  # omit the or_ and this line if no current_user (for public resources)
    #             AccessPolicy.identity_id == current_user2.user_id,
    #             AccessPolicy.public,
    #         ),
    #         or_(
    #             AccessPolicy.resource_id.in_(
    #                 select(resource_hierarchy_cte.c.resource_id)
    #             ),
    #             AccessPolicy.resource_id.in_(base_resource_ids),
    #         ),
    #     )

    #     print("=== subquery ===")
    #     print(subquery.compile())
    #     print(subquery.compile().params)
    #     print("\n")

    #     response_results_subquery = await session.exec(subquery)
    #     results_subquery = response_results_subquery.all()

    #     print("=== results_subquery ===")
    #     pprint(results_subquery)
    #     print("\n")

    #     assert 0

    # User2 should be able to read the child resource:

    # print("=== created_protected_child.id ===")
    # print(created_protected_child.id)
    # print("\n")

    async with ProtectedChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=True",
        json=many_test_protected_grand_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)

    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    async with ProtectedGrandChildCRUD() as crud:
        db_protected_grand_child = await crud.read_by_id(
            created_protected_grand_child.id,
            current_user2,
        )

    assert (
        db_protected_grand_child.text
        == many_test_protected_grand_child_resources[0]["text"]
    )
    assert db_protected_grand_child.id == UUID(created_protected_grand_child.id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent_missing_permission(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=True",
        json=many_test_protected_grand_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)

    async with ProtectedGrandChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_grand_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedGrandChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent_missing_child_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=False",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=True",
        json=many_test_protected_grand_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)
    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    async with ProtectedGrandChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_grand_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedGrandChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_get_protected_grand_child_resource_through_inheritance_via_child_from_parent_missing_child_inheritance(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
    register_current_user,
    add_one_test_access_policy,
    get_async_test_session,
):
    """Tests ."""
    app_override_get_azure_payload_dependency

    # Make a POST request to create the protected resource
    response = await async_client.post(
        "/api/v1/protected/resource/",
        json=many_test_protected_resources[0],
    )

    assert response.status_code == 201
    created_protected_resource = ProtectedResource(**response.json())
    assert created_protected_resource.name == many_test_protected_resources[0]["name"]
    assert (
        created_protected_resource.description
        == many_test_protected_resources[0]["description"]
    )

    # Make a POST request to create the protected child as a child of a protected resource
    response_child = await async_client.post(
        f"/api/v1/protected/child/?parent_id={created_protected_resource.id}&inherit=True",
        json=many_test_protected_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_child = ProtectedChild(**response_child.json())

    # Make a POST request to create the protected grandchild as a child of a protected child resource
    response_grandchild = await async_client.post(
        f"/api/v1/protected/grandchild/?parent_id={created_protected_child.id}&inherit=False",
        json=many_test_protected_grand_child_resources[0],
    )
    assert response.status_code == 201
    created_protected_grand_child = ProtectedGrandChild(**response_grandchild.json())

    current_user2 = await register_current_user(current_user_data_user2)
    # Give read access to the user2 for the parent resource:
    policy = {
        "resource_id": created_protected_resource.id,
        "identity_id": current_user_data_user2["user_id"],
        "action": "read",
    }
    await add_one_test_access_policy(policy)

    async with ProtectedGrandChildCRUD() as crud:
        try:
            await crud.read_by_id(
                created_protected_grand_child.id,
                current_user2,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "ProtectedGrandChild not found."
        else:
            pytest.fail("No HTTPexception raised!")


# endregion ## GET tests

# AccessPolicy and AccessLog tests not necessary in all tests! Just in one post, one read, one update and one delete test!


# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Tests to implement for the protected resource family API:
# ✔︎ User and Admin creates a protected resource: gets logged and access policy created
# ✔︎ User creates a child resource for a protected resource: hierarchy entry gets created
# X User reads all protected resource: only the protected resources and child resources, that the user has access to are returned
# X User reads a protected resource by id: gets logged
# - User reads a protected resource: children and grand children get returned as well - but only the ones the user has access to
# ✔︎ User and Admin reads a child protected resource, where resource inherits access from parent
# ✔︎ User and Admin reads a child protected resource, where resource inherits access from parent but user has no access to parent
# ✔︎ User and Admin reads a child protected resource, where resource does not inherit access from parent but user has access to parent
# - User reads a grand child protected resource, where user inherits access from grand parent (which is a protected resource)
# X User2 reads child and grand child where access to the parent resource through is inherited through subsubgroup / subgroup / group to parent resource
# - User reads a protected resource, where user inherits access from a group
# - User reads a protected resource, where user is in a sub_sub_group and inherits access from membership in a group
# - User reads a protected resource fails, where inheritance is set to false (resource inheritance)
# - User reads a protected resource fails, where inheritance is set to false (group inheritance)
# X User updates a protected resource: gets logged
# - User updates a protected resource: with inherited write access from parent / grand parent (resource inheritance)
# - User updates a protected resource: with inherited write access from group, where user is in group / sub-group / sub-sub-group (group inheritance)
# X User deletes a protected resource: gets logged
# - User deletes a protected resource: with inherited owner access from parent / grand parent (resource inheritance)
# - User deletes a protected resource: with inherited owner access from group, where user is in group / sub-group / sub-sub-group (group inheritance)
