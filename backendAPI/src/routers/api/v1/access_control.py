import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{subject}")
def get_course(subject: str):
    """Returns a subject."""
    logger.info("GET a course")
    return {"message": f"Hello from course {subject}!"}
