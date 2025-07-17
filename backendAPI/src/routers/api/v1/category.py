import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from core.security import Guards, get_http_access_token_payload
from core.types import GuardTypes
from crud.category import CategoryCRUD
from models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

category_view = BaseView(CategoryCRUD)


@router.post("/", status_code=201)
async def post_category(
    category: CategoryCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> Category:
    """Creates a new category."""
    return await category_view.post(
        category,
        token_payload,
        guards,
        # scopes=["api.write"],
        # roles=["User"],
    )


@router.get("/", status_code=200)
async def get_categories(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[CategoryRead]:
    """Returns all category."""
    return await category_view.get(
        token_payload,
        guards,
        # roles=["User"],
    )


@router.get("/{category_id}", status_code=200)
async def get_category_by_id(
    category_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> CategoryRead:
    """Returns a category."""
    return await category_view.get_by_id(category_id, token_payload, guards)


@router.put("/{category_id}", status_code=200)
async def put_category(
    category_id: UUID,
    category: CategoryUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> Category:
    """Updates a category."""
    return await category_view.put(category_id, category, token_payload, guards)


@router.delete("/{category_id}", status_code=200)
async def delete_category(
    category_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:  # Category:
    """Deletes a category."""
    return await category_view.delete(category_id, token_payload, guards)
