import pytest
from uuid import UUID

from core.types import Action
from crud.access import AccessPolicyCRUD

from tests.utils import one_test_policy, many_test_policies


# effectively tests the AccessPolicyCRUD create method:
@pytest.mark.anyio
async def test_create_access_policy():
    """Test creating an access policy."""

    policy_crud = AccessPolicyCRUD()
    created_policy = await policy_crud.create(one_test_policy)
    policy_in_db = created_policy.model_dump()
    assert policy_in_db["identity_id"] == UUID(one_test_policy["identity_id"])
    assert policy_in_db["identity_type"] == one_test_policy["identity_type"]
    assert policy_in_db["resource_id"] == one_test_policy["resource_id"]
    assert policy_in_db["resource_type"] == one_test_policy["resource_type"]
    assert policy_in_db["action"] == Action(one_test_policy["action"])
