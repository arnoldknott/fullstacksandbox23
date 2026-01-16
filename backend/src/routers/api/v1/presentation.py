import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.security import (
    Guards,
    check_token_against_guards,
    get_http_access_token_payload,
)
from core.types import GuardTypes
from crud.presentation import PresentationCRUD
from models.presentation import (
    Presentation,
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
)

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

presentation_view = BaseView(PresentationCRUD)


# region Presentation

@router.post("/", status_code=201)
async def post_presentation(
    presentation: PresentationCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Presentation:
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
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> PresentationRead:
    """Returns a presentation."""
    return await presentation_view.get_by_id(resource_id, token_payload, guards)


@router.get("/public/{resource_id}", status_code=200)
async def get_public_presentation_by_id(
    resource_id: UUID,
) -> PresentationRead:
    """Returns a public presentation without authentication."""
    return await presentation_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/{resource_id}", status_code=200)
async def put_presentation(
    resource_id: UUID,
    presentation: PresentationUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Presentation:
    """Updates a presentation."""
    return await presentation_view.put(
        resource_id, presentation, token_payload, guards
    )


@router.delete("/{resource_id}", status_code=200)
async def delete_presentation(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> None:
    """Deletes a presentation."""
    return await presentation_view.delete(resource_id, token_payload, guards)


# endregion Presentation