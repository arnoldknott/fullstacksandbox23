import logging
from typing import Annotated

from core.security import validate_token
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def get_protected_resource(token: Annotated[str, Depends(validate_token)]):
    """Returns a protected resource."""
    logger.info("GET protected resource")
    return {"message": "Hello from a protected resource!"}
