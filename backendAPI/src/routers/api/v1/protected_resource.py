import logging
from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Query

from core.security import Guards, get_access_token_payload
from core.types import GuardTypes
from crud.protected_resource import (
    ProtectedResourceCRUD,
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
)
from models.protected_resource import (
    ProtectedResource,
    ProtectedResourceCreate,
    ProtectedChild,
    ProtectedChildCreate,
    ProtectedGrandChild,
    ProtectedGrandChildCreate,
)

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

# region ProtectedResource

protected_resource_view = BaseView(ProtectedResourceCRUD, ProtectedResource)


# TBD: write more tests for this:
@router.post("/", status_code=201)
async def post_protected_resource(
    protected_resource: ProtectedResourceCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedResource:
    """Creates a new protected resource."""
    return await protected_resource_view.post(protected_resource, token_payload, guards)


# TBD: write tests for this:
@router.get("/", status_code=200)
async def get_protected_resources(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[ProtectedResource]:
    """Returns all protected resources."""
    return await protected_resource_view.get(token_payload, guards)


# TBD: write tests for this:
@router.get("/{resource_id}", status_code=200)
async def get_protected_resource_by_id(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> ProtectedResource:
    """Returns a protected resource."""
    return await protected_resource_view.get_by_id(token_payload, resource_id, guards)


# TBD: write tests for this:
@router.put("/{resource_id}", status_code=200)
async def put_protected_resource(
    resource_id: UUID,
    protected_resource: ProtectedResourceCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedResource:
    """Updates a protected resource."""
    return await protected_resource_view.put(
        resource_id, protected_resource, token_payload, guards
    )


# TBD: write more tests for this:
@router.delete("/{resource_id}", status_code=200)
async def delete_protected_resource(
    resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedResource:
    """Deletes a protected resource."""
    return await protected_resource_view.delete(token_payload, resource_id, guards)


# endregion ProtectedResource

# region ProtectedChild

protected_child_view = BaseView(ProtectedChildCRUD, ProtectedChild)


# TBD: write tests for this:
@router.post("/", status_code=201)
async def post_protected_child(
    protected_resource: ProtectedChildCreate,
    parent_id: Annotated[UUID | None, Query()] = None,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> ProtectedResource:
    """Creates a new protected resource."""
    return await protected_resource_view.post(
        protected_resource, token_payload, guards, parent_id
    )


# endregion ProtectedChild


# # TBD: implement tests for this:
# this should be ready to go - just not tested yet and this one get's called by frontend - so for now it's important to return something.
# @router.get("/", status_code=200)
# async def get_protected_resource(
#     token_payload=Depends(get_access_token_payload),
# ) -> List[ProtectedResource]:
#     """Returns a protected resource."""
#     return protected_resource_view.get(
#         token_payload,
#         # TBD: id here? - no only for "get-by-id" route!
#         # scopes=["api.read"], this is on the router already, no need to repeat it here, but it's not wrong to do so. Not the cleanest code. Hmmm...
#         roles=["User"],
#     )


# # This is secure and works!
# # old version - remove after refactoring to BaseView is done!
# @router.post("/", status_code=201)
# async def post_protected_resource(
#     protected_resource: ProtectedResourceCreate,
#     # _1=Depends(CurrentAccessTokenHasScope("api.write")),# put that one back in place if refactoring fails!
#     # _2=Depends(CurrentAccessTokenHasRole("Admin")),# put that one back in place! if refactoring fails!
#     token_payload=Depends(get_access_token_payload),
# ) -> ProtectedResource:
#     """Creates a new protected resource."""
#     logger.info("POST protected resource")
#     token = CurrentAccessToken(token_payload)
#     await token.has_scope("api.write")
#     await token.has_role("User")
#     current_user = await token.provides_current_user()
#     # print("=== protected_resource ===")
#     # print(protected_resource)
#     async with ProtectedResourceCRUD(current_user) as crud:
#         created_protected_resource = await crud.create(protected_resource)
#     return created_protected_resource


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
