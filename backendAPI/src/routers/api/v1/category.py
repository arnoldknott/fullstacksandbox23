import logging
from typing import List

from crud.category import CategoryCRUD
from fastapi import APIRouter, HTTPException
from models.category import Category, CategoryCreate, CategoryUpdate
from models.demo_resource import DemoResource

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


@router.get("/", status_code=200)
async def get_all_categories() -> List[Category]:
    """Returns all categories."""
    logger.info("GET all categories")
    async with CategoryCRUD() as crud:
        response = await crud.read_all()
    return response


@router.get("/{category_id}")
async def get_category_by_id(category_id: str) -> Category:
    """Returns a category."""
    logger.info("GET category")
    try:
        category_id = int(category_id)
    except ValueError:
        logger.error("Category ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid category id")
    async with CategoryCRUD() as crud:
        response = await crud.read_by_id(category_id)
    return response


@router.put("/{category_id}")
async def update_category(
    category_id: str,
    category: CategoryUpdate,
) -> Category:
    """Updates a category."""
    logger.info("PUT category")
    try:
        category_id = int(category_id)
    except ValueError:
        logger.error("Category ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid category id")
    async with CategoryCRUD() as crud:
        old_category = await crud.read_by_id(category_id)
        response = await crud.update(old_category, category)
    return response


@router.delete("/{category_id}")
async def delete_category(category_id: str) -> Category:
    """Deletes a category."""
    logger.info("DELETE category")
    try:
        category_id = int(category_id)
    except ValueError:
        logger.error("Category ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid category id")
    async with CategoryCRUD() as crud:
        response = await crud.delete(category_id)
    return response


@router.get("/{category_id}/demo_resources")
async def get_all_demo_resources_in_category(category_id: str) -> list[DemoResource]:
    """Returns all demo resources within category."""
    logger.info("GET all demo resources within category")
    try:
        category_id = int(category_id)
    except ValueError:
        logger.error("Category ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid category id")
    async with CategoryCRUD() as crud:
        response = await crud.read_all_demo_resources(category_id)
    return response
