import pytest
from uuid import UUID

from crud.access import AccessPolicyCRUD
from models.access import AccessPolicyCreate, AccessPolicy

from core.types import CurrentUserData

from tests.utils import (
    one_test_user,
    token_payload_roles_admin,
    one_test_policy,
    many_test_policies,
    many_test_users,
    user_id_nonexistent,
)


@pytest.mark.anyio
async def test_admin_creates_access_policy():
    """Test creating an access policy."""

    mocked_admin_user = CurrentUserData(
        user_id=UUID(one_test_user["azure_user_id"]),
        roles=token_payload_roles_admin["roles"],
    )

    async with AccessPolicyCRUD() as policy_crud:
        policy = AccessPolicy(**one_test_policy)
        created_policy = await policy_crud.create(policy, mocked_admin_user)

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
async def test_owner_creates_access_policy():
    """Test creating an access policy."""

    mocked_admin_user = CurrentUserData(
        user_id=UUID(one_test_user["azure_user_id"]),
    )

    async with AccessPolicyCRUD() as policy_crud:
        policy = AccessPolicy(**one_test_policy)
        created_policy = await policy_crud.create(policy, mocked_admin_user)

    # Using the SQLModels and comparing it's attributes:
    modelled_test_policy = AccessPolicyCreate(**one_test_policy)
    assert created_policy.policy_id is not None
    assert created_policy.identity_id == modelled_test_policy.identity_id
    assert created_policy.identity_type == modelled_test_policy.identity_type
    assert created_policy.resource_id == modelled_test_policy.resource_id
    assert created_policy.resource_type == modelled_test_policy.resource_type
    assert created_policy.action == modelled_test_policy.action


@pytest.mark.anyio
async def test_prevent_create_duplicate_access_policy(add_many_test_access_policies):
    """Test preventing the creation of a duplicate access policy."""
    add_many_test_access_policies

    mocked_admin_user = CurrentUserData(
        user_id=UUID(one_test_user["azure_user_id"]),
    )

    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.create(many_test_policies[2], mocked_admin_user)
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden"
        else:
            # test above should enter the except statement and not reach this point
            assert 1 == 2


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource():
    """Test preventing the creation of a duplicate access policy."""

    mocked_admin_user = CurrentUserData(
        user_id=UUID(one_test_user["azure_user_id"]),
        roles=token_payload_roles_admin["roles"],
    )

    one_public_test_policy = one_test_policy.copy()
    one_public_test_policy.pop("identity_id")
    one_public_test_policy.pop("identity_type")

    public_resource_policy = {
        **one_public_test_policy,
        "public": True,
    }
    modelled_policy = AccessPolicyCreate(**public_resource_policy)
    async with AccessPolicyCRUD() as policy_crud:
        created_policy = await policy_crud.create(
            public_resource_policy, mocked_admin_user
        )

    assert created_policy.policy_id is not None
    assert created_policy.identity_id is None
    assert created_policy.identity_type is None
    assert created_policy.resource_id == modelled_policy.resource_id
    assert created_policy.resource_type == modelled_policy.resource_type
    assert created_policy.action == modelled_policy.action


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource_with_identity_fails():
    """Test preventing the creation of a public access policy with specific identity."""

    mocked_admin_user = CurrentUserData(
        user_id=UUID(one_test_user["azure_user_id"]),
    )

    public_resource_policy_with_identity = {
        **one_test_policy,
        "public": True,
    }

    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.create(
                public_resource_policy_with_identity, mocked_admin_user
            )
    except Exception as err:
        # TBD: change to 422?
        assert err.status_code == 403
        assert err.detail == "Forbidden"


@pytest.mark.anyio
async def test_create_access_policy_for_non_public_resource_without_identity_fails():
    """Test preventing the creation of a public access policy with specific identity."""

    one_public_test_policy = one_test_policy.copy()

    one_public_test_policy.pop("identity_id")
    one_public_test_policy.pop("identity_type")

    one_test_policy_without_identity = one_test_policy

    mocked_admin_user = CurrentUserData(
        user_id=UUID(one_test_user["azure_user_id"]),
    )

    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.create(
                one_test_policy_without_identity, mocked_admin_user
            )
    except Exception as err:
        # TBD: change to 422?
        assert err.status_code == 403
        assert err.detail == "Forbidden"


