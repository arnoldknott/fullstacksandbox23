import logging
from typing import Annotated

from core.oauth import validate_token
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
router = APIRouter()

# TBD: add OAuth2AuthorizationCodeBearer, asks for client_id and client_secret
# needs scopes
# primarily this is relevant for Swagger UI, API can be accessed by other tools right now, as long as
# their callback URL is registered in the Azure AD app registration!
# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl="https://login.microsoftonline.com/f251f123-c9ce-448e-9277-34bb285911d9/oauth2/v2.0/authorize",
#     tokenUrl="https://login.microsoftonline.com/f251f123-c9ce-448e-9277-34bb285911d9/oauth2/token",
#     scopes={
#         "api://{-- put API scope here -- }/api.read": "Read API",
#         "api://{-- put API scope here -- }/api.write": "Write API",
#     },
# )


# This is secure and works!
@router.get("/")
def get_protected_resource(token: Annotated[str, Depends(validate_token)]):
    """Returns a protected resource."""
    logger.info("GET protected resource")
    return {"message": "Hello from a protected resource!"}


# @router.get("/oauth")
# def get_protected_resource_oauth(token: Annotated[str, Depends(oauth2_scheme)]):
#     """Returns a protected resource."""
#     logger.info("GET protected resource")
#     return {
#         "message": "Hello from another protected resource - enabling oAuth2 on Swagger UI!"
#     }
