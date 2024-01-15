import logging
from typing import Annotated

from core.access import GroupChecker, ScopeChecker, validate_token
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
router = APIRouter()


# Not necessary anymore, since the protection is moved to the router level
# def get_protected_resource(token: Annotated[str, Depends(validate_token)]):


# This is secure and works!
@router.get("/")
def get_protected_resource():
    """Returns a protected resource."""
    logger.info("GET protected resource")
    return {"message": "Hello from a protected resource!"}


# check if working now: should be good! But mainly to be used at router level!
checked_scopes = ScopeChecker(["api.write"])


# this variable above adds another scope on top of the one, from the router level
# to the function below
@router.get("/scope")
def get_scope_protected_resource(checked: Annotated[str, Depends(checked_scopes)]):
    """Returns a scope protected resource."""
    logger.info("GET scope protected resource")
    return {"message": "Hello from a protected resource with scope requirement!"}


@router.get("/group/{group}")
def get_group_protected_resource(token: Annotated[str, Depends(validate_token)]):
    """Returns a group protected resource."""
    logger.info("GET group protected resource")
    groups = GroupChecker(["-- put allowed group here --"])
    print("=== groups ===")
    print(groups)
    return {"message": "Hello from a protected resource with scope requirement!"}


# @router.get("/oauth")
# def get_protected_resource_oauth(token: Annotated[str, Depends(oauth2_scheme)]):
#     """Returns a protected resource."""
#     logger.info("GET protected resource")
#     return {
#         "message": "Hello from another protected resource - enabling oAuth2 on Swagger UI!"
#     }
