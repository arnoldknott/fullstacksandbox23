import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.security import Guards, get_access_token_payload
from core.types import GuardTypes
from crud.protected_resource import (
    ProtectedResourceCRUD,
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
)
from models.protected_resource import (
    ProtectedChild,
    ProtectedChildCreate,
    ProtectedChildRead,
    ProtectedChildUpdate,
    ProtectedResource,
    ProtectedResourceRead,
    ProtectedResourceCreate,
    ProtectedResourceUpdate,
    ProtectedGrandChild,
    ProtectedGrandChildRead,
    ProtectedGrandChildCreate,
    ProtectedGrandChildUpdate,
)
from models.access import ResourceHierarchyRead

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

# Endpoints for family of protected resources with parent-child relationships in three generations:
# - protected resource
#   - protected child
#     - protected grand child


# region ProtectedResource

protected_resource_view = BaseView(ProtectedResourceCRUD, ProtectedResource)


@router.post("/resource/", status_code=201)
async def post_protected_resource(
    protected_resource: ProtectedResourceCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedResource:
    """Creates a new protected resource."""
    return await protected_resource_view.post(protected_resource, token_payload, guards)


@router.get("/resource/", status_code=200)
async def get_protected_resources(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[ProtectedResourceRead]:
    """Returns all protected resources."""
    return await protected_resource_view.get(token_payload, guards)


@router.get("/resource/{resource_id}", status_code=200)
async def get_protected_resource_by_id(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> ProtectedResourceRead:
    """Returns a protected resource."""
    return await protected_resource_view.get_by_id(resource_id, token_payload, guards)


@router.put("/resource/{resource_id}", status_code=200)
async def put_protected_resource(
    resource_id: UUID,
    protected_resource: ProtectedResourceUpdate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedResource:
    """Updates a protected resource."""
    return await protected_resource_view.put(
        resource_id, protected_resource, token_payload, guards
    )


@router.delete("/resource/{resource_id}", status_code=200)
async def delete_protected_resource(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a protected resource."""
    return await protected_resource_view.delete(resource_id, token_payload, guards)


# endregion ProtectedResource

# region ProtectedChild

protected_child_view = BaseView(ProtectedChildCRUD, ProtectedChild)


@router.post("/child/", status_code=201)
async def post_protected_child(
    protected_child: ProtectedChildCreate,
    parent_id: Annotated[UUID | None, Query()] = None,
    inherit: Annotated[bool, Query()] = False,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedChild:
    """Creates a new protected child."""
    return await protected_child_view.post(
        protected_child, token_payload, guards, parent_id, inherit
    )


# TBD: write tests for this endpoint:
@router.post("/child/{child_id}/parent/{parent_id}", status_code=201)
async def post_add_child_to_parent(
    parent_id: UUID,
    child_id: UUID,
    inherit: Annotated[bool, Query()] = False,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ResourceHierarchyRead:
    """Adds a child to a parent."""
    return await protected_child_view.post_add_child_to_parent(
        parent_id, child_id, token_payload, guards, inherit
    )


@router.get("/child/", status_code=200)
async def get_protected_child(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[ProtectedChildRead]:
    """Returns all protected child resources."""
    return await protected_child_view.get(token_payload, guards)


@router.get("/child/{resource_id}", status_code=200)
async def get_protected_child_by_id(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> ProtectedChildRead:
    """Returns a protected child resource."""
    return await protected_child_view.get_by_id(resource_id, token_payload, guards)


@router.put("/child/{resource_id}", status_code=200)
async def put_protected_child(
    resource_id: UUID,
    protected_child: ProtectedChildUpdate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedChild:
    """Updates a protected child resource."""
    return await protected_child_view.put(
        resource_id, protected_child, token_payload, guards
    )


@router.delete("/child/{resource_id}", status_code=200)
async def delete_protected_child(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a protected child resource."""
    return await protected_child_view.delete(resource_id, token_payload, guards)


# endregion ProtectedChild

# region ProtectedGrandChild

protected_grand_child_view = BaseView(ProtectedGrandChildCRUD, ProtectedGrandChild)


@router.post("/grandchild/", status_code=201)
async def post_protected_grandchild(
    protected_grandchild: ProtectedGrandChildCreate,
    parent_id: Annotated[UUID | None, Query()] = None,
    inherit: Annotated[bool, Query()] = False,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedGrandChild:
    """Creates a new protected grandchild."""
    return await protected_grand_child_view.post(
        protected_grandchild, token_payload, guards, parent_id, inherit
    )


@router.get("/grandchild/", status_code=200)
async def get_protected_grandchild(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[ProtectedGrandChildRead]:
    """Returns all protected grandchild resources."""
    return await protected_grand_child_view.get(token_payload, guards)


@router.get("/grandchild/{resource_id}", status_code=200)
async def get_protected_grandchild_by_id(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> ProtectedGrandChildRead:
    """Returns a protected grandchild resource."""
    return await protected_grand_child_view.get_by_id(
        resource_id, token_payload, guards
    )


@router.put("/grandchild/{resource_id}", status_code=200)
async def put_protected_grandchild(
    resource_id: UUID,
    protected_grandchild: ProtectedGrandChildUpdate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedGrandChild:
    """Updates a protected grandchild resource."""
    return await protected_grand_child_view.put(
        resource_id, protected_grandchild, token_payload, guards
    )


@router.delete("/grandchild/{resource_id}", status_code=200)
async def delete_protected_grandchild(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a protected grandchild resource."""
    return await protected_grand_child_view.delete(resource_id, token_payload, guards)


# endregion ProtectedGrandChild


# This is secure and works!
# old version - remove after refactoring to BaseView is done!
# note - this is the path called by the frontend!
# @router.get("/")
# async def get_protected_resource(
#     token_payload=Depends(get_access_token_payload),
#     # current_user=Depends(CurrentAzureUserInDatabase()),
# ):
#     """Returns a protected resource."""
#     token = CurrentAccessToken(token_payload)
#     current_user = await token.gets_or_signs_up_current_user()
#     logger.info("GET protected resource")
#     return {
#         # "message": "Hello from protected resource!"
#         "message": f"Authenticated user (user_id: {current_user.id}, azure_user_id: {current_user.azure_user_id}) is authorized to access protected resource!"
#     }
