import logging

from fastapi import APIRouter, Depends
from .base import BaseView
from core.security import get_access_token_payload
from models.access import AccessPolicy, AccessPolicyCreate
from crud.access import AccessPolicyCRUD

logger = logging.getLogger(__name__)
router = APIRouter()

access_view = BaseView(AccessPolicyCRUD, AccessPolicy)


@router.post("/policy", status_code=201)
async def post_access_policy(
    access_policy: AccessPolicyCreate,
    token_payload=Depends(get_access_token_payload),
) -> AccessPolicy:
    """Creates a new access policy."""
    return await access_view.post(
        access_policy,
        token_payload,
        scopes=["api.write"],
        roles=["User"],
    )


# implement protected routes for:
# AccessPolicies:
# - create (share with identity, i.e. user, group)
# - create (public share)
# - make a generic for the above two - checks are handled in model AccessPolicyCreate!
# - read (check who has access)
# - read by resource - use filter
# - read by identity - use filter
# - change access Action (own, write, read) -> use delete and create
# - delete (unshare)
# - hierarchy (inheritance)?
# AccessLogs:
# - read (check who accessed what)
# - read first "own": corresponds to create
# - read last access - use order_by
# - read access count - use func.count
# - read access by identity - use filter
# - read access by resource - use filter
