import logging
from typing import Annotated

import httpx

# from core.security import get_token_from_header
from fastapi import APIRouter, Header, Query

# from fastapi import APIRouter, Depends, Header, HTTPException, status
# from fastapi.security import OAuth2AuthorizationCodeBearer
from msal import ConfidentialClientApplication

from core.config import config
from jobs.demo.tasks import demo_task

logger = logging.getLogger(__name__)
router = APIRouter()


# # TBD: add OAuth2AuthorizationCodeBearer, asks for client_id and client_secret
# # needs scopes
# # primarily this is relevant for Swagger UI, API can be accessed by other tools right now, as long as
# # their callback URL is registered in the Azure AD app registration!
# # move this to main.py?
# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/v2.0/authorize",
#     tokenUrl=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/token",
#     scopes={
#         f"api://{config.API_SCOPE}/api.read": "Read API",
#         f"api://{config.API_SCOPE}/api.write": "Write API",
#     },
#     scheme_name="OAuth2 Authorization Code",
#     description="OAuth2 Authorization Code Bearer implementeation for Swagger UI - identity provider is Microsoft Azure AD",
# )


confClientApp = ConfidentialClientApplication(
    config.AZURE_CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",
    client_credential=config.BACK_CLIENT_SECRET,
)


# def exchange_code_for_token(code: str):
#     data = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "client_id": config.AZURE_CLIENT_ID,
#         "client_secret": config.BACK_CLIENT_SECRET,
#         "redirect_uri": "http://localhost:8000/docs/oauth2-redirect",  # replace with your actual callback URL
#     }
#     response = httpx.post(
#         "https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/token",
#         data=data,
#     )
#     token = response.json().get("access_token")
#     return token


# TBD: refactor to use dependency injection
# might require a working on-behalf-of workflow?
def get_users_groups_ms_graph(access_token: str):
    """Dummy function to try if access token works from backend: getting transistiveMemberOf"""
    # response = httpx.get("https://graph.microsoft.com/v1.0/me/transitiveMemberOf", headers = {"Authorization": f"Bearer {access_token}"})
    response = httpx.get(
        "https://graph.microsoft.com/v1.0/me/transitiveMemberOf",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    groups = response.json()

    return groups


def get_me_ms_graph(access_token: str):
    """Dummy function to try if access token works from backend"""
    # response = httpx.get("https://graph.microsoft.com/v1.0/me/transitiveMemberOf", headers = {"Authorization": f"Bearer {access_token}"})
    response = httpx.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


@router.get("/health")
async def get_health():
    """Returns a 200 OK."""
    logger.info("Health check")
    return {"status": "ok"}


# @router.get("/version")
# async def version():
#     """Returns the version of the backendAPI."""
#     logger.info("Version check")
#     return {"version": "0.0.1"}


@router.get("/keyvault")
async def get_keyvault():
    """Returns the configuration of the Azure keyvault."""
    logger.info("Keyvault check")
    return {
        "Azure keyvault status": config.KEYVAULT_HEALTH,
    }


# @router.get("/postgres")
# async def get_postgres():
#     """Returns the configuration of the PostgreSQL database."""
#     logger.info("Postgres check")
# return alembic version:
# SELECT * FROM public.alembic_version

# @router.get("/redis")
# async def get_redis():
#     """Returns the configuration of the Redis database."""
#     logger.info("Redis check")
# access the Redis database to check if it is running


@router.get("/celery")
async def run_demo_task_in_celery(
    x: Annotated[int, Query()] = 1, y: Annotated[int, Query()] = 2
):
    """Executes a demo task in celery - adding two numbers."""
    logger.info("Celery demo task executed")
    celery_result = demo_task.delay(x, y)
    print("=== api - v1 - core - celery - celery_result ===")
    print(celery_result)
    result = celery_result.get(timeout=10)
    print("=== api - v1 - core - celery - result ===")
    print(result)
    return {"result": result}


# # Don't put under protected resource, because the protected resource router requires scope "api.read"  for this API!
# # This route is protected by the OAuth2AuthorizationCodeBearer scheme.
# @router.get("/oauth2")
# def get_oauth(token: Annotated[str, Depends(oauth2_scheme)]):
#     """Returns a protected resource."""
#     logger.info("GET protected resource")

#     return {
#         "message": "Hello from a protected resource - enabling oAuth2 on Swagger UI!"
#     }

# # Not working yet, callback needs to handle the token
# @router.get("/docs/oauth2-redirect")
# def callback(code: str = Depends(oauth2_scheme)):
#     token = exchange_code_for_token(code)
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not authenticate",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return {"access_token": token, "token_type": "bearer"}


# Note: this one is protected under the scope "user_impersonization"" from https://management.azure.com
# Cannot scopes from other audiences, like this backendAPI.
@router.get("/onbehalfof")
async def get_onbehalfof(authorization: Annotated[str | None, Header()] = None):
    """Access Microsoft Graph as downstream API on behalf of the user."""
    # print("=== header ===")
    # print(authorization)
    token = authorization.split("Bearer ")[1]
    # token = get_token_from_header(authorization)
    logger.info("🔑 Acquiring token on behalf of")
    print("=== getting token on behalf of ===")
    result = confClientApp.acquire_token_on_behalf_of(
        token,
        scopes=["User.Read"],
        # scopes=[".default"],
        # scopes=[
        #     "api.read"
        # ],  # ["User.Read", "https://management.azure.com/user_impersonation"],
    )
    # print("=== token from on-behalf-of ===")
    # print(result)
    try:
        if "access_token" in result:
            logger.info("🔑 Getting user information on behalf of")
            on_behalf_of_token = result["access_token"]
            # Seems to work:
            # response = get_users_groups_ms_graph(on_behalf_of_token)
            response = get_me_ms_graph(on_behalf_of_token)
            logger.info("On behalf of access to Microsoft Graph")
            return {"body": response}
    except Exception as err:
        logger.error("🔑 Failed to fetch user groups from Microsoft Graph.")
        raise err