@pytest.mark.anyio
async def test_read_access_policy_by_policy_id(
    add_many_test_access_policies,
):
    """Test reading an access policy by policy_id."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_policy_id(3)
        read_policy = await policy_crud.read(3)

    assert read_policy.policy_id == 3
    assert read_policy.identity_id == policies[2].identity_id
    assert read_policy.identity_type == policies[2].identity_type
    assert read_policy.resource_id == policies[2].resource_id
    assert read_policy.resource_type == policies[2].resource_type
    assert read_policy.action == policies[2].action


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_policy_id(
    add_many_test_access_policies,
):
    """Test reading an access policy by policy_id."""
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # results = await policy_crud.read_by_policy_id(1234)
            await policy_crud.read(1234)
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            # test above should enter the except statement and not reach this point
            assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_by_identity(
    add_many_test_access_policies,
):
    """Test reading multiple access policies for a given identity."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_identity(
        read_policy = await policy_crud.read(
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
    add_many_test_access_policies,
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_identity(
            await policy_crud.read(
                identity_id=UUID(user_id_nonexistent),
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            # test above should enter the except statement and not reach this point
            assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_by_resource(
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_resource(
        read_policy = await policy_crud.read(
            resource_id=4,
            resource_type="protected_resource",
        )
        assert len(read_policy) == 2

        assert read_policy[0].policy_id is not None
        assert read_policy[1].policy_id is not None

        assert read_policy[0].identity_id == policies[1].identity_id
        assert read_policy[0].identity_type == policies[1].identity_type
        assert read_policy[0].resource_id == policies[1].resource_id
        assert read_policy[0].resource_type == policies[1].resource_type
        assert read_policy[0].action == policies[1].action

        assert read_policy[1].identity_id == policies[2].identity_id
        assert read_policy[1].identity_type == policies[2].identity_type
        assert read_policy[1].resource_id == policies[2].resource_id
        assert read_policy[1].resource_type == policies[2].resource_type
        assert read_policy[1].action == policies[2].action


@pytest.mark.anyio
async def test_read_access_policy_for_wrong_resource_type(
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=4,
                resource_type="wrong_resource_type",
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            # test above should enter the except statement and not reach this point
            assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_resource(
    add_many_test_access_policies,
):
    """Test reading an access policy by policy_id."""
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=1234,
                resource_type="protected_resource",
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            # test above should enter the except statement and not reach this point
            assert 1 == 2


@pytest.mark.anyio
async def test_read_access_policy_by_identity_and_resource(
    add_many_test_access_policies,
):
    """Test reading an access policy by identity and resource."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_identity_and_resource(
        read_policy = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            resource_type=policies[2].resource_type,
        )

    assert len(read_policy) == 1

    assert read_policy[0].policy_id is not None
    assert read_policy[0].identity_id == policies[2].identity_id
    assert read_policy[0].identity_type == policies[2].identity_type
    assert read_policy[0].resource_id == policies[2].resource_id
    assert read_policy[0].resource_type == policies[2].resource_type
    assert read_policy[0].action == policies[2].action


@pytest.mark.anyio
async def test_read_access_policy_by_identity_and_resource_and_action(
    add_many_test_access_policies,
):
    """Test reading an access policy by identity and resource."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_identity_and_resource_and_action(
        read_policy = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            resource_type=policies[2].resource_type,
            action=policies[2].action,
        )

    assert len(read_policy) == 1

    assert read_policy[0].policy_id is not None
    assert read_policy[0].identity_id == policies[2].identity_id
    assert read_policy[0].identity_type == policies[2].identity_type
    assert read_policy[0].resource_id == policies[2].resource_id
    assert read_policy[0].resource_type == policies[2].resource_type
    assert read_policy[0].action == policies[2].action


@pytest.mark.anyio
async def test_delete_access_policy_by_policy_id(add_many_test_access_policies):
    """Test deleting an access policy."""
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(3)

    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.read(3)
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            # test above should enter the except statement and not reach this point
            assert 1 == 2
