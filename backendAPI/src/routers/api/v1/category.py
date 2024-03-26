import logging
import uuid

# from typing import List
from fastapi import APIRouter, Depends, HTTPException

from core.security import get_access_token_payload
from .base import BaseView

from crud.category import CategoryCRUD

from models.category import Category, CategoryCreate, CategoryUpdate, CategoryRead
from models.demo_resource import DemoResource

logger = logging.getLogger(__name__)
router = APIRouter()

category_view = BaseView(CategoryCRUD, Category)

# # TBD delete version before refactoring:
# @router.post("/", status_code=201)
# async def post_category(
#     category: CategoryCreate,
# ) -> Category:
#     """Creates a new category."""
#     logger.info("POST category")
#     async with CategoryCRUD() as crud:
#         created_category = await crud.create(category)
#     return created_category


@router.post("/", status_code=201)
async def post_category(
    category: CategoryCreate,
    token_payload=Depends(get_access_token_payload),
) -> Category:
    """Creates a new category."""
    return await category_view.post(
        category,
        token_payload,
        scopes=["api.write"],
        roles=["User"],
    )


# # TBD delete version before refactoring:
# @router.get("/", status_code=200)
# async def get_all_categories() -> List[Category]:
#     """Returns all categories."""
#     logger.info("GET all categories")
#     async with CategoryCRUD() as crud:
#         response = await crud.read_all()
#     return response

# @router.get("/{category_id}")
# async def get_category_by_id(category_id: str) -> Category:
#     """Returns a category."""
#     logger.info("GET category")
#     try:
#         category_id = uuid.UUID(category_id)
#     except ValueError:
#         logger.error("Category ID is not a universal unique identifier (uuid).")
#         raise HTTPException(status_code=400, detail="Invalid category id")
#     async with CategoryCRUD() as crud:
#         response = await crud.read_by_id(category_id)
#     return response


@router.get("/", status_code=200)
async def get_categories(
    token_payload=Depends(get_access_token_payload),
) -> list[CategoryRead]:
    """Returns all protected resources."""
    return await category_view.get(
        token_payload,
        roles=["User"],
    )


@router.get("/{category_id}", status_code=200)
async def get_category_by_id(
    category_id: str,
    token_payload=Depends(get_access_token_payload),
) -> CategoryRead:
    """Returns a protected resource."""
    return await category_view.get_by_id(
        category_id,
        token_payload,
        roles=["User"],
    )


# # TBD delete version before refactoring:
# @router.put("/{category_id}")
# async def update_category(
#     category_id: str,
#     category: CategoryUpdate,
# ) -> Category:
#     """Updates a category."""
#     logger.info("PUT category")
#     try:
#         category_id = uuid.UUID(category_id)
#     except ValueError:
#         logger.error("Category ID is not a universal unique identifier (uuid).")
#         raise HTTPException(status_code=400, detail="Invalid category id")
#     async with CategoryCRUD() as crud:
#         old_category = await crud.read_by_id(category_id)
#         response = await crud.update(old_category, category)
#     return response


@router.put("/{category_id}", status_code=200)
async def put_category(
    category_id: str,
    category: CategoryUpdate,
    token_payload=Depends(get_access_token_payload),
) -> Category:
    """Updates a category."""
    return await category_view.put(
        category_id,
        category,
        token_payload,
        roles=["User"],
        scopes=["api.write"],
    )


# @router.delete("/{category_id}")
# async def delete_category(category_id: str) -> Category:
#     """Deletes a category."""
#     logger.info("DELETE category")
#     try:
#         category_id = uuid.UUID(category_id)
#     except ValueError:
#         logger.error("Category ID is not a universal unique identifier (uuid).")
#         raise HTTPException(status_code=400, detail="Invalid category id")
#     async with CategoryCRUD() as crud:
#         response = await crud.delete(category_id)
#     return response


@router.delete("/{category_id}", status_code=200)
async def delete_category(
    category_id: str,
    token_payload=Depends(get_access_token_payload),
) -> Category:
    """Deletes a protected resource."""
    return await category_view.delete(
        category_id, token_payload, roles=["User"], scopes=["api.write"]
    )


# TBD: refactor to updated access protection
@router.get("/{category_id}/demoresources")
async def get_all_demo_resources_in_category(category_id: str) -> list[DemoResource]:
    """Returns all demo resources within category."""
    logger.info("GET all demo resources within category")
    try:
        category_id = uuid.UUID(category_id)
    except ValueError:
        logger.error("Category ID is not a universal unique identifier (uuid).")
        raise HTTPException(status_code=400, detail="Invalid category id")
    async with CategoryCRUD() as crud:
        response = await crud.read_all_demo_resources(category_id)
    return response
