import logging

from uuid import UUID
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from core.types import ResourceType, IdentityType, Action
from .base import BaseView
from core.security import (
    get_access_token_payload,
    Guards,
    GuardTypes,
)

# from core.types import GuardTypes
from models.access import (
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyUpdate,
    AccessPolicyRead,
    AccessPolicyDelete,
)
from crud.access import AccessPolicyCRUD

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


# TBD: write tests for this
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
    print("=== access_policy ===")
    print(access_policy)
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


access_log_view = BaseView(AccessPolicyCRUD, AccessPolicy)

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# TBD: write tests for this
# @router.get("/log/created/{resource_id}", status_code=200)
# async def get_creation_information_for_resource(
#     resource_id: UUID,
#     token_payload=Depends(get_access_token_payload),
# ) -> list[AccessLogRead]:
#     """Returns creation information for a resource."""
#     return await access_log_view.get_with_query_options(
#         token_payload,
#         roles=["user"],
#         filters=[AccessLog.resource_id == resource_id],
#         order_by=AccessLog.time,
#         # TBD: ascending or descending?
#         limit=1,
#     )


# AccessLogs:
# only read operations for log - no create, update, delete!
# - read (check who accessed what)
# - read resource first "own": corresponds to create
# - read resource last access - use order_by
# - read access count - use func.count
# - read access by identity - use filter
# - read access by resource - use filter
