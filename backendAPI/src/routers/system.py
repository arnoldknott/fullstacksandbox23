import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    """Returns a 200 OK."""
    logger.info("Health check")
    return {"status": "ok"}
