import logging

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from core.types import ResourceType, IdentityType
from .base import BaseView
from core.security import get_access_token_payload, CurrentAccessToken
from models.access import AccessPolicy, AccessPolicyCreate, AccessPolicyRead
from crud.access import AccessPolicyCRUD

logger = logging.getLogger(__name__)
router = APIRouter()

access_policy_view = BaseView(AccessPolicyCRUD, AccessPolicy)


@router.post("/policy", status_code=201)
async def post_access_policy(
    access_policy: AccessPolicyCreate,
    token_payload=Depends(get_access_token_payload),
) -> AccessPolicy:
    """Creates a new access policy."""
    return await access_policy_view.post(
        access_policy,
        token_payload,
        scopes=["api.write"],
        roles=["User"],
    )


# TBD: write tests for this
@router.get("/policies", status_code=200)
async def get_access_policies(
    token_payload=Depends(get_access_token_payload),
) -> list[AccessPolicyRead]:
    """Returns all protected resources."""
    return await access_policy_view.get(
        token_payload,
        roles=["Admin"],
    )


# TBD: write tests for this:
@router.get("/policy/resource/{resource_id}", status_code=200)
async def get_access_policies_for_resource(
    resource_id: str,
    resource_type: str,
    token_payload=Depends(get_access_token_payload),
) -> list[AccessPolicyRead]:
    """Returns all protected resources."""
    if not resource_id or not resource_type:
        raise ValueError("Resource ID and type must be provided.")
    if not UUID(resource_id):
        raise ValueError("Resource ID is not a universal unique identifier (uuid).")
    if resource_type not in ResourceType.list():
        raise ValueError("Resource type is not valid.")
    filters = [
        AccessPolicy.resource_id == resource_id,
        AccessPolicy.resource_type == resource_type,
    ]
    return await access_policy_view.get_with_filters(
        filters,
        token_payload,
        roles=["User"],
    )


# TBD: write tests for this:
@router.get("/policy/identity/{identity_id}", status_code=200)
async def get_access_policies_for_identity(
    identity_id: str,
    identity_type: str,
    token_payload=Depends(get_access_token_payload),
) -> list[AccessPolicyRead]:
    """Returns all protected resources."""
    if not identity_id:
        raise ValueError("Identity ID must be provided.")
    if not UUID(identity_id):
        raise ValueError("Identity ID is not a universal unique identifier (uuid).")
    if not identity_type:
        identity_type = IdentityType.user
    elif identity_type not in IdentityType.list():
        raise ValueError("Identity type is not valid.")
    token_payload = CurrentAccessToken(token_payload)
    current_user = token_payload.provides_current_user()
    if not token_payload.has_role("Admin", require=False):
        if current_user.user_id != identity_id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden.",
            )
    filters = [
        AccessPolicy.identity_id == identity_id,
        AccessPolicy.identity_type == identity_type,
    ]
    return await access_policy_view.get_with_query_options(
        filters=filters,
        token_payload=token_payload,
        roles=["User"],
    )


# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# implement protected routes for:
# AccessPolicies:
# ✔︎ create (share with identity, i.e. user, group)
# ✔︎ create (public share)
# ✔︎ make a generic for the above two - checks are handled in model AccessPolicyCreate!
# X read all (check who has access)
# X read by resource - use filter
# X read by identity - use filter
# - change access Action (own, write, read) -> use delete and create
# - delete (unshare)
# - hierarchy (inheritance)?


access_log_view = BaseView(AccessPolicyCRUD, AccessPolicy)

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# AccessLogs:
# - read (check who accessed what)
# - read resource first "own": corresponds to create
# - read resource last access - use order_by
# - read access count - use func.count
# - read access by identity - use filter
# - read access by resource - use filter
