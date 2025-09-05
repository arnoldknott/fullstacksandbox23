import uuid
from pprint import pprint

import pytest

from core.types import Action, CurrentUserData, IdentityType, ResourceType
from crud.access import (
    AccessLoggingCRUD,
    AccessPolicyCRUD,
    IdentityHierarchyCRUD,
    ResourceHierarchyCRUD,
)
from models.access import (
    AccessLogCreate,
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessPolicyUpdate,
)
from models.protected_resource import ProtectedResource
from tests.utils import (
    child_identity_id1,
    child_identity_id4,
    child_identity_id5,
    child_identity_id9,
    child_resource_id1,
    child_resource_id2,
    child_resource_id4,
    child_resource_id7,
    child_resource_id8,
    child_resource_id10,
    current_user_data_admin,
    current_user_data_user1,
    current_user_data_user2,
    current_user_data_user3,
    identity_id_group1,
    identity_id_group2,
    identity_id_group3,
    identity_id_user1,
    identity_id_user2,
    many_resource_ids,
    many_test_child_identities,
    many_test_child_resource_entities,
    many_test_policies,
    one_test_policy_own,
    one_test_policy_public_read,
    one_test_policy_read,
    one_test_policy_share,
    one_test_policy_write,
    resource_id1,
    resource_id2,
    resource_id3,
    resource_id7,
    resource_id9,
    resource_id10,
    user_id_nonexistent,
)

# region AccessPolicy CRUD tests


@pytest.mark.anyio
async def test_admin_creates_access_policy(
    register_current_user, register_one_resource
):
    """Test creating an access policy."""

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
    add_one_test_access_policy,
):
    """Test creating an access policy."""

    # users need to be registered for the policies to be created:
    sharing_user = await register_current_user(current_user_data_user1)
    await register_current_user(current_user_data_user3)

    # Admin needs to register the first resource - owned by user 1:
    current_admin_user = await register_current_user(current_user_data_admin)
    await add_one_test_access_policy(one_test_policy_own, current_admin_user)

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
async def test_reader_creates_access_policy_fails(
    register_current_user,
    add_one_test_access_policy,
):
    """Test creating an access policy."""

    # users need to be registered for the policies to be created:
    sharing_user = await register_current_user(current_user_data_user1)
    await register_current_user(current_user_data_user3)

    # # resources need to be registered for the policies to be created:
    # policy = AccessPolicy(**one_test_policy_share)

    # Admin needs to register the first resource - owned by user 1:
    current_admin_user = await register_current_user(current_user_data_admin)
    await add_one_test_access_policy(one_test_policy_read, current_admin_user)

    try:
        # User 1 (with read-only permissions) tries to share with user 3:
        async with AccessPolicyCRUD() as policy_crud:
            policy = AccessPolicy(**one_test_policy_share)
            await policy_crud.create(policy, sharing_user)
    except Exception as err:
        assert err.status_code == 403
        assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_writer_creates_access_policy_fails(
    register_current_user,
    add_one_test_access_policy,
):
    """Test creating an access policy."""

    # users need to be registered for the policies to be created:
    sharing_user = await register_current_user(current_user_data_user1)
    await register_current_user(current_user_data_user3)

    # # resources need to be registered for the policies to be created:
    # policy = AccessPolicy(**one_test_policy_share)

    # Admin needs to register the first resource - owned by user 1:
    current_admin_user = await register_current_user(current_user_data_admin)
    await add_one_test_access_policy(one_test_policy_write, current_admin_user)

    try:
        # User 1 (with read-only permissions) tries to share with user 3:
        async with AccessPolicyCRUD() as policy_crud:
            policy = AccessPolicy(**one_test_policy_share)
            await policy_crud.create(policy, sharing_user)
    except Exception as err:
        assert err.status_code == 403
        assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_prevent_create_duplicate_access_policy(
    register_many_current_users,
    register_many_resources,
    add_many_test_access_policies,
):
    """Test preventing the creation of a duplicate access policy."""

    current_users = register_many_current_users
    register_many_resources

    add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        try:
            policy = await policy_crud.create(many_test_policies[2], current_users[0])
            print(policy)
        except Exception as err:
            assert err.status_code == 409
            assert (
                err.detail
                == "Access policy for identity and resource already exists. Update instead of create."
            )
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_create_access_policy_for_public_resource(
    register_current_user, register_many_resources
):
    """Test preventing the creation of a duplicate access policy."""

    current_admin_user = await register_current_user(current_user_data_admin)
    register_many_resources

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


# TBD: implement tests for filters_allowed and allowed methods - or leave this to the read / delete?


@pytest.mark.anyio
async def test_admin_read_access_policy_by_resource(
    register_many_current_users,
    register_many_resources,
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    current_admin_user = register_many_current_users[0]
    register_many_resources

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
    register_many_resources,
    add_many_test_access_policies,
):
    """Test user reading an access policy by id."""

    (register_many_resources,)
    policies = add_many_test_access_policies
    current_user1 = register_many_current_users[1]

    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            resource_id=policies[1].resource_id, current_user=current_user1
        )

    print("=== read_policy ===")
    pprint(read_policy)

    assert int(read_policy[0].id)
    assert read_policy[0].identity_id == policies[1].identity_id
    assert read_policy[0].resource_id == policies[1].resource_id
    assert read_policy[0].action == policies[1].action


# TBD: change to resource_id / identity_id or delete?
@pytest.mark.anyio
async def test_read_access_policy_by_id_without_permission(
    register_many_current_users,
    register_many_resources,
    add_many_test_access_policies,
):
    """Test reading an access policy by id without permission."""
    (register_many_current_users,)
    register_many_resources
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        result = await policy_crud.read(resource_id=policies[2].resource_id)
        assert result == []


