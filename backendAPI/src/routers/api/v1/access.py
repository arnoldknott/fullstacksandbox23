import logging

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from core.types import ResourceType, IdentityType
from .base import BaseView
from core.security import (
    get_access_token_payload,
    CurrentAccessToken,
    Guards,
    GuardTypes,
)

# from core.types import GuardTypes
from models.access import (
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyRead,
)
from crud.access import AccessPolicyCRUD

logger = logging.getLogger(__name__)
router = APIRouter()

access_policy_view = BaseView(AccessPolicyCRUD, AccessPolicy)


# class AccessPolicyView(BaseView):
#     """Extends base view with access policy specific methods."""

#     def __init__(self):
#         super().__init__(AccessPolicyCRUD, AccessPolicy)

#     # TBD: rethink: this gets ways to complicated
#     async def get_access_policies_for_resource(
#         self,
#         resource_id: UUID,
#         resource_type: ResourceType,  # TBD: remove and let CRUD figure it out?
#         token_payload=None,
#         guards=None,  #: GuardTypes = Depends(Guards(roles=["User"])),
#     ) -> List[AccessPolicyRead]:
#         """GET view for access policies for a resource"""
#         logger.info("GET user by azure_user_id")
#         current_user = await self._check_token_against_guards(token_payload, guards)
#         # current_user = await self._guards(token_payload, scopes, roles, groups)
#         async with self.crud() as crud:
#             access_policies = await crud.read_access_policies_by_resource_id(
#                 resource_id, resource_type, current_user
#             )
#         return access_policies

#     async def get_access_policies_for_identity(
#         self,
#         identity_id: UUID,
#         identity_type: IdentityType,  # TBD: remove and let CRUD figure it out?
#         token_payload=None,
#         guards=None,  #: GuardTypes = Depends(Guards(roles=["User"])),
#     ) -> List[AccessPolicyRead]:
#         """GET view for access policies for a identity"""
#         logger.info("GET user by azure_user_id")
#         current_user = await self._check_token_against_guards(token_payload, guards)
#         # current_user = await self._guards(token_payload, scopes, roles, groups)
#         async with self.crud() as crud:
#             access_policies = await crud.read_access_policies_for_identity(
#                 identity_id, identity_type, current_user
#             )
#         return access_policies


# access_policy_view = AccessPolicyView()


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
    # resource_type: ResourceType,  # TBD: remove and let CRUD figure it out?
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
            resource_id, current_user
        )
    return access_policies
    # return await access_policy_view.get_access_policies_for_resource(
    #     resource_id,
    #     resource_type,
    #     token_payload,
    #     guards=guards,
    #     # roles=["User"],
    # )
    # filters = [
    #     AccessPolicy.resource_id == resource_id,
    #     AccessPolicy.resource_type == resource_type,
    # ]
    # return await access_policy_view.get_with_query_options(
    #     filters,
    #     token_payload,
    #     roles=["User"],
    # )


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
            resource_type, current_user
        )
    return access_policies


# TBD: write tests for this:
# - Admin can query any user-id
# - User can only query their own user-id
@router.get("/policy/identity/{identity_id}", status_code=200)
async def get_access_policies_for_identity(
    identity_id: UUID,
    # identity_type: IdentityType = IdentityType.user,  # TBD: remove and let CRUD figure it out?
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
            identity_id, current_user
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
            identity_type, current_user
        )
    return access_policies


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
# - change access Action (own, write, read) -> use delete and create
# - delete (unshare)
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
# - read (check who accessed what)
# - read resource first "own": corresponds to create
# - read resource last access - use order_by
# - read access count - use func.count
# - read access by identity - use filter
# - read access by resource - use filter
