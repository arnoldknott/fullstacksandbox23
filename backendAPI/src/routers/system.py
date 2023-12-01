import logging

from config import config
from fastapi import APIRouter

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


@router.get("/config")
async def get_config():
    """Returns the configuration of the backendAPI."""
    logger.info("Config check")
    return {
        "TEST_SECRET1": config.TEST_SECRET1,
        "TEST_SECRET2": config.TEST_SECRET2,
    }
