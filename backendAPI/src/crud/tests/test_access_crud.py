import pytest
import uuid
from datetime import datetime, timedelta
from pprint import pprint

from core.types import Action, CurrentUserData
from crud.access import AccessPolicyCRUD, AccessLoggingCRUD
from models.protected_resource import ProtectedResource
from models.access import (
    AccessPolicyCreate,
    AccessPolicy,
    AccessLogCreate,
)


from tests.utils import (
    current_user_data_admin,
    current_user_data_user1,
    current_user_data_user2,
    current_user_data_user3,
    one_test_policy_read,
    one_test_policy_own,
    one_test_policy_share,
    one_test_policy_public_read,
    many_test_policies,
    user_id_nonexistent,
)

# region AccessPolicy CRUD tests


@pytest.mark.anyio
async def test_admin_creates_access_policy(
    register_current_user, register_one_resource
):
    """Test creating an access policy."""

    # mocked_admin_user = CurrentUserData(**current_user_data_admin)
    current_admin_user = await register_current_user(current_user_data_admin)

    policy = AccessPolicy(**one_test_policy_read)
    await register_one_resource(uuid.UUID(policy.resource_id), ProtectedResource)

    async with AccessPolicyCRUD() as policy_crud:
        await register_current_user(current_user_data_user1)
        created_policy = await policy_crud.create(policy, current_admin_user)

    modelled_test_policy = AccessPolicyCreate(**one_test_policy_read)
    assert int(created_policy.id)
    assert created_policy.identity_id == modelled_test_policy.identity_id
    assert created_policy.resource_id == modelled_test_policy.resource_id
    assert created_policy.action == modelled_test_policy.action


@pytest.mark.anyio
async def test_owner_creates_access_policy(
    register_current_user,
    register_one_resource,
    add_test_access_policy,
):
    """Test creating an access policy."""

    # users need to be registered for the policies to be created:
    sharing_user = await register_current_user(current_user_data_user1)
    await register_current_user(current_user_data_user3)

    # resources need to be registered for the policies to be created:
    policy = AccessPolicy(**one_test_policy_own)

    # Admin needs to register the first resource - owned by user 1:
    current_admin_user = await register_current_user(current_user_data_admin)
    await add_test_access_policy(one_test_policy_own, current_admin_user)

    # User 1 shares with user 3:
    async with AccessPolicyCRUD() as policy_crud:
        policy = AccessPolicy(**one_test_policy_share)
        created_policy = await policy_crud.create(policy, sharing_user)

    modelled_test_policy = AccessPolicyCreate(**one_test_policy_share)
    assert int(created_policy.id)
    assert created_policy.identity_id == modelled_test_policy.identity_id
    assert created_policy.resource_id == modelled_test_policy.resource_id
    assert created_policy.action == modelled_test_policy.action


@pytest.mark.anyio
async def test_prevent_create_duplicate_access_policy(
    register_many_current_users,
    register_many_protected_resources,
    add_many_test_access_policies,
):
    """Test preventing the creation of a duplicate access policy."""

    current_users = register_many_current_users
    register_many_protected_resources

    add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        try:
            policy = await policy_crud.create(many_test_policies[2], current_users[0])
            print(policy)
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource(
    register_current_user, register_many_protected_resources
):
    """Test preventing the creation of a duplicate access policy."""

    current_admin_user = await register_current_user(current_user_data_admin)
    register_many_protected_resources

    modelled_policy = AccessPolicy(**one_test_policy_public_read)
    async with AccessPolicyCRUD() as policy_crud:
        created_policy = await policy_crud.create(modelled_policy, current_admin_user)

    assert created_policy.resource_id == uuid.UUID(modelled_policy.resource_id)
    assert created_policy.identity_id is None
    assert created_policy.action == modelled_policy.action


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource_with_identity_fails(
    register_current_user,
):
    """Test preventing the creation of a public access policy with specific identity."""

    current_admin_user = await register_current_user(current_user_data_admin)

    public_resource_policy_with_identity = {
        **one_test_policy_public_read,
        "identity_id": str(uuid.uuid4()),
    }
    modelled_policy = AccessPolicy(**public_resource_policy_with_identity)

    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.create(modelled_policy, current_admin_user)
    except Exception as err:
        # TBD: change to 422?
        assert err.status_code == 403
        assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_create_access_policy_for_non_public_resource_without_identity_fails(
    register_current_user,
):
    """Test preventing the creation of a public access policy with specific identity."""

    invalid_policy = {
        "resource_id": str(uuid.uuid4()),
        "action": "read",
    }

    current_admin_user = await register_current_user(current_user_data_admin)

    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.create(invalid_policy, current_admin_user)
    except Exception as err:
        # TBD: change to 422?
        assert err.status_code == 403
        assert err.detail == "Forbidden."


