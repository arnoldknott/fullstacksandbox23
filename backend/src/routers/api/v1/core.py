import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Header, Query
from msal import ConfidentialClientApplication

from core.config import config
from core.security import (
    Guards,
    check_token_against_guards,
    get_http_access_token_payload,
)
from core.types import GuardTypes
from jobs.demo.tasks import demo_task

logger = logging.getLogger(__name__)
router = APIRouter()


confClientApp = ConfidentialClientApplication(
    config.BACKEND_API_CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",
    client_credential=config.BACK_CLIENT_SECRET,
)


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


async def get_token_payload(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
):
    """Decodes the token from the request."""
    logger.info("Getting token payload")
    await check_token_against_guards(token_payload, guards)
    return token_payload


@router.get("/oauth_token_payload")
async def read_token_payload(
    token_payload: Annotated[dict, Depends(get_token_payload)],
):
    return token_payload


# Note: this one is protected under the scope "user_impersonization"" from https://management.azure.com
# Cannot scopes from other audiences, like this backendAPI.
@router.get("/onbehalfof")
async def get_onbehalfof(
    token_payload: Annotated[dict, Depends(get_token_payload)],
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
    authorization: Annotated[str | None, Header()] = None,
    ):
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
