import logging
from uuid import UUID
from typing import Annotated, Any, Optional, cast

from fastapi import APIRouter, Depends, HTTPException

from core.security import (
    Guards,
    check_token_against_guards,
    get_http_access_token_payload,
    provide_http_token_payload,
)
from core.types import GuardTypes
from crud.presentation import PresentationCRUD
from models.presentation import (
    Presentation,
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
    validate_endpoint_path,
)

# from models import PresentationCreate, PresentationRead, PresentationUpdate
from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

presentation_view = BaseView(PresentationCRUD)


# region Presentation


@router.post("/", status_code=201)
async def post_presentation(
    presentation: PresentationCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> PresentationRead:
    """Creates a new presentation."""
    return await presentation_view.post(presentation, token_payload, guards)


@router.get("/", status_code=200)
async def get_presentations(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[PresentationRead]:
    """Returns all presentations."""
    return await presentation_view.get(token_payload, guards)


@router.get("/{resource_id}", status_code=200)
async def get_presentation_by_id(
    resource_id: UUID,
    token_payload: Annotated[
        Optional[dict], Depends(provide_http_token_payload)
    ] = None,
) -> PresentationRead:
    """Returns a presentation by resource_id."""
    return await presentation_view.get_by_id(resource_id, token_payload, guards=None)


@router.get("/path/{path:path}", status_code=200)
async def get_presentation_by_path(
    path: str,
    token_payload: Annotated[
        Optional[dict], Depends(provide_http_token_payload)
    ] = None,
) -> PresentationRead:
    """Returns a presentation by path."""
    current_user = None
    if token_payload:
        current_user = await check_token_against_guards(token_payload, guards=None)

    # Normalize to leading slash so "/a/b" and "a/b" resolve consistently.
    normalized_path = path if path.startswith("/") else f"/{path}"

    async with PresentationCRUD() as crud:
        validated_path = validate_endpoint_path(normalized_path)
        presentation_path = cast(Any, getattr(Presentation, "path"))
        by_path = await crud.read(
            current_user=current_user,
            filters=[presentation_path == validated_path],
            limit=1,
        )
        return by_path[0]


# TBD: redesign to remove the public endpooint and
# make authentication optional in the get_by_id method
# First try with authentication if provided
# if not straight go to fetching the presentation without authentication and return it if it is public
# Also allow filtering for path instead / before UUID from resource_id
# @router.get("/public/{resource_id}", status_code=200)
# async def get_public_presentation_by_id(
#     resource_id: UUID,
# ) -> PresentationRead:
#     """Returns a public presentation without authentication."""
#     return await presentation_view.get_by_id(
#         resource_id, token_payload=None, guards=None
#     )


@router.put("/{resource_id}", status_code=200)
async def put_presentation(
    resource_id: UUID,
    presentation: PresentationUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> PresentationRead:
    """Updates a presentation."""
    return await presentation_view.put(resource_id, presentation, token_payload, guards)


@router.delete("/{resource_id}", status_code=200)
async def delete_presentation(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> None:
    """Deletes a presentation."""
    return await presentation_view.delete(resource_id, token_payload, guards)


# endregion Presentation
