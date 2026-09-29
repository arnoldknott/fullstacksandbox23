import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from core.config import config
from core.security import (
    Guards,
    MicrosoftGuard,
    check_token_against_guards,
    get_http_access_token_payload,
)
from core.types import GuardTypes
from jobs.demo.tasks import demo_task

logger = logging.getLogger(__name__)
router = APIRouter()


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
    celery_result = demo_task.delay(x, y)  # type: ignore[attr-defined]
    print("=== api - v1 - core - celery - celery_result ===")
    print(celery_result)
    result = celery_result.get(timeout=10)
    print("=== api - v1 - core - celery - result ===")
    print(result)
    return {"result": result}


async def get_token_payload(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(MicrosoftGuard(scopes=["api.read"], roles=["User"]))
    ),
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
