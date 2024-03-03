import logging

from core.security import get_access_token_payload, CurrentAccessToken
from fastapi import APIRouter, Depends
from models.protected_resource import ProtectedResource, ProtectedResourceCreate
from crud.protected_resource import ProtectedResourceCRUD
from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()


# Not necessary anymore, since the protection is moved to the router level
# def get_protected_resource(token: Annotated[str, Depends(validate_token)]):


protected_resource_view = BaseView(ProtectedResourceCRUD)


# TBD: write more tests for this:
@router.post("/", status_code=201)
async def post_protected_resource(
    protected_resource: ProtectedResourceCreate,
    token_payload=Depends(get_access_token_payload),
) -> ProtectedResource:
    """Creates a new protected resouce."""
    return await protected_resource_view.post(
        token_payload,
        protected_resource,
        scopes=["api.write"],
        roles=["User"],
    )


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
#     current_user = token.provides_current_user()
#     # print("=== protected_resource ===")
#     # print(protected_resource)
#     async with ProtectedResourceCRUD(current_user) as crud:
#         created_protected_resource = await crud.create(protected_resource)
#     return created_protected_resource


# This is secure and works!
@router.get("/")
async def get_protected_resource(
    token_payload=Depends(get_access_token_payload),
    # current_user=Depends(CurrentAzureUserInDatabase()),
):
    """Returns a protected resource."""
    token = CurrentAccessToken(token_payload)
    current_user = await token.gets_or_signs_up_current_user()
    logger.info("GET protected resource")
    return {
        # "message": "Hello from protected resource!"
        "message": f"Authenticated user (user_id: {current_user.user_id}, azure_user_id: {current_user.azure_user_id}) is authorized to access protected resource!"
    }


#
