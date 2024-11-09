import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.security import (
    Guards,
    GuardTypes,
    check_token_against_guards,
    get_access_token_payload,
)
from core.types import Action, IdentityType, ResourceType
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD
from models.access import (
    AccessLog,
    AccessLogRead,
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessPolicyRead,
    AccessPolicyUpdate,
)

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()


# region AccessPolicies


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

    current_user = await check_token_against_guards(token_payload, guards)
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

    current_user = await check_token_against_guards(token_payload, guards)
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
    current_user = await check_token_against_guards(token_payload, guards)
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

    current_user = await check_token_against_guards(token_payload, guards)
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
    current_user = await check_token_against_guards(token_payload, guards)
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
    current_user = await check_token_against_guards(token_payload, guards)
    access_policy = AccessPolicyDelete(
        resource_id=resource_id,
        identity_id=identity_id,
        action=action,
        public=public,
    )
    async with access_policy_view.crud() as crud:
        return await crud.delete(current_user, access_policy)


# endregion AccessPolicies

# region AccessLogs

access_log_view = BaseView(AccessLoggingCRUD, AccessLog)


@router.get("/logs", status_code=200)
async def get_access_logs(
    resource_id: Annotated[UUID | None, Query()] = None,
    identity_id: Annotated[UUID | None, Query()] = None,
    action: Annotated[Action | None, Query()] = None,
    status_code: Annotated[int | None, Query()] = None,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[AccessLogRead]:
    """Returns all access logs."""
    logger.info("GET access logs")
    current_user = await check_token_against_guards(token_payload, guards)
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
    current_user = await check_token_against_guards(token_payload, guards)
    # TBD: should be removed now: resource_id is always mandatory now and identity_id is optional - FastAPI should take care of it.
    # if resource_id is None and identity_id is None:
    #     raise HTTPException(
    #         status_code=422,
    #         detail="At least one of the parameters resource_id or identity_id must be provided.",
    #     )
    async with access_log_view.crud() as crud:
        return await crud.read_access_logs_by_resource_id_and_identity_id(
            current_user, resource_id=resource_id, identity_id=identity_id
        )


# TBD: implement a route for identity_id only, so user can see everything the user has access to - filter by own, write, read as query parameter
@router.get("/log/identity/{identity_id}", status_code=200)
async def get_access_logs_for_identity(
    identity_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessLogRead]:
    """Returns creation information for a resource."""
    logger.info("GET access log information for identity")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_access_logs_by_resource_id_and_identity_id(
            current_user, identity_id=identity_id
        )


@router.get("/log/{resource_id}/created", status_code=200)
async def get_creation_date_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> datetime:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
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
    current_user = await check_token_against_guards(token_payload, guards)
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
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_resource_access_count(
            current_user,
            resource_id=resource_id,
        )


# endregion AccessLogs

### No - don't implement - leave the hierarchy inside the individual resources
# region ResourceHierarchy

# add child to parent
# read all children of parent?
# read all parents of child??
# remove child from parent

# endregion ResourceHierarchy

### No - don't implement - leave the hierarchy inside the individual resources
# region IdentityHierarchy

# add child to parent
# read all children of parent?
# read all parents of child??
# remove child from parent

# endregion IdentityHierarchy

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Resource Hierarchy:
# implement as query parameters, wherever it makes sense?