# TBD: implement tests for filters_allowed logic:
# - public resource


@pytest.mark.anyio
async def test_read_access_policy_for_nonexisting_resource_id(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy by id."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        result = await policy_crud.read(
            resource_id=uuid.uuid4(),
            current_user=current_admin_user,
        )
        assert result == []


@pytest.mark.anyio
async def test_read_access_policy_by_identity(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading multiple access policies for a given identity."""
    register_many_resources
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
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy for an identity, that does not exist."""
    (register_many_resources,)
    current_admin_user = register_many_current_users[0]
    (add_many_test_access_policies,)
    async with AccessPolicyCRUD() as policy_crud:
        result = await policy_crud.read(
            identity_id=uuid.UUID(user_id_nonexistent),
            current_user=current_admin_user,
        )
        assert result == []


@pytest.mark.anyio
async def test_read_access_policy_by_resource_missing_resource_type(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    register_many_resources
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
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy for a given resource."""
    (register_many_resources,)
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    async with AccessPolicyCRUD() as policy_crud:
        result = await policy_crud.read(
            resource_id=policies[1].resource_id,
            resource_type="wrong_resource_type",
            current_user=current_admin_user,
        )
        assert result == []


@pytest.mark.anyio
async def test_read_access_policy_by_identity_and_resource(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy by identity and resource."""
    (register_many_resources,)
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
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test reading an access policy by identity and resource."""
    register_many_resources
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


@pytest.mark.anyio
async def test_admin_changes_access_policy_from_write_to_own(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test updating an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    update_policy = AccessPolicyUpdate(
        **policies[2].model_dump(), new_action=Action.own
    )
    async with AccessPolicyCRUD() as policy_crud:
        updated_policy = await policy_crud.update(
            access_policy=update_policy,
            current_user=current_admin_user,
        )

    assert int(updated_policy.id)
    assert int(updated_policy.id) == policies[2].id
    assert updated_policy.identity_id == policies[2].identity_id
    assert updated_policy.resource_id == policies[2].resource_id
    assert updated_policy.action == Action.own

    async with AccessPolicyCRUD() as policy_crud:
        result = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            action=Action.write,
            current_user=current_admin_user,
        )
        assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            action=Action.own,
            current_user=current_admin_user,
        )

    assert updated_policy == read_policy[0]


@pytest.mark.anyio
async def test_owner_user_changes_access_policy_from_write_to_own(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test updating an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    update_policy = AccessPolicyUpdate(
        **policies[2].model_dump(), new_action=Action.own
    )
    async with AccessPolicyCRUD() as policy_crud:
        updated_policy = await policy_crud.update(
            access_policy=update_policy,
            current_user=CurrentUserData(**current_user_data_user1),
        )

    assert int(updated_policy.id)
    assert int(updated_policy.id) == policies[2].id
    assert updated_policy.identity_id == policies[2].identity_id
    assert updated_policy.resource_id == policies[2].resource_id
    assert updated_policy.action == Action.own

    async with AccessPolicyCRUD() as policy_crud:
        result = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            action=Action.write,
            current_user=current_admin_user,
        )
        assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            action=Action.own,
            current_user=current_admin_user,
        )

    assert updated_policy == read_policy[0]


@pytest.mark.anyio
async def test_owner_user_creates_new_access_policy_through_update(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test updating an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    add_many_test_access_policies
    create_policy = AccessPolicyUpdate(
        identity_id=identity_id_user2, resource_id=resource_id2, new_action=Action.write
    )
    del create_policy.action
    async with AccessPolicyCRUD() as policy_crud:
        created_policy = await policy_crud.update(
            access_policy=create_policy,
            current_user=CurrentUserData(**current_user_data_user1),
        )

    assert int(created_policy.id)
    assert created_policy.identity_id == uuid.UUID(identity_id_user2)
    assert created_policy.resource_id == uuid.UUID(resource_id2)
    assert created_policy.action == Action.write

    async with AccessPolicyCRUD() as policy_crud:
        read_policy = await policy_crud.read(
            identity_id=identity_id_user2,
            resource_id=resource_id2,
            action=Action.write,
            current_user=current_admin_user,
        )

    assert created_policy == read_policy[0]


@pytest.mark.anyio
async def test_user_fails_to_create_new_access_policy_through_update_missing_access(
    register_many_resources,
    register_many_current_users,
):
    """Test updating an access policy."""
    register_many_resources
    register_many_current_users
    create_policy = AccessPolicyUpdate(
        identity_id=identity_id_user2, resource_id=resource_id2, new_action=Action.write
    )
    del create_policy.action
    try:
        async with AccessPolicyCRUD() as policy_crud:
            await policy_crud.update(
                access_policy=create_policy,
                current_user=CurrentUserData(**current_user_data_user1),
            )
    except Exception as err:
        assert err.status_code == 404
        assert str(err.detail) == "Access policy not found."
    else:
        pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_non_owner_user_tries_to_change_access_policy_from_write_to_own(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test updating an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies
    update_policy = AccessPolicyUpdate(
        **policies[2].model_dump(), new_action=Action.own
    )
    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.update(
                access_policy=update_policy,
                current_user=CurrentUserData(**current_user_data_user2),
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")

    async with AccessPolicyCRUD() as policy_crud:
        old_policy_still_in_place = await policy_crud.read(
            identity_id=policies[2].identity_id,
            resource_id=policies[2].resource_id,
            action=Action.write,
            current_user=current_admin_user,
        )

    assert int(old_policy_still_in_place[0].id) == int(policies[2].id)
    assert old_policy_still_in_place[0].identity_id == policies[2].identity_id
    assert old_policy_still_in_place[0].resource_id == policies[2].resource_id
    assert old_policy_still_in_place[0].action == policies[2].action


@pytest.mark.anyio
async def test_admin_deletes_access_policy(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

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
        result = await policy_crud.read(
            resource_id=policies[2].resource_id,
            identity_id=policies[2].identity_id,
            action=policies[2].action,
            current_user=current_admin_user,
        )
        assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies) - 1


@pytest.mark.anyio
async def test_admin_deletes_all_access_policies_for_a_resource(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policies = AccessPolicyDelete(resource_id=resource_id1)
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(
            access_policy=delete_policies,
            current_user=current_admin_user,
        )

    expected_deletion = [
        policies[0],
        policies[5],
        policies[9],
    ]
    async with AccessPolicyCRUD() as policy_crud:
        for policy in expected_deletion:
            result = await policy_crud.read(
                resource_id=policy.resource_id,
                identity_id=policy.identity_id,
                action=policy.action,
                current_user=current_admin_user,
            )
            assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == 7

    assert all_policies_after_deletion[0] == policies[1]
    assert all_policies_after_deletion[1] == policies[2]
    assert all_policies_after_deletion[2] == policies[3]
    assert all_policies_after_deletion[3] == policies[4]
    assert all_policies_after_deletion[4] == policies[6]
    assert all_policies_after_deletion[5] == policies[7]
    assert all_policies_after_deletion[6] == policies[8]


@pytest.mark.anyio
async def test_admin_deletes_all_access_policies_for_an_identity(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policies = AccessPolicyDelete(identity_id=identity_id_user1)
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(
            access_policy=delete_policies,
            current_user=current_admin_user,
        )

    expected_deletion = [
        policies[1],
        policies[5],
        policies[6],
        policies[7],
    ]
    async with AccessPolicyCRUD() as policy_crud:
        for policy in expected_deletion:
            result = await policy_crud.read(
                resource_id=policy.resource_id,
                identity_id=policy.identity_id,
                action=policy.action,
                current_user=current_admin_user,
            )
            assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == 6

    assert all_policies_after_deletion[0] == policies[0]
    assert all_policies_after_deletion[1] == policies[2]
    assert all_policies_after_deletion[2] == policies[3]
    assert all_policies_after_deletion[3] == policies[4]
    assert all_policies_after_deletion[4] == policies[8]
    assert all_policies_after_deletion[5] == policies[9]


@pytest.mark.anyio
async def test_user_deletes_all_access_policies_for_a_resource_with_owner_rights(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policies = AccessPolicyDelete(resource_id=resource_id1)
    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.delete(
            access_policy=delete_policies,
            current_user=CurrentUserData(**current_user_data_user2),
        )

    expected_deletion = [
        policies[0],
        policies[5],
        policies[9],
    ]
    async with AccessPolicyCRUD() as policy_crud:
        for policy in expected_deletion:
            result = await policy_crud.read(
                resource_id=policy.resource_id,
                identity_id=policy.identity_id,
                action=policy.action,
                current_user=current_admin_user,
            )
            assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == 7

    assert all_policies_after_deletion[0] == policies[1]
    assert all_policies_after_deletion[1] == policies[2]
    assert all_policies_after_deletion[2] == policies[3]
    assert all_policies_after_deletion[3] == policies[4]
    assert all_policies_after_deletion[4] == policies[6]
    assert all_policies_after_deletion[5] == policies[7]
    assert all_policies_after_deletion[6] == policies[8]


@pytest.mark.anyio
async def test_admin_tries_to_delete_all_public_access_policies(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    async with AccessPolicyCRUD() as policy_crud:
        try:
            delete_policies = AccessPolicyDelete(public=True)
            await policy_crud.delete(
                access_policy=delete_policies,
                current_user=current_admin_user,
            )
        except Exception as err:
            assert (
                "Value error, Only one public resource can be deleted at a time."
                in str(err)
            )
        else:
            pytest.fail("No Value error raised!")

    # read all policies to check if the number of policies is still the same
    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies)


@pytest.mark.anyio
async def test_admin_tries_to_delete_all_own_access_policies(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    async with AccessPolicyCRUD() as policy_crud:
        try:
            delete_policies = AccessPolicyDelete(Action=Action.own)
            await policy_crud.delete(
                access_policy=delete_policies,
                current_user=current_admin_user,
            )
        except Exception as err:
            print("=== error ===")
            pprint(err)
            assert (
                "Either resource_id or identity_id required when deleting policies."
                in str(err)
            )
        else:
            pytest.fail("No Value error raised!")

    # read all policies to check if the number of policies is still the same
    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies)


@pytest.mark.anyio
async def test_admin_tries_to_delete_all_write_access_policies(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    async with AccessPolicyCRUD() as policy_crud:
        try:
            delete_policies = AccessPolicyDelete(Action=Action.write)
            await policy_crud.delete(
                access_policy=delete_policies,
                current_user=current_admin_user,
            )
        except Exception as err:
            print("=== error ===")
            pprint(err)
            assert (
                "Either resource_id or identity_id required when deleting policies."
                in str(err)
            )
        else:
            pytest.fail("No Value error raised!")

    # read all policies to check if the number of policies is still the same
    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies)


@pytest.mark.anyio
async def test_admin_tries_to_delete_all_read_access_policies(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    async with AccessPolicyCRUD() as policy_crud:
        try:
            delete_policies = AccessPolicyDelete(Action=Action.read)
            await policy_crud.delete(
                access_policy=delete_policies,
                current_user=current_admin_user,
            )
        except Exception as err:
            print("=== error ===")
            pprint(err)
            assert (
                "Either resource_id or identity_id required when deleting policies."
                in str(err)
            )
        else:
            pytest.fail("No Value error raised!")

    # read all policies to check if the number of policies is still the same
    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies)


@pytest.mark.anyio
async def test_user_deletes_all_access_policies_for_a_resource_without_owner_rights(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policies = AccessPolicyDelete(resource_id=resource_id2)
    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.delete(
                access_policy=delete_policies,
                current_user=CurrentUserData(**current_user_data_user3),
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")

    # read all policies to check if the number of policies is still the same
    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies)


@pytest.mark.anyio
async def test_user_deletes_access_policy_with_owner_rights(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

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
        result = await policy_crud.read(
            resource_id=policies[2].resource_id,
            identity_id=policies[2].identity_id,
            action=policies[2].action,
            current_user=current_admin_user,
        )
        assert result == []

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_after_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_after_deletion) == len(policies) - 1


@pytest.mark.anyio
async def test_user_deletes_access_policy_without_owner_rights(
    register_many_resources,
    register_many_current_users,
    add_many_test_access_policies,
):
    """Test deleting an access policy."""
    register_many_resources
    current_admin_user = register_many_current_users[0]
    policies = add_many_test_access_policies

    async with AccessPolicyCRUD() as policy_crud:
        all_policies_before_deletion = await policy_crud.read(
            current_user=current_admin_user
        )

    assert len(all_policies_before_deletion) == len(policies)

    delete_policy = policies[2]  # write access for user3 to resource2
    async with AccessPolicyCRUD() as policy_crud:
        try:
            await policy_crud.delete(
                access_policy=delete_policy,
                current_user=CurrentUserData(
                    **current_user_data_user2
                ),  # no policy gives user2 own access to resource2
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Access policy not found."
        else:
            pytest.fail("No HTTPexception raised!")

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
async def test_create_access_log(register_many_current_users, register_many_resources):
    """Test creating an access log."""
    current_user = register_many_current_users[1]
    resource2_id = register_many_resources[1]
    access_log = AccessLogCreate(
        identity_id=str(current_user.user_id),
        resource_id=resource2_id,
        action=Action.read,
        status_code=200,
    )

    async with AccessLoggingCRUD() as logging_crud:
        created_log = await logging_crud.create(access_log)

    assert int(created_log.id)
    assert created_log.identity_id == access_log.identity_id
    assert created_log.resource_id == access_log.resource_id
    assert created_log.action == access_log.action
    assert created_log.status_code == access_log.status_code


# TBD: check if the rest is covered through test_access.py!

# endregion AccessLogging CRUD tests

# region ResourceHierarchy CRUD tests


@pytest.mark.anyio
async def test_admin_create_resource_hierarchy(
    register_many_resources,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    resources = register_many_resources
    new_child_id = uuid.uuid4()

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        created_hierarchy = await hierarchy_crud.create(
            current_user=current_admin_user,
            parent_id=resources[0],
            child_type=ResourceType.protected_child,
            child_id=new_child_id,
        )

    assert created_hierarchy.parent_id == uuid.UUID(resources[0])
    assert created_hierarchy.child_id == new_child_id
    assert created_hierarchy.inherit is False
    assert created_hierarchy.order == 1


@pytest.mark.anyio
async def test_admin_create_resource_hierarchy_with_inheritance(
    register_many_resources,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    resources = register_many_resources
    new_child_id = uuid.uuid4()

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        created_hierarchy = await hierarchy_crud.create(
            current_user=current_admin_user,
            parent_id=resources[0],
            child_type=ResourceType.protected_child,
            child_id=new_child_id,
            inherit=True,
        )

    assert created_hierarchy.parent_id == uuid.UUID(resources[0])
    assert created_hierarchy.child_id == new_child_id
    assert created_hierarchy.inherit is True
    assert created_hierarchy.order == 1


@pytest.mark.anyio
async def test_admin_create_resource_hierarchy_with_not_allowed_child_type(
    register_many_resources,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    resources = register_many_resources
    new_child_id = uuid.uuid4()

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_admin_user,
                parent_id=resources[0],
                child_type=ResourceType.demo_resource,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_admin_create_resource_hierarchy_parent_is_child_to_itself(
    register_many_resources,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    resources = register_many_resources

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_admin_user,
                parent_id=resources[0],
                child_type=ResourceType.protected_child,
                child_id=resources[0],
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_admin_create_resource_hierarchy_with_nonexisting_parent(
    register_many_resources,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    register_many_resources
    new_child_id = uuid.uuid4()

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_admin_user,
                parent_id=uuid.uuid4(),
                child_type=ResourceType.protected_child,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_user_create_resource_hierarchy(
    register_current_user, add_many_test_access_policies, add_one_test_access_policy
):
    """Test creating a resource hierarchy."""
    current_user_data = await register_current_user(current_user_data_user1)
    access_policies = add_many_test_access_policies

    new_child_id = uuid.uuid4()

    await add_one_test_access_policy(
        {
            "identity_id": current_user_data.user_id,
            "resource_id": str(new_child_id),
            "action": Action.own,
        }
    )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        created_hierarchy = await hierarchy_crud.create(
            current_user=current_user_data,
            parent_id=uuid.UUID(resource_id2),
            child_type=ResourceType.protected_child,
            child_id=new_child_id,
        )

    assert created_hierarchy.parent_id == access_policies[1].resource_id
    assert created_hierarchy.child_id == new_child_id
    assert created_hierarchy.inherit is False


@pytest.mark.anyio
async def test_user_create_resource_hierarchy_without_access(
    register_current_user, add_many_test_access_policies
):
    """Test creating a resource hierarchy."""
    current_user_data = await register_current_user(current_user_data_user1)
    new_child_id = uuid.uuid4()

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_user_data,
                parent_id=uuid.UUID(resource_id3),
                child_type=ResourceType.protected_child,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_user_create_resource_hierarchy_without_access_to_child(
    register_current_user, add_many_test_access_policies
):
    """Test creating a resource hierarchy."""
    current_user_data = await register_current_user(current_user_data_user1)
    add_many_test_access_policies

    new_child_id = uuid.uuid4()

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_user_data,
                parent_id=uuid.UUID(resource_id3),
                child_type=ResourceType.protected_child,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_admin_reads_resource_hierarchy_single_child_of_a_parent(
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)
    new_child_id = uuid.uuid4()
    relationship = await add_one_parent_child_resource_relationship(new_child_id)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user,
            parent_id=relationship.parent_id,
        )

    assert len(read_relation) == 1
    assert read_relation[0].child_id == new_child_id
    assert read_relation[0].parent_id == relationship.parent_id
    assert read_relation[0].inherit == relationship.inherit
    assert "order" not in read_relation[0]


@pytest.mark.anyio
async def test_admin_reads_resource_hierarchy_multiple_children_of_a_parent(
    add_many_parent_child_resource_relationships,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user, parent_id=resource_id3
        )

    assert len(read_relation) == 10
    for relation, expected in zip(read_relation, many_test_child_resource_entities):
        assert relation.parent_id == uuid.UUID(resource_id3)
        assert relation.child_id == uuid.UUID(expected["id"])
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_resource_hierarchy_all_allowed_children_of_a_parent(
    add_many_parent_child_resource_relationships,
    register_current_user,
    add_many_test_access_policies,
    add_one_test_access_policy,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)

    access_to_children_ids = [
        child_resource_id1,
        child_resource_id2,
        child_resource_id4,
        child_resource_id7,
        child_resource_id8,
        child_resource_id10,
    ]
    for child_id in access_to_children_ids:
        await add_one_test_access_policy(
            {
                "identity_id": current_user.user_id,
                "resource_id": child_id,
                "action": Action.read,
            },
        )

    # async with AccessPolicyCRUD() as policy_crud:
    #     policies = await policy_crud.read(
    #         current_user=CurrentUserData(**current_user_data_admin),
    #         # current_user=current_user,
    #     )
    #     print("=== policies ===")
    #     pprint(policies)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_user, parent_id=resource_id3
        )

    assert len(read_relation) == 6
    for relation, expected_child_id in zip(read_relation, access_to_children_ids):
        assert relation.parent_id == uuid.UUID(resource_id3)
        assert relation.child_id == uuid.UUID(expected_child_id)
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_resource_hierarchy_all_children_of_a_parent_without_parent_access(
    add_many_parent_child_resource_relationships,
    register_current_user,
    add_many_test_access_policies,
):
    """Test reading all children of a parent resource."""
    current_user_data = await register_current_user(current_user_data_user2)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user_data, parent_id=resource_id3
        )
        assert result == []


@pytest.mark.anyio
async def test_admin_reads_resource_hierarchy_all_relationships(
    add_many_parent_child_resource_relationships,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.read(current_user=current_admin_user)
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Hierarchy not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_admin_reads_resource_hierarchy_single_parent_of_child(
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)
    child_id = uuid.uuid4()
    relationship = await add_one_parent_child_resource_relationship(child_id)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user,
            child_id=relationship.child_id,
        )

    assert len(read_relation) == 1
    assert read_relation[0].child_id == child_id
    assert read_relation[0].parent_id == relationship.parent_id
    assert read_relation[0].inherit == relationship.inherit
    assert "order" not in read_relation[0]


@pytest.mark.anyio
async def test_admin_reads_resource_hierarchy_multiple_parents_of_a_child(
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)
    child_id = uuid.uuid4()
    for parent in many_resource_ids:
        await add_one_parent_child_resource_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user, child_id=child_id
        )

    assert len(read_relation) == 10
    for relation, expected_parent_id in zip(read_relation, many_resource_ids):
        assert relation.parent_id == uuid.UUID(expected_parent_id)
        assert relation.child_id == child_id
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_resource_hierarchy_all_allowed_parents_of_a_child(
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)
    child_id = uuid.uuid4()
    access_to_parent_ids = [
        resource_id3,
        resource_id7,
        resource_id9,
        resource_id10,
    ]

    for parent_id in access_to_parent_ids:
        await add_one_test_access_policy(
            {
                "identity_id": current_user.user_id,
                "resource_id": parent_id,
                "action": Action.read,
            },
        )

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": str(child_id),
            "action": Action.read,
        },
    )
    for parent in many_resource_ids:
        await add_one_parent_child_resource_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_user, child_id=child_id
        )

    assert len(read_relation) == 4
    for relation, expected_parent_id in zip(read_relation, access_to_parent_ids):
        assert relation.parent_id == uuid.UUID(expected_parent_id)
        assert relation.child_id == child_id
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_resource_hierarchy_all_allowed_parents_without_access_to_child(
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)
    child_id = uuid.uuid4()
    access_to_parent_ids = [
        resource_id3,
        resource_id7,
        resource_id9,
        resource_id10,
    ]

    for parent_id in access_to_parent_ids:
        await add_one_test_access_policy(
            {
                "identity_id": current_user.user_id,
                "resource_id": parent_id,
                "action": Action.read,
            },
        )
    for parent in many_resource_ids:
        await add_one_parent_child_resource_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(current_user=current_user, child_id=child_id)
        assert result == []


@pytest.mark.anyio
async def test_user_reads_resource_hierarchy_all_allowed_parents_without_access_to_parents(
    add_one_test_access_policy,
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)
    child_id = uuid.uuid4()

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": str(child_id),
            "action": Action.read,
        },
    )
    for parent in many_resource_ids:
        await add_one_parent_child_resource_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(current_user=current_user, child_id=child_id)
        assert result == []


@pytest.mark.anyio
async def test_user_reads_resource_hierarchy_all_parents_of_a_child_without_access(
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user_data = await register_current_user(current_user_data_user2)
    child_id = uuid.uuid4()
    for parent in many_resource_ids:
        await add_one_parent_child_resource_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user_data, child_id=child_id
        )
        assert result == []


@pytest.mark.anyio
async def test_admin_deletes_resource_hierarchy_child(
    add_one_parent_child_resource_relationship,
    register_current_user,
):
    """Test deleting a child."""
    current_admin_user = await register_current_user(current_user_data_admin)
    child_id = uuid.uuid4()
    relationship = await add_one_parent_child_resource_relationship(child_id)

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        await hierarchy_crud.delete(
            current_user=current_admin_user,
            parent_id=relationship.parent_id,
            child_id=relationship.child_id,
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_admin_user, child_id=child_id
        )
        assert result == []


@pytest.mark.anyio
async def test_user_deletes_resource_hierarchy_child_with_owner_rights(
    add_many_parent_child_resource_relationships,
    register_current_user,
    add_one_test_access_policy,
):
    """Test deleting a child."""
    current_user = await register_current_user(current_user_data_user1)
    add_many_parent_child_resource_relationships

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": child_resource_id8,
            "action": Action.own,
        },
    )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        await hierarchy_crud.delete(
            current_user=current_user,
            parent_id=resource_id3,
            child_id=child_resource_id8,
        )

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user, child_id=child_resource_id8
        )
        assert result == []


@pytest.mark.anyio
async def test_user_deletes_resource_hierarchy_child_without_owner_rights(
    add_many_parent_child_resource_relationships,
    register_current_user,
    add_one_test_access_policy,
):
    """Test deleting a child."""
    current_user = await register_current_user(current_user_data_user1)
    add_many_parent_child_resource_relationships

    async with ResourceHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.delete(
                current_user=current_user,
                parent_id=resource_id3,
                child_id=child_resource_id8,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Hierarchy not found."
        else:
            pytest.fail("No HTTPexception raised!")


# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Passing tests:
# ✔︎ admin creates adds a new child to existing parent
# ✔︎ admin creates adds a new child to existing parent with inheritance
# ✔︎ admin creates tries to add a new child with a resource_type that is not allowed as child for the parent
# ✔ admin creates tries to add a child to non-existing parent
# ✔ user creates adds a new child to existing parent with access
# ✔ user creates tries to add a child without owner access to existing parent
# ✔ admin reads single child of one parent
# ✔ admin reads all children of one parent
# ✔ user read returns only allowed children of a parent with read access to parent
# ✔ user tries to read all children of a parent without read access to parent
# ✔ admin reads all relationships (without giving parent_id or child_id) fails
# ✔ admin reads single parent of a child
# ✔ admin reads all parents of a child
# ✔ user read returns only allowed parents of a child with read access to child
# ✔ user tries to read all parents of a child without read access to child
# ✔ user tries to read all parents of a child without read access to parents
# ✔ admin deletes a child
# ✔ user deletes a child with owner access to child
# ✔ user tries to delete a child without owner access to child
# - inheritance of access rights => base CRUD!

# endregion ResourceHierarchy CRUD tests

# region IdentityHierarchy CRUD tests


@pytest.mark.anyio
async def test_admin_create_identity_hierarchy(
    register_many_entities,
    register_current_user,
):
    """Test creating a identity hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    identities = register_many_entities[10:]
    parent_id = identities[1].id
    new_child_id = uuid.uuid4()

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        created_hierarchy = await hierarchy_crud.create(
            current_user=current_admin_user,
            parent_id=parent_id,
            child_type=IdentityType.sub_group,
            child_id=new_child_id,
        )

    assert created_hierarchy.parent_id == parent_id
    assert created_hierarchy.child_id == new_child_id
    assert created_hierarchy.inherit is False


@pytest.mark.anyio
async def test_admin_create_identity_hierarchy_with_inheritance(
    register_many_entities,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    identities = register_many_entities[10:]
    parent_id = identities[1].id
    new_child_id = uuid.uuid4()

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        created_hierarchy = await hierarchy_crud.create(
            current_user=current_admin_user,
            parent_id=parent_id,
            child_type=IdentityType.sub_group,
            child_id=new_child_id,
            inherit=True,
        )

    assert created_hierarchy.parent_id == parent_id
    assert created_hierarchy.child_id == new_child_id
    assert created_hierarchy.inherit is True


@pytest.mark.anyio
async def test_admin_create_identity_hierarchy_with_not_allowed_child_type(
    register_many_entities,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    identities = register_many_entities[10:]
    parent_id = identities[1].id
    new_child_id = uuid.uuid4()

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_admin_user,
                parent_id=parent_id,
                child_type=IdentityType.sub_sub_group,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_admin_create_identity_hierarchy_parent_is_child_to_itself(
    register_many_entities,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    identities = register_many_entities[10:]
    parent_id = identities[1].id

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_admin_user,
                parent_id=parent_id,
                child_type=IdentityType.sub_group,
                child_id=parent_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."


@pytest.mark.anyio
async def test_admin_create_identity_hierarchy_with_nonexisting_parent(
    register_many_entities,
    register_current_user,
):
    """Test creating a resource hierarchy."""
    current_admin_user = await register_current_user(current_user_data_admin)
    register_many_entities[10:]
    new_child_id = uuid.uuid4()

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_admin_user,
                parent_id=uuid.uuid4(),
                child_type=IdentityType.sub_group,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_user_create_identity_hierarchy(
    register_current_user, register_many_entities, add_one_test_access_policy
):
    """Test creating a resource hierarchy."""
    current_user_data = await register_current_user(current_user_data_user1)
    parent_identity = register_many_entities[11]

    await add_one_test_access_policy(
        {
            "identity_id": str(current_user_data.user_id),
            "resource_id": str(parent_identity.id),
            "action": Action.own,
        },
    )

    new_child_id = uuid.uuid4()

    await add_one_test_access_policy(
        {
            "identity_id": current_user_data.user_id,
            "resource_id": str(new_child_id),
            "action": Action.own,
        }
    )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        created_hierarchy = await hierarchy_crud.create(
            current_user=current_user_data,
            parent_id=parent_identity.id,
            child_type=IdentityType.sub_group,
            child_id=new_child_id,
        )

    assert created_hierarchy.parent_id == parent_identity.id
    assert created_hierarchy.child_id == new_child_id
    assert created_hierarchy.inherit is False


@pytest.mark.anyio
async def test_user_create_identity_hierarchy_without_access(
    register_current_user, register_many_entities
):
    """Test creating a resource hierarchy."""
    current_user_data = await register_current_user(current_user_data_user1)
    parent_identity = register_many_entities[11]
    new_child_id = uuid.uuid4()

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_user_data,
                parent_id=parent_identity.id,
                child_type=IdentityType.sub_group,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_user_create_identity_hierarchy_without_access_to_child(
    register_current_user, register_many_entities, add_one_test_access_policy
):
    """Test creating a resource hierarchy."""
    current_user_data = await register_current_user(current_user_data_user1)
    parent_identity = register_many_entities[11]

    await add_one_test_access_policy(
        {
            "identity_id": str(current_user_data.user_id),
            "resource_id": str(parent_identity.id),
            "action": Action.own,
        },
    )

    new_child_id = uuid.uuid4()

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.create(
                current_user=current_user_data,
                parent_id=parent_identity.id,
                child_type=IdentityType.sub_group,
                child_id=new_child_id,
            )
        except Exception as err:
            assert err.status_code == 403
            assert err.detail == "Forbidden."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_admin_reads_identity_hierarchy_single_child_of_a_parent(
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent identity."""
    current_admin_user = await register_current_user(current_user_data_admin)
    new_child_id = uuid.uuid4()
    relationship = await add_one_parent_child_identity_relationship(new_child_id)

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user,
            parent_id=relationship.parent_id,
        )

    assert len(read_relation) == 1
    assert read_relation[0].child_id == new_child_id
    assert read_relation[0].parent_id == relationship.parent_id
    assert read_relation[0].inherit == relationship.inherit


@pytest.mark.anyio
async def test_admin_reads_identity_hierarchy_multiple_children_of_a_parent(
    add_many_parent_child_identity_relationships,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user, parent_id=identity_id_group2
        )

    expected_children = [
        many_test_child_identities[0],
        many_test_child_identities[3],
        many_test_child_identities[4],
        many_test_child_identities[8],
    ]

    assert len(read_relation) == 4
    for relation, expected in zip(read_relation, expected_children):
        assert relation.parent_id == uuid.UUID(identity_id_group2)
        assert relation.child_id == uuid.UUID(expected["id"])
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_identity_hierarchy_all_allowed_children_of_a_parent(
    add_many_parent_child_identity_relationships,
    register_current_user,
    add_one_test_access_policy,
):
    """Test reading all children of a parent identity."""
    current_user = await register_current_user(current_user_data_user3)

    access_to_children_ids = [
        child_identity_id1,
        child_identity_id4,
        child_identity_id5,
        child_identity_id9,
    ]
    for child_id in access_to_children_ids:
        await add_one_test_access_policy(
            {
                "identity_id": current_user.user_id,
                "resource_id": child_id,
                "action": Action.read,
            },
        )
    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": identity_id_group2,
            "action": Action.read,
        },
    )

    async with AccessPolicyCRUD() as policy_crud:
        await policy_crud.read(
            current_user=CurrentUserData(**current_user_data_admin),
            # current_user=current_user,
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_user, parent_id=identity_id_group2
        )

    assert len(read_relation) == 4
    for relation, expected_child_id in zip(read_relation, access_to_children_ids):
        assert relation.parent_id == uuid.UUID(identity_id_group2)
        assert relation.child_id == uuid.UUID(expected_child_id)
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_identity_hierarchy_all_children_of_a_parent_without_parent_access(
    add_many_parent_child_identity_relationships,
    register_current_user,
    add_many_test_access_policies,
):
    """Test reading all children of a parent resource."""
    current_user_data = await register_current_user(current_user_data_user2)

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user_data, parent_id=identity_id_group2
        )
        assert result == []


@pytest.mark.anyio
async def test_admin_reads_identity_hierarchy_all_relationships(
    add_many_parent_child_identity_relationships,
    register_current_user,
):
    """Test reading all children of a parent identity."""
    current_admin_user = await register_current_user(current_user_data_admin)

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.read(current_user=current_admin_user)
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Hierarchy not found."
        else:
            pytest.fail("No HTTPexception raised!")


@pytest.mark.anyio
async def test_admin_reads_identity_hierarchy_single_parent_of_child(
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent identity."""
    current_admin_user = await register_current_user(current_user_data_admin)
    child_id = uuid.uuid4()
    relationship = await add_one_parent_child_identity_relationship(child_id)

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user,
            child_id=relationship.child_id,
        )

    assert len(read_relation) == 1
    assert read_relation[0].child_id == child_id
    assert read_relation[0].parent_id == relationship.parent_id
    assert read_relation[0].inherit == relationship.inherit


@pytest.mark.anyio
async def test_admin_reads_identity_hierarchy_multiple_parents_of_a_child(
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_admin_user = await register_current_user(current_user_data_admin)
    child_id = uuid.uuid4()
    group_ids = [
        identity_id_group1,
        identity_id_group2,
        identity_id_group3,
    ]
    for parent in group_ids:
        await add_one_parent_child_identity_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_admin_user, child_id=child_id
        )

    assert len(read_relation) == 3
    for relation, expected_parent_id in zip(read_relation, group_ids):
        assert relation.parent_id == uuid.UUID(expected_parent_id)
        assert relation.child_id == child_id
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_identity_hierarchy_all_allowed_parents_of_a_child(
    add_one_test_access_policy,
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)
    child_id = uuid.uuid4()
    access_to_parent_ids = [
        identity_id_group1,
        identity_id_group3,
    ]

    for parent_id in access_to_parent_ids:
        await add_one_test_access_policy(
            {
                "identity_id": current_user.user_id,
                "resource_id": parent_id,
                "action": Action.read,
            },
        )

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": str(child_id),
            "action": Action.read,
        },
    )
    for parent in access_to_parent_ids:
        await add_one_parent_child_identity_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        read_relation = await hierarchy_crud.read(
            current_user=current_user, child_id=child_id
        )

    assert len(read_relation) == 2
    for relation, expected_parent_id in zip(read_relation, access_to_parent_ids):
        assert relation.parent_id == uuid.UUID(expected_parent_id)
        assert relation.child_id == child_id
        assert relation.inherit is False


@pytest.mark.anyio
async def test_user_reads_identity_hierarchy_all_allowed_parents_without_access_to_child(
    add_one_test_access_policy,
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)
    child_id = uuid.uuid4()
    access_to_parent_ids = [
        identity_id_group1,
        identity_id_group3,
    ]

    for parent_id in access_to_parent_ids:
        await add_one_test_access_policy(
            {
                "identity_id": current_user.user_id,
                "resource_id": parent_id,
                "action": Action.read,
            },
        )
    for parent in access_to_parent_ids:
        await add_one_parent_child_identity_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(current_user=current_user, child_id=child_id)
        assert result == []


@pytest.mark.anyio
async def test_user_reads_identity_hierarchy_all_allowed_parents_without_access_to_parents(
    add_one_test_access_policy,
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user = await register_current_user(current_user_data_user3)
    child_id = uuid.uuid4()
    parent_ids = [
        identity_id_group1,
        identity_id_group3,
    ]

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": str(child_id),
            "action": Action.read,
        },
    )
    for parent in parent_ids:
        await add_one_parent_child_identity_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(current_user=current_user, child_id=child_id)
    assert result == []


@pytest.mark.anyio
async def test_user_reads_identity_hierarchy_all_parents_of_a_child_without_access(
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test reading all children of a parent resource."""
    current_user_data = await register_current_user(current_user_data_user2)
    child_id = uuid.uuid4()
    parent_ids = [
        identity_id_group1,
        identity_id_group3,
    ]

    for parent in parent_ids:
        await add_one_parent_child_identity_relationship(
            child_id, parent_id=uuid.UUID(parent)
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user_data, child_id=child_id
        )
        assert result == []


@pytest.mark.anyio
async def test_admin_deletes_identity_hierarchy_child(
    add_one_parent_child_identity_relationship,
    register_current_user,
):
    """Test deleting a child."""
    current_admin_user = await register_current_user(current_user_data_admin)
    child_id = uuid.uuid4()
    relationship = await add_one_parent_child_identity_relationship(child_id)

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        await hierarchy_crud.delete(
            current_user=current_admin_user,
            parent_id=relationship.parent_id,
            child_id=relationship.child_id,
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_admin_user, child_id=child_id
        )
        assert result == []


@pytest.mark.anyio
async def test_user_deletes_identity_hierarchy_child_with_owner_rights(
    add_many_parent_child_identity_relationships,
    register_current_user,
    add_one_test_access_policy,
):
    """Test deleting a child."""
    current_user = await register_current_user(current_user_data_user1)
    add_many_parent_child_identity_relationships

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": child_identity_id5,
            "action": Action.own,
        },
    )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        await hierarchy_crud.delete(
            current_user=current_user,
            parent_id=identity_id_group2,
            child_id=child_identity_id5,
        )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user, child_id=child_identity_id5
        )
        assert result == []


@pytest.mark.anyio
async def test_admin_tries_to_delete_identity_hierarchy_without_parent_id_and_child_id(
    add_many_parent_child_identity_relationships,
    register_current_user,
    add_one_test_access_policy,
):
    """Test deleting a child."""
    current_user = await register_current_user(current_user_data_admin)
    add_many_parent_child_identity_relationships

    await add_one_test_access_policy(
        {
            "identity_id": current_user.user_id,
            "resource_id": child_identity_id5,
            "action": Action.own,
        },
    )

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.delete(
                current_user=current_user,
            )
        except Exception as err:
            assert err.status_code == 422
            assert err.detail == "At least one of parent_id and child_id are required."

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        result = await hierarchy_crud.read(
            current_user=current_user, child_id=child_identity_id5
        )
        assert result[0].child_id == uuid.UUID(child_identity_id5)
        assert result[0].parent_id == uuid.UUID(identity_id_group2)


@pytest.mark.anyio
async def test_user_deletes_identity_hierarchy_child_without_owner_rights(
    add_many_parent_child_identity_relationships,
    register_current_user,
    add_one_test_access_policy,
):
    """Test deleting a child."""
    current_user = await register_current_user(current_user_data_user1)
    add_many_parent_child_identity_relationships

    async with IdentityHierarchyCRUD() as hierarchy_crud:
        try:
            await hierarchy_crud.delete(
                current_user=current_user,
                parent_id=identity_id_group2,
                child_id=child_identity_id5,
            )
        except Exception as err:
            assert err.status_code == 404
            assert err.detail == "Hierarchy not found."
        else:
            pytest.fail("No HTTPexception raised!")


# endregion IdentityHierarchy CRUD tests
