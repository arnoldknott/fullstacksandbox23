import pytest
from uuid import UUID

from crud.access import AccessPolicyCRUD
from models.access import AccessPolicyCreate, AccessPolicy

from tests.utils import one_test_policy, many_test_users, user_id_nonexistent


@pytest.mark.anyio
async def test_create_access_policy():
    """Test creating an access policy."""

    async with AccessPolicyCRUD() as policy_crud:
        policy = AccessPolicy(**one_test_policy)
        created_policy = await policy_crud.create(policy)

    # Using the SQLModels and comparing it's attributes:
    modelled_test_policy = AccessPolicyCreate(**one_test_policy)
    # print("=== test_create_access_policy - policy ===")
    # print(policy)
    # print("=== test_create_access_policy - modelled_test_policy ===")
    # print(modelled_test_policy)
    # print("=== test_create_access_policy - created_policy ===")
    # print(created_policy)
    assert created_policy.policy_id is not None
    assert created_policy.identity_id == modelled_test_policy.identity_id
    assert created_policy.identity_type == modelled_test_policy.identity_type
    assert created_policy.resource_id == modelled_test_policy.resource_id
    assert created_policy.resource_type == modelled_test_policy.resource_type
    assert created_policy.action == modelled_test_policy.action

    # # Without using the SQLModels, i.e. basically comparing the Python dictionaries:
    # policy_in_db = created_policy.model_dump()
    # assert policy_in_db["identity_id"] == UUID(one_test_policy["identity_id"])
    # assert policy_in_db["identity_type"] == one_test_policy["identity_type"]
    # assert policy_in_db["resource_id"] == one_test_policy["resource_id"]
    # assert policy_in_db["resource_type"] == one_test_policy["resource_type"]
    # assert policy_in_db["action"] == Action(one_test_policy["action"])


@pytest.mark.anyio
async def test_read_access_policy_by_policy_id(
    add_many_test_access_policies,
):
    """Test reading an access policy by policy_id."""
    assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_policy_id():
    """Test reading an access policy by policy_id."""
    assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_by_identity(
    add_many_test_access_policies,
):
    """Test reading multiple access policies for a given identity."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read_by_identity(
            identity_id=UUID(many_test_users[1]["azure_user_id"]),
        )

    assert len(read_policy) == 2
    assert read_policy[0].policy_id is not None
    assert read_policy[1].policy_id is not None

    assert read_policy[0].identity_id == policies[0].identity_id
    assert read_policy[0].identity_type == policies[0].identity_type
    assert read_policy[0].resource_id == policies[0].resource_id
    assert read_policy[0].resource_type == policies[0].resource_type
    assert read_policy[0].action == policies[0].action

    assert read_policy[1].identity_id == policies[4].identity_id
    assert read_policy[1].identity_type == policies[4].identity_type
    assert read_policy[1].resource_id == policies[4].resource_id
    assert read_policy[1].resource_type == policies[4].resource_type
    assert read_policy[1].action == policies[4].action


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_identity(
    add_many_test_access_policies,
):
    """Test reading an access policy for an identity, that does not exist."""
    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.read_by_identity(
                identity_id=UUID(user_id_nonexistent),
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"


@pytest.mark.anyio
async def test_read_access_policy_by_resource(
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_resource():
    """Test reading an access policy by policy_id."""
    assert 1 == 2