# TBD: add tests for creating policies for non-existing resource and identity types

# TBD: implement tests for filters_allowed and allowed methods - or leave this to the read / delete?


@pytest.mark.anyio
async def test_admin_read_access_policy_by_resource(
    register_many_current_users,
    register_many_protected_resources,
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    current_admin_user = register_many_current_users[0]
    register_many_protected_resources

    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_resource(
        read_policy = await policy_crud.read(
            resource_id=policies[1].resource_id,
            current_user=current_admin_user,
        )
        assert len(read_policy) == 2

        assert int(read_policy[0].id)
        assert read_policy[0].identity_id == policies[1].identity_id
        assert read_policy[0].resource_id == policies[1].resource_id
        assert read_policy[0].action == policies[1].action

        assert int(read_policy[1].id)
        assert read_policy[1].identity_id == policies[2].identity_id
        assert read_policy[1].resource_id == policies[2].resource_id
        assert read_policy[1].action == policies[2].action


@pytest.mark.anyio
async def test_user_read_access_policy_by_resource_id(
    register_many_current_users,
    register_many_protected_resources,
    add_many_test_access_policies,
):
    """Test user reading an access policy by id."""

    register_many_protected_resources,
    policies = add_many_test_access_policies
    current_user1 = register_many_current_users[1]

    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            resource_id=policies[1].resource_id, current_user=current_user1
        )

    assert int(read_policy[0].id)
    assert read_policy[0].identity_id == policies[1].identity_id
    assert read_policy[0].resource_id == policies[1].resource_id
    assert read_policy[0].action == policies[1].action


# TBD: change to resource_id / identity_id or delete?
@pytest.mark.anyio
async def test_read_access_policy_by_id_without_permission(
    register_many_current_users,
    register_many_protected_resources,
    add_many_test_access_policies,
):
    """Test reading an access policy by id without permission."""
    register_many_current_users,
    register_many_protected_resources
    policies = add_many_test_access_policies
    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.read(resource_id=policies[2].resource_id)
    except Exception as err:
        assert err.status_code == 404
        assert err.detail == "Access policy not found."
    else:
        pytest.fail("No HTTPexception raised!")


# TBD: implement tests for filters_allowed logic:
# - public resource


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_resource_id(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy by id."""
    register_many_protected_resources
    current_admin_user = register_many_current_users[0]
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # results = await policy_crud.read_by_id(1234)
            await policy_crud.read(
                resource_id=uuid.uuid4(),
                current_user=current_admin_user,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_by_identity(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading multiple access policies for a given identity."""
    register_many_protected_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            identity_id=current_user_data_user2["user_id"],
            current_user=current_admin_user,
        )

    assert len(read_policy) == 2

    assert int(read_policy[0].id)
    assert read_policy[0].identity_id == policies[0].identity_id
    assert read_policy[0].resource_id == policies[0].resource_id
    assert read_policy[0].action == policies[0].action

    assert int(read_policy[1].id)
    assert read_policy[1].identity_id == policies[4].identity_id
    assert read_policy[1].resource_id == policies[4].resource_id
    assert read_policy[1].action == policies[4].action


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_identity(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy for an identity, that does not exist."""
    register_many_protected_resources,
    current_admin_user = register_many_current_users[0]
    add_many_test_access_policies,
    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.read(
                identity_id=uuid.UUID(user_id_nonexistent),
                current_user=current_admin_user,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_by_resource_missing_resource_type(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    register_many_protected_resources
    current_admin_user = register_many_current_users
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=policies[1].resource_id,
                current_user=current_admin_user,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_for_wrong_resource_type(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    register_many_protected_resources,
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        try:
            # await policy_crud.read_by_resource(
            await policy_crud.read(
                resource_id=policies[1].resource_id,
                resource_type="wrong_resource_type",
                current_user=current_admin_user,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_read_access_policy_by_identity_and_resource(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy by identity and resource."""
    register_many_protected_resources,
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        # read_policy = await policy_crud.read_by_identity_and_resource(
        read_policy = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            current_user=current_admin_user,
        )

    assert len(read_policy) == 1

    assert int(read_policy[0].id)
    assert read_policy[0].identity_id == policies[2].identity_id
    assert read_policy[0].resource_id == policies[2].resource_id
    assert read_policy[0].action == policies[2].action


@pytest.mark.anyio
async def test_read_access_policy_by_identity_and_resource_and_action(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy by identity and resource."""
    register_many_protected_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            action=policies[2].action,
            current_user=current_admin_user,
        )

    assert len(read_policy) == 1

    assert int(read_policy[0].id)
    assert read_policy[0].identity_id == policies[2].identity_id
    assert read_policy[0].resource_id == policies[2].resource_id
    assert read_policy[0].action == policies[2].action


# TBD: implement tests for change method


@pytest.mark.anyio
async def test_admin_deletes_access_policy(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_protected_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    # TBD: this should only be possible for admin or owner

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policy = policies[2]
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(
            access_policy=delete_policy,
            current_user=current_admin_user,
        )

    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.read(
                resource_id=policies[2].resource_id,
                identity_id=policies[2].identity_id,
                action=policies[2].action,
                current_user=current_admin_user,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies) - 1


@pytest.mark.anyio
async def test_user_deletes_access_policy_with_owner_rights(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_protected_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    # TBD: this should only be possible for admin or owner

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policy = policies[2]  # write access for user3 to resource2
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(
            access_policy=delete_policy,
            current_user=CurrentUserData(
                **current_user_data_user1
            ),  # policy2 gives user1 own access to resource2
        )

    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.read(
                resource_id=policies[2].resource_id,
                identity_id=policies[2].identity_id,
                action=policies[2].action,
                current_user=current_admin_user,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies) - 1


@pytest.mark.anyio
async def test_user_deletes_access_policy_without_owner_rights(
    register_many_protected_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_protected_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    # TBD: this should only be possible for admin or owner

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policy = policies[2]  # write access for user3 to resource2
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(
            access_policy=delete_policy,
            current_user=CurrentUserData(
                **current_user_data_user2
            ),  # no policy gives user2 own access to resource2
        )

    # read the specific policy to check if it still exists
    async with AccessPolicyCRUD() as policy_crud:
        policy2_still_exists = await policy_crud.read(
            resource_id=policies[2].resource_id,
            identity_id=policies[2].identity_id,
            action=policies[2].action,
            current_user=current_admin_user,
        )
        assert policy2_still_exists[0] == policies[2]

    # read all policies to check if the number of policies is still the same
    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies)


# endregion AccessPolicy CRUD tests

# region AccessLogging CRUD tests


@pytest.mark.anyio
async def test_create_access_log(
    register_many_current_users, register_many_protected_resources
):
    """Test creating an access log."""
    current_user = register_many_current_users[1]
    resource2_id = register_many_protected_resources[1]
    # TBD: add test logs to utils
    access_log = AccessLogCreate(
        identity_id=str(current_user.user_id),
        resource_id=resource2_id,
        action=Action.read,
        status_code=200,
    )

    async with AccessLoggingCRUD() as logging_crud:
        created_log = await logging_crud.log_access(access_log)

    # assert created_log.id is not None
    assert int(created_log.id)
    assert created_log.identity_id == access_log.identity_id
    assert created_log.resource_id == access_log.resource_id
    assert created_log.action == access_log.action
    assert created_log.status_code == access_log.status_code


@pytest.mark.anyio
async def test_read_access_log_for_resource_type(
    register_many_current_users, register_many_protected_resources
):
    """Test reading an access log for resource."""
    current_user = register_many_current_users[1]
    resource_id3 = register_many_protected_resources[3]

    access_log = AccessLogCreate(
        identity_id=str(current_user.user_id),
        resource_id=resource_id3,
        action=Action.read,
        status_code=200,
    )

    time_before = datetime.now()
    async with AccessLoggingCRUD() as logging_crud:
        await logging_crud.log_access(access_log)
    time_after = datetime.now()

    async with AccessLoggingCRUD() as crud:
        identity_log = await crud.read_log_by_identity_id(
            current_user_data_user1["user_id"]
        )
        resource_log = await crud.read_log_by_resource(
            resource_id3,
            "ProtectedResource",
        )
    assert len(identity_log) == 1
    assert int(identity_log.id)
    assert identity_log[0].resource_id == access_log.resource_id
    assert identity_log[0].identity_id == uuid.UUID(current_user_data_user1["user_id"])
    assert identity_log[0].action == access_log.action
    assert identity_log[0].status_code == access_log.status_code
    assert identity_log[0].time >= time_before - timedelta(seconds=25)
    assert identity_log[0].time <= time_after + timedelta(seconds=25)

    # TBD: move the double checking to the tests for access control in crud access tests:
    assert resource_log[0].id == identity_log[0].id
    assert resource_log[0].resource_id == identity_log[0].resource_id
    assert resource_log[0].identity_id == identity_log[0].identity_id
    assert resource_log[0].status_code == identity_log[0].status_code
    assert resource_log[0].action == identity_log[0].action
    assert resource_log[0].time == identity_log[0].time


# endregion AccessLogging CRUD tests
