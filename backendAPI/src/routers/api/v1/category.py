import logging

from crud.category import CategoryCRUD
from fastapi import APIRouter
from models.category import Category, CategoryCreate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)
async def post_category(
    category: CategoryCreate,
) -> Category:
    """Creates a new category."""
    logger.info("POST category")
    async with CategoryCRUD() as crud:
        created_category = await crud.create(category)
    return created_category
