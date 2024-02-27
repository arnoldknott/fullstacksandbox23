import logging

from core.security import get_access_token_payload, CurrentAccessToken
from fastapi import APIRouter, Depends
from models.protected_resource import ProtectedResource, ProtectedResourceCreate
from crud.protected_resource import ProtectedResourceCRUD

logger = logging.getLogger(__name__)
router = APIRouter()


# Not necessary anymore, since the protection is moved to the router level
# def get_protected_resource(token: Annotated[str, Depends(validate_token)]):


@router.post("/", status_code=201)
async def post_user(
    user: ProtectedResourceCreate,
    # _1=Depends(CurrentAccessTokenHasScope("api.write")),# put that one back in place if refactoring fails!
    # _2=Depends(CurrentAccessTokenHasRole("Admin")),# put that one back in place! if refactoring fails!
    token_payload=Depends(get_access_token_payload),
) -> ProtectedResource:
    """Creates a new user."""
    logger.info("POST user")
    token = CurrentAccessToken(token_payload)
    await token.has_scope("api.write")
    await token.has_role("User")
    async with ProtectedResourceCRUD() as crud:
        created_user = await crud.create(user)
    return created_user


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
        "message": f"Authenticated user (user_id: {current_user.user_id}, azure_user_id: {current_user.azure_user_id}) is authorized to access protected resource!"
    }


# TBD: after reworking security, put the scope protection on router level
# TBD: add role protection (admin only on push, put and delete routes)
# check if working now: should be good! But mainly to be used at router level!
# checked_scopes = ScopeChecker(["api.write"])
# this variable above adds another scope on top of the one, from the router level
# to the function below
# def get_scope_protected_resource(checked: Annotated[str, Depends(checked_scopes)]):
@router.get("/scope")
def get_scope_protected_resource():
    """Returns a scope protected resource."""
    logger.info("GET scope protected resource")
    return {"message": "Hello from a protected resource with scope requirement!"}


# def get_group_protected_resource(token: Annotated[str, Depends(validate_token)]):
@router.get("/group/{group}")
def get_group_protected_resource():
    """Returns a group protected resource."""
    logger.info("GET group protected resource")
    # groups = GroupChecker(["-- put allowed group here --"])
    # print("=== groups ===")
    # print(groups)
    return {"message": "Hello from a protected resource with scope requirement!"}


# @router.get("/oauth")
# def get_protected_resource_oauth(token: Annotated[str, Depends(oauth2_scheme)]):
#     """Returns a protected resource."""
#     logger.info("GET protected resource")
#     return {
#         "message": "Hello from another protected resource - enabling oAuth2 on Swagger UI!"
#     }
