import pytest
import uuid
from datetime import datetime, timedelta


from crud.access import AccessPolicyCRUD, AccessLoggingCRUD
from models.access import AccessPolicyCreate, AccessPolicy, AccessLog

from core.types import CurrentUserData

from tests.utils import (
    many_test_azure_users,
    token_payload_roles_admin,
    one_test_policy_read,
    one_test_policy_write,
    one_test_policy_own,
    one_test_policy_share,
    one_test_policy_public_read,
    many_test_policies,
    many_test_azure_users,
    user_id_nonexistent,
)

# region AccessPolicy CRUD tests


@pytest.mark.anyio
async def test_admin_creates_access_policy():
    """Test creating an access policy."""

    mocked_admin_user = CurrentUserData(
        user_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
        roles=token_payload_roles_admin["roles"],
    )

    async with AccessPolicyCRUD() as policy_crud:
        policy = AccessPolicy(**one_test_policy_read)
        created_policy = await policy_crud.create(policy, mocked_admin_user)

    modelled_test_policy = AccessPolicyCreate(**one_test_policy_read)
    assert created_policy.id is not None
    assert created_policy.identity_id == modelled_test_policy.identity_id
    assert created_policy.identity_type == modelled_test_policy.identity_type
    assert created_policy.resource_id == modelled_test_policy.resource_id
    assert created_policy.resource_type == modelled_test_policy.resource_type
    assert created_policy.action == modelled_test_policy.action


@pytest.mark.anyio
async def test_owner_creates_access_policy(add_test_access_policies):
    """Test creating an access policy."""

    await add_test_access_policies([one_test_policy_own])

    mocked_user = CurrentUserData(
        user_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
    )

    async with AccessPolicyCRUD() as policy_crud:
        policy = AccessPolicy(**one_test_policy_share)
        created_policy = await policy_crud.create(policy, mocked_user)

    modelled_test_policy = AccessPolicyCreate(**one_test_policy_share)
    assert created_policy.id is not None
    assert created_policy.identity_id == modelled_test_policy.identity_id
    assert created_policy.identity_type == modelled_test_policy.identity_type
    assert created_policy.resource_id == modelled_test_policy.resource_id
    assert created_policy.resource_type == modelled_test_policy.resource_type
    assert created_policy.action == modelled_test_policy.action


