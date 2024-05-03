import logging

from uuid import UUID
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from core.types import ResourceType, IdentityType, Action
from .base import BaseView
from core.security import (
    get_access_token_payload,
    Guards,
    GuardTypes,
)
from models.access import (
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyUpdate,
    AccessPolicyRead,
    AccessPolicyDelete,
    AccessLog,
    AccessLogRead,
)
from crud.access import AccessPolicyCRUD, AccessLoggingCRUD

logger = logging.getLogger(__name__)
router = APIRouter()

access_policy_view = BaseView(AccessPolicyCRUD, AccessPolicy)


@router.post("/policy", status_code=201)
async def post_access_policy(
    access_policy: AccessPolicyCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> AccessPolicy:
    """Creates a new access policy."""
    return await access_policy_view.post(access_policy, token_payload, guards=guards)


@router.get("/policies", status_code=200)
async def get_access_policies(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies."""
    return await access_policy_view.get(token_payload, guards)


@router.get("/policy/resource/{resource_id}", status_code=200)
async def get_access_policies_for_resource(
    resource_id: UUID,
    # TBD: add a query parameter for action
    # TBD: add a query parameter for exclude current_user in the result
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies for requested resource_id."""
    logger.info("GET access policies for resource_id")

    current_user = await access_policy_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_policy_view.crud() as crud:
        access_policies = await crud.read_access_policies_by_resource_id(
            current_user, resource_id
        )
    return access_policies


@router.get("/policy/resource/type/{resource_type}", status_code=200)
async def get_access_policies_by_resource_type(
    resource_type: ResourceType,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies for requested resource_type."""
    logger.info("GET access_policies for resource_type")

    current_user = await access_policy_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_policy_view.crud() as crud:
        access_policies = await crud.read_access_policies_by_resource_type(
            current_user, resource_type
        )
    return access_policies


# - Admin can query any user-id
# - User can only query the access policies with other user-id's, of which user is owner
@router.get("/policy/identity/{identity_id}", status_code=200)
async def get_access_policies_for_identity(
    identity_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies for the requested identity."""
    logger.info("GET user by azure_user_id")
    current_user = await access_policy_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_policy_view.crud() as crud:
        access_policies = await crud.read_access_policies_for_identity(
            current_user, identity_id
        )
    return access_policies


@router.get("/policy/identity/type/{identity_type}", status_code=200)
async def get_access_policies_by_identity_type(
    identity_type: IdentityType,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies for requested resource_type."""
    logger.info("GET access_policies for resource_type")

    current_user = await access_policy_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_policy_view.crud() as crud:
        access_policies = await crud.read_access_policies_by_identity_type(
            current_user, identity_type
        )
    return access_policies


@router.put("/policy", status_code=200)
async def put_access_policy(
    access_policy: AccessPolicyUpdate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> AccessPolicyRead:
    """Deletes an old access policy and creates a new instead."""
    logger.info("PUT access policy")
    current_user = await access_policy_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_policy_view.crud() as crud:
        new_policy_in_database = await crud.change(current_user, access_policy)
        print("=== new_policy_in_database ===")
        print(new_policy_in_database)
        return new_policy_in_database


@router.delete("/policy", status_code=200)
async def delete_access_policy(
    # access_policy: AccessPolicyDelete,
    resource_id: Annotated[UUID | None, Query()] = None,
    identity_id: Annotated[UUID | None, Query()] = None,
    action: Annotated[Action | None, Query()] = None,
    public: Annotated[bool | None, Query()] = None,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes an access policy."""
    logger.info("DELETE access policy")
    current_user = await access_policy_view._check_token_against_guards(
        token_payload, guards
    )
    access_policy = AccessPolicyDelete(
        resource_id=resource_id,
        identity_id=identity_id,
        action=action,
        public=public,
    )
    async with access_policy_view.crud() as crud:
        return await crud.delete(current_user, access_policy)


# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# implement protected routes for:
# AccessPolicies:
# ✔︎ create (share with identity, i.e. user, group)
# ✔︎ create (public share)
# ✔︎ make a generic for the above two - checks are handled in model AccessPolicyCreate!
# ✔︎ read all (check who has access)
# ✔︎ read by resource_id - use filter
# ✔︎ read by resource_type - use filter - join with IdentifierTypeTable
# ✔︎ read by identity - use filter
# ✔︎ read by identity_type - use filter - join with IdentifierTypeTable (can wait)
# ✔︎ change access Action (own, write, read) -> use delete first and then create; but update model can be used: derive from Create and add new action!
# ✔︎ delete (unshare)
# - hierarchy (inheritance)?


access_log_view = BaseView(AccessLoggingCRUD, AccessLog)

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented


@router.get("/logs", status_code=200)
async def get_access_logs(
    resource_id: Annotated[UUID | None, Query()] = None,
    identity_id: Annotated[UUID | None, Query()] = None,
    action: Annotated[Action | None, Query()] = None,
    status_code: Annotated[int | None, Query()] = 200,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[AccessLogRead]:
    """Returns all access logs."""
    logger.info("GET access logs")
    current_user = await access_log_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_log_view.crud() as crud:
        return await crud.read(
            current_user, resource_id, identity_id, action, status_code=status_code
        )


@router.get("/log/{resource_id}", status_code=200)
async def get_access_logs_for_resource(
    resource_id: UUID,
    identity_id: Annotated[UUID | None, Query()] = None,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessLogRead]:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await access_log_view._check_token_against_guards(
        token_payload, guards
    )
    if resource_id is None and identity_id is None:
        raise HTTPException(
            status_code=422,
            detail="At least one of the parameters resource_id or identity_id must be provided.",
        )
    async with access_log_view.crud() as crud:
        return await crud.read_access_logs_by_resource_id_and_identity_id(
            current_user, resource_id=resource_id, identity_id=identity_id
        )


@router.get("/log/{resource_id}/created", status_code=200)
async def get_creation_date_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> datetime:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await access_log_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_log_view.crud() as crud:
        return await crud.read_resource_created_at(
            current_user,
            resource_id=resource_id,
        )


@router.get("/log/{resource_id}/last-accessed", status_code=200)
async def get_last_accessed_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> AccessLogRead:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await access_log_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_log_view.crud() as crud:
        return await crud.read_resource_last_accessed_at(
            current_user,
            resource_id=resource_id,
        )


@router.get("/log/{resource_id}/count", status_code=200)
async def get_access_count_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> int:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await access_log_view._check_token_against_guards(
        token_payload, guards
    )
    async with access_log_view.crud() as crud:
        return await crud.read_resource_access_count(
            current_user,
            resource_id=resource_id,
        )


# AccessLogs:
# only read operations for log - no create, update, delete!
# implement as query parameters, wherever it makes sense?
# ✔︎ read all logs - admin only
# X read logs by resource_id
# X read resources first "own" log: corresponds to create
# X read resource last access - use order_by
# X read access count - use func.count/len
# X read access by identity
# X read access by resource
