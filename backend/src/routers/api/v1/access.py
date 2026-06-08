import logging
from datetime import datetime
from typing import Annotated, AsyncGenerator, List, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from core.security import (
    Guards,
    GuardTypes,
    check_token_against_guards,
    get_http_access_token_payload,
)
from core.databases import get_async_session
from core.types import Action, IdentityType, ResourceType
from crud.access import (
    get_types_from_ids,
    AccessLoggingCRUD,
    AccessPolicyCRUD,
    ResourceHierarchyCRUD,
    IdentityHierarchyCRUD,
)
from models.access import (
    AccessLogRead,
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessPolicyRead,
    AccessPolicyUpdate,
    BaseHierarchyCreate,
    BaseHierarchyDelete,
    ResourceHierarchyRead,
    IdentityHierarchyRead,
)

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()


# region AccessPolicies


access_policy_view = BaseView(AccessPolicyCRUD)


@router.post("/policy", status_code=201)
async def post_access_policy(
    access_policy: AccessPolicyCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> AccessPolicy:
    """Creates a new access policy."""
    return await access_policy_view.post(access_policy, token_payload, guards=guards)


@router.get("/policies", status_code=200)
async def get_access_policies(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies."""
    return await access_policy_view.get(token_payload, guards)


# Only owners get the list of access policies
@router.get("/policy/resource/{resource_id}", status_code=200)
async def get_access_policies_for_resource(
    resource_id: UUID,
    # TBD: add a query parameter for action
    # TBD: add a query parameter for exclude current_user in the result
    token_payload=Depends(get_http_access_token_payload),
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


# Technically a get action, but it's retrieving information based on the resource_ids
@router.post("/policy/resources", status_code=200)
async def get_access_policies_for_resources(
    resource_ids: list[UUID],
    # TBD: add a query parameter for action
    # TBD: add a query parameter for exclude current_user in the result
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessPolicyRead]:
    """Returns all access policies for the requested resource_ids."""
    logger.info("GET access policies for resource_ids")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_policy_view.crud() as crud:
        access_policies = []
        for resource_id in resource_ids:
            access_policies += await crud.read_access_policies_by_resource_id(
                current_user, resource_id
            )
    return access_policies


@router.get("/policy/resource/type/{resource_type}", status_code=200)
async def get_access_policies_by_resource_type(
    resource_type: ResourceType,
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> AccessPolicyRead:
    """Deletes an old access policy and creates a new instead."""
    logger.info("PUT access policy")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_policy_view.crud() as crud:
        new_policy_in_database = await crud.update(current_user, access_policy)
        return new_policy_in_database


@router.delete("/policy", status_code=200)
async def delete_access_policy(
    # access_policy: AccessPolicyDelete,
    resource_id: Annotated[UUID | None, Query()] = None,
    identity_id: Annotated[UUID | None, Query()] = None,
    action: Annotated[Action | None, Query()] = None,
    public: Annotated[bool | None, Query()] = None,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> int:
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

# region Entity Type


@router.get("/type/{entity_id}", status_code=200)
async def get_access_policies_by_entity_type(
    entity_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> ResourceType | IdentityType | None:
    """Returns all access policies for requested entity_type."""
    logger.info("GET access_policies for entity_type")

    current_user = await check_token_against_guards(token_payload, guards)
    entity_type = None
    async with access_policy_view.crud() as crud:
        entity_type = await crud.read_entity_type_by_id(current_user, entity_id)
    return entity_type


# endregion Entity Type


# region AccessRights


@router.get("/right/resource/{resource_id}", status_code=200)
async def get_my_access_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> Action | None:
    """Returns the access level to a resource for the current user."""
    logger.info("GET access level for resource_id")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_policy_view.crud() as crud:
        return await crud.check_access(
            resource_id=resource_id, current_user=current_user
        )


@router.post("/right/resources", status_code=200)
async def get_my_access_for_resources(
    resource_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[Action | None]:
    """Returns the access level to a resource for the current user."""
    logger.info("GET access level for resource_id")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_policy_view.crud() as crud:
        access_rights = []
        for resource_id in resource_ids:
            right = await crud.check_access(
                resource_id=resource_id, current_user=current_user
            )
            access_rights.append(right)
    return access_rights


# endregion AccessRights

# region AccessLogs

access_log_view = BaseView(AccessLoggingCRUD)


@router.get("/logs", status_code=200)
async def get_access_logs(
    resource_id: Annotated[UUID | None, Query()] = None,
    identity_id: Annotated[UUID | None, Query()] = None,
    action: Annotated[Action | None, Query()] = None,
    status_code: Annotated[int | None, Query()] = None,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
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
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[AccessLogRead]:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_access_logs_by_resource_id_and_identity_id(
            current_user, resource_id=resource_id, identity_id=identity_id
        )


@router.get("/log/identity/{identity_id}", status_code=200)
async def get_access_logs_for_identity(
    identity_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> datetime:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_resource_created_at(
            resource_id=resource_id,
            current_user=current_user,
        )


# TBD: change from /log to logs - it's a list of resources!
@router.post("/logs/created", status_code=200)
async def get_creation_date_for_resources(
    resource_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[datetime]:
    """Returns creation information for a list of resources."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        creation_dates = []
        for resource_id in resource_ids:
            creation_date = await crud.read_resource_created_at(
                resource_id=resource_id,
                current_user=current_user,
            )
            creation_dates.append(creation_date)
    return creation_dates


@router.get("/log/{resource_id}/last-modified", status_code=200)
async def get_last_modified_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> datetime:
    """Returns the log for the latest modification of a resource."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_resource_last_modified_at(
            resource_id=resource_id,
            current_user=current_user,
        )


@router.post("/logs/last-modified", status_code=200)
async def get_last_modified_for_resources(
    resource_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[datetime]:
    """Returns latest modification time for resources."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        last_modified_dates = []
        for resource_id in resource_ids:
            last_modified = await crud.read_resource_last_modified_at(
                resource_id=resource_id,
                current_user=current_user,
            )
            last_modified_dates.append(last_modified)
    return last_modified_dates


@router.get("/log/{resource_id}/last-accessed", status_code=200)
async def get_last_accessed_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> AccessLogRead:
    """Returns the log for the latest access of a resource."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_resource_last_accessed_at(
            resource_id=resource_id,
            current_user=current_user,
        )


@router.post("/logs/last-accessed", status_code=200)
async def get_last_accessed_for_resources(
    resource_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[datetime]:
    """Returns latest access time for resources."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        last_accessed_dates = []
        for resource_id in resource_ids:
            last_accessed = await crud.read_resource_last_accessed_at(
                resource_id=resource_id,
                current_user=current_user,
                action=Action.read,
            )
            last_accessed_dates.append(last_accessed.time)
    return last_accessed_dates


@router.get("/log/{resource_id}/count", status_code=200)
async def get_access_count_for_resource(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> int:
    """Returns creation information for a resource."""
    logger.info("GET access log information for resource")
    current_user = await check_token_against_guards(token_payload, guards)
    async with access_log_view.crud() as crud:
        return await crud.read_resource_access_count(
            resource_id=resource_id,
            current_user=current_user,
        )


# endregion AccessLogs

# region Hierarchies

# O add child to parent
# read all children of parent?
# read all parents of child??
# O update relationship between parent and child (e.g. change inherit flag)
# O reorder children of parent
# O remove child from parent


async def choose_hierarchy_CRUD(
    entity_ids: List[UUID],
) -> AsyncGenerator[ResourceHierarchyCRUD | IdentityHierarchyCRUD, None]:
    """Chooses the appropriate hierarchy CRUD based on the entity (either resource or identity) ID."""
    session = await get_async_session()
    try:
        entity_types = await get_types_from_ids(session, entity_ids)
        hierarchy_type = None
        for entity_type in entity_types:
            if hierarchy_type is None:
                if entity_type in ResourceType.list():
                    hierarchy_type = ResourceType
                elif entity_type in IdentityType.list():
                    hierarchy_type = IdentityType
            else:
                if (
                    entity_type in ResourceType.list()
                    and hierarchy_type != ResourceType
                ):
                    raise ValueError("Mixed entity types are not allowed.")
                elif (
                    entity_type in IdentityType.list()
                    and hierarchy_type != IdentityType
                ):
                    raise ValueError("Mixed entity types are not allowed.")

        if not hierarchy_type:
            raise ValueError("Entity type not found for the given ID.")
        if hierarchy_type == ResourceType:
            async with ResourceHierarchyCRUD(session=session) as crud:
                yield crud
            return

        if hierarchy_type == IdentityType:
            async with IdentityHierarchyCRUD(session=session) as crud:
                yield crud
    finally:
        await session.close()


@router.post("/hierarchy/{parent_id}/child/{child_id}", status_code=201)
async def post_relationship(
    parent_id: UUID,
    child_id: UUID,
    inherit: Annotated[bool, Query()] = False,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
    # ) -> List[ResourceHierarchyRead] | List[IdentityHierarchyRead]:
) -> ResourceHierarchyRead | IdentityHierarchyRead:
    """Creates a new relationship between a child and a parent resource."""
    logger.info("POST view to add child to parent calls add_child_to_parent CRUD")
    BaseHierarchyCreate.model_validate(
        {
            "parent_id": parent_id,
            "child_id": child_id,
            "inherit": inherit,
        }
    )
    current_user = await check_token_against_guards(token_payload, guards)
    # if isinstance(child_ids, UUID):
    #     child_ids = [child_ids]

    # created_hierarchies = []
    # for child_id in child_ids:
    #     async for hierarchy_CRUD in choose_hierarchy_CRUD([parent_id, child_id]):
    #         created_hierarchy = await hierarchy_CRUD.create(
    #             current_user, parent_id, child_id, inherit
    #         )
    #         created_hierarchies.append(created_hierarchy)
    # return created_hierarchies
    created_hierarchy = None
    async for hierarchy_CRUD in choose_hierarchy_CRUD([parent_id, child_id]):
        created_hierarchy = await hierarchy_CRUD.create(
            current_user, parent_id, child_id, inherit
        )
    if created_hierarchy is None:
        raise HTTPException(status_code=400, detail="Hierarchy could not be created.")
    return created_hierarchy


@router.post("/hierarchies", status_code=201)
async def post_relationships(
    hierarchies: List[BaseHierarchyCreate],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> List[ResourceHierarchyRead] | List[IdentityHierarchyRead]:
    """Creates a new relationship between a child and a parent resource."""
    logger.info("POST view to add child to parent calls add_child_to_parent CRUD")
    current_user = await check_token_against_guards(token_payload, guards)

    created_hierarchies = []
    for hierarchy in hierarchies:
        async for hierarchy_CRUD in choose_hierarchy_CRUD(
            [hierarchy.parent_id, hierarchy.child_id]
        ):
            created_hierarchy = await hierarchy_CRUD.create(
                current_user, hierarchy.parent_id, hierarchy.child_id, hierarchy.inherit
            )
            created_hierarchies.append(created_hierarchy)
    return created_hierarchies


@router.get("/hierarchies", status_code=200)
async def get_relationships(
    parent_id: Annotated[UUID | None, Query()] = None,
    child_id: Annotated[UUID | None, Query()] = None,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> List[ResourceHierarchyRead] | List[IdentityHierarchyRead]:
    logger.info("GET retrieves parent-child relationships.")
    if not parent_id and not child_id:
        raise HTTPException(
            status_code=400,
            detail="At least one of parent_id or child_id must be provided.",
        )
    current_user = await check_token_against_guards(token_payload, guards)
    read_hierarchies = []
    ids = [parent_id] if parent_id else []
    ids.append(child_id) if child_id else None
    async for hierarchy_CRUD in choose_hierarchy_CRUD(ids):
        read_hierarchies = await hierarchy_CRUD.read(current_user, parent_id, child_id)
    return read_hierarchies


@router.post(
    "/hierarchy/{parent_id}/move/{child_id}/{position}",
    status_code=201,
)
async def post_reorder_children(
    parent_id: UUID,
    child_id: UUID,
    position: str,
    other_child_id: Annotated[UUID | None, Query()] = None,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
):
    """Within a parent resource moves one child before another child."""
    logger.info("POST reorder children view calls reorder_children CRUD")
    current_user = await check_token_against_guards(token_payload, guards)
    if position not in ["start", "end"]:
        if not other_child_id:
            raise HTTPException(status_code=400, detail="Bad request.")
        elif position not in ["before", "after"]:
            raise HTTPException(status_code=400, detail="Bad request.")
    async for hierarchy_CRUD in choose_hierarchy_CRUD([parent_id, child_id]):
        if isinstance(hierarchy_CRUD, ResourceHierarchyCRUD):
            await hierarchy_CRUD.reorder_children(
                current_user,
                parent_id,
                child_id,
                position,
                other_child_id,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Reordering is not supported for this hierarchy.",
            )


@router.put("/hierarchy/{parent_id}/child/{child_id}", status_code=200)
async def put_relationship(
    parent_id: UUID,
    child_id: UUID,
    inherit: bool,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ResourceHierarchyRead | IdentityHierarchyRead:
    logger.info("PUT updates a parent-child relationship.")
    current_user = await check_token_against_guards(token_payload, guards)
    updated_hierarchy = cast(ResourceHierarchyRead | IdentityHierarchyRead, None)
    async for hierarchy_CRUD in choose_hierarchy_CRUD([parent_id, child_id]):
        updated_hierarchy = await hierarchy_CRUD.update(
            current_user, parent_id, child_id, inherit
        )
    return updated_hierarchy


@router.delete("/hierarchy/{parent_id}/child/{child_id}", status_code=200)
async def delete_relationship(
    parent_id: UUID,
    child_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> int:
    """Deletes the relationship between a child and a parent resource."""
    logger.info("DELETE removes a child from a parent.")
    current_user = await check_token_against_guards(token_payload, guards)
    deleted_number = 0
    async for hierarchy_CRUD in choose_hierarchy_CRUD([parent_id, child_id]):
        deleted_number = await hierarchy_CRUD.delete(current_user, parent_id, child_id)
    return deleted_number


@router.delete("/hierarchies", status_code=200)
async def delete_relationships(
    hierarchies: List[BaseHierarchyDelete],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> int:
    """Removes several hierarchies."""
    logger.info("DELETE removes several hierarchies")
    current_user = await check_token_against_guards(token_payload, guards)
    deleted_hierarchies = 0
    for hierarchy in hierarchies:
        ids = [hierarchy.parent_id] if hierarchy.parent_id else []
        ids.append(hierarchy.child_id) if hierarchy.child_id else None
        async for hierarchy_CRUD in choose_hierarchy_CRUD(ids):
            this_deleted_number = await hierarchy_CRUD.delete(
                current_user, hierarchy.parent_id, hierarchy.child_id
            )
            deleted_hierarchies += this_deleted_number
    return deleted_hierarchies


# endregion Hierarchies

### Reconsider: maybe worthwhile implementing - leave the hierarchy inside the individual resources
# region ResourceHierarchy

# add child to parent
# read all children of parent?
# read all parents of child??
# remove child from parent
# reorder children of parent
# update relationship between parent and child (e.g. change inherit flag)

# endregion ResourceHierarchy

# region IdentityHierarchy

### Reconsider: maybe worthwhile implementing - leave the hierarchy inside the individual resources
# region IdentityHierarchy

# add child to parent
# read all children of parent?
# read all parents of child??
# remove child from parent
# update relationship between parent and child (e.g. change inherit flag)

# endregion IdentityHierarchy

# Nomenclature:
# ✔︎ implemented
# X missing tests
# - not implemented

# Resource Hierarchy:
# implement as query parameters, wherever it makes sense?