@pytest.mark.anyio
async def test_prevent_create_duplicate_access_policy():
    """Test preventing the creation of a duplicate access policy."""

    mocked_admin_user = CurrentUserData(
        user_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
    )

    async with AccessPolicyCRUD() as policy_crud:
        try:
            policy = await policy_crud.create(many_test_policies[2], mocked_admin_user)
            print(policy)
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource():
    """Test preventing the creation of a duplicate access policy."""

    mocked_admin_user = CurrentUserData(
        user_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
        roles=token_payload_roles_admin["roles"],
    )

    one_public_test_policy = one_test_policy_public_read

    public_resource_policy = {
        **one_public_test_policy,
        "public": True,
    }
    modelled_policy = AccessPolicyCreate(**public_resource_policy)
    async with AccessPolicyCRUD() as policy_crud:
        created_policy = await policy_crud.create(
            public_resource_policy, mocked_admin_user
        )

    assert created_policy.id is not None
    assert created_policy.identity_id is None
    assert created_policy.identity_type is None
    assert created_policy.resource_id == modelled_policy.resource_id
    assert created_policy.resource_type == modelled_policy.resource_type
    assert created_policy.action == modelled_policy.action


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource_with_identity_fails():
    """Test preventing the creation of a public access policy with specific identity."""

    mocked_admin_user = CurrentUserData(
        user_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
    )

    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.create(one_test_policy_public_read, mocked_admin_user)
    except Exception as err:
        # TBD: change to 422?
        assert err.status_code == 403
        assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_create_access_policy_for_non_public_resource_without_identity_fails():
    """Test preventing the creation of a public access policy with specific identity."""

    invalid_policy = {
        "resource_id": str(uuid.uuid4()),
        "resource_type": "ProtectedResource",
        "action": "read",
    }

    mocked_admin_user = CurrentUserData(
        user_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
    )

    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.create(invalid_policy, mocked_admin_user)
    except Exception as err:
        # TBD: change to 422?
        assert err.status_code == 403
        assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_read_access_policy_by_id(
    add_many_test_access_policies,
):
    """Test reading an access policy by id."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_id(3)
        read_policy = await policy_crud.read(policies[2].id)

    assert read_policy.id == policies[2].id
    assert read_policy.identity_id == policies[2].identity_id
    assert read_policy.identity_type == policies[2].identity_type
    assert read_policy.resource_id == policies[2].resource_id
    assert read_policy.resource_type == policies[2].resource_type
    assert read_policy.action == policies[2].action


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_id(
    add_many_test_access_policies,
):
    """Test reading an access policy by id."""
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # results = await policy_crud.read_by_id(1234)
            await policy_crud.read(uuid.uuid4())
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_by_identity(
    add_many_test_access_policies,
):
    """Test reading multiple access policies for a given identity."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_identity(
        read_policy = await policy_crud.read(
            identity_id=uuid.UUID(many_test_azure_users[1]["azure_user_id"]),
        )

    assert len(read_policy) == 2
    assert read_policy[0].id is not None
    assert read_policy[1].id is not None

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
                identity_id=uuid.UUID(user_id_nonexistent),
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_by_resource(
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_resource(
        read_policy = await policy_crud.read(
            resource_id=policies[1].resource_id,
            resource_type="ProtectedResource",
        )
        assert len(read_policy) == 2

        assert read_policy[0].id is not None
        assert read_policy[1].id is not None

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
async def test_read_access_policy_by_resource_missing_resource_type(
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=policies[1].resource_id,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_for_wrong_resource_type(
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=policies[1].resource_id,
                resource_type="wrong_resource_type",
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_resource(
    add_many_test_access_policies,
):
    """Test reading an access policy by id."""
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=uuid.uuid4(),
                resource_type="protected_resource",
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            pytest.fail("No HTTPexception raised!")


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

    assert read_policy[0].id is not None
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

    assert read_policy[0].id is not None
    assert read_policy[0].identity_id == policies[2].identity_id
    assert read_policy[0].identity_type == policies[2].identity_type
    assert read_policy[0].resource_id == policies[2].resource_id
    assert read_policy[0].resource_type == policies[2].resource_type
    assert read_policy[0].action == policies[2].action


# TBD: add tests for update


# TBD: add tests for missing own policies
@pytest.mark.anyio
async def test_delete_access_policy_by_id(add_many_test_access_policies):
    """Test deleting an access policy."""
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(policies[2].id)

    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.read(policies[2].id)
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found"
        else:
            pytest.fail("No HTTPexception raised!")


# endregion AccessPolicy CRUD tests

# region AccessLogging CRUD tests


@pytest.mark.anyio
async def test_create_access_log():
    """Test creating an access log."""
    access_log = AccessLog(
        identity_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
        identity_type="User",
        resource_id=uuid.uuid4(),
        resource_type="ProtectedResource",
        action="read",
        status_code=200,
    )

    async with AccessLoggingCRUD() as logging_crud:
        created_log = await logging_crud.log_access(access_log)

    assert created_log.id is not None
    assert created_log.identity_id == access_log.identity_id
    assert created_log.identity_type == access_log.identity_type
    assert created_log.resource_id == access_log.resource_id
    assert created_log.resource_type == access_log.resource_type
    assert created_log.action == access_log.action
    assert created_log.status_code == access_log.status_code


@pytest.mark.anyio
async def test_read_access_log():
    """Test creating an access log."""

    resource_id = uuid.uuid4()

    access_log = AccessLog(
        identity_id=uuid.UUID(many_test_azure_users[0]["azure_user_id"]),
        identity_type="User",
        resource_id=resource_id,
        resource_type="ProtectedResource",
        action="read",
        status_code=200,
    )

    time_before = datetime.now()
    async with AccessLoggingCRUD() as logging_crud:
        await logging_crud.log_access(access_log)
    time_after = datetime.now()

    async with AccessLoggingCRUD() as crud:
        identity_log = await crud.read_log_by_identity_id(
            many_test_azure_users[0]["azure_user_id"]
        )
        resource_log = await crud.read_log_by_resource(
            resource_id,
            "ProtectedResource",
        )
    assert len(identity_log) == 1
    assert identity_log[0].id is not None
    assert identity_log[0].resource_id == access_log.resource_id
    assert identity_log[0].resource_type == access_log.resource_type
    assert identity_log[0].identity_id == uuid.UUID(
        many_test_azure_users[0]["azure_user_id"]
    )
    assert identity_log[0].identity_type == "User"
    assert identity_log[0].action == access_log.action
    assert identity_log[0].status_code == access_log.status_code
    assert identity_log[0].time >= time_before - timedelta(seconds=25)
    assert identity_log[0].time <= time_after + timedelta(seconds=25)

    # TBD: move the double checking to the tests for access control in crud access tests:
    assert len(resource_log) == 1
    assert resource_log[0].id == identity_log[0].id
    assert resource_log[0].resource_id == identity_log[0].resource_id
    assert resource_log[0].resource_type == identity_log[0].resource_type
    assert resource_log[0].identity_id == identity_log[0].identity_id
    assert resource_log[0].identity_type == identity_log[0].identity_type
    assert resource_log[0].status_code == identity_log[0].status_code
    assert resource_log[0].action == identity_log[0].action
    assert resource_log[0].time == identity_log[0].time


# endregion AccessLogging CRUD tests
