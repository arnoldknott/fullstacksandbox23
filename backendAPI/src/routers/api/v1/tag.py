import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from core.security import Guards, get_http_access_token_payload
from core.types import GuardTypes
from crud.tag import TagCRUD
from models.tag import Tag, TagCreate, TagRead, TagUpdate

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

tag_view = BaseView(TagCRUD)


@router.post("/", status_code=201)
async def post_tag(
    tag: TagCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> Tag:
    """Creates a new tag."""
    return await tag_view.post_with_public_access(
        tag,
        token_payload,
        guards,
        # scopes=["api.write"],
        # roles=["User"],
    )


@router.get("/", status_code=200)
async def get_tags() -> list[TagRead]:
    """Returns all tags."""
    return await tag_view.get()


@router.get("/{tag_id}", status_code=200)
async def get_tag_by_id(
    tag_id: UUID,
) -> TagRead:
    """Returns a tag."""
    return await tag_view.get_by_id(tag_id)


@router.put("/{tag_id}", status_code=200)
async def put_tag(
    tag_id: UUID,
    tag: TagUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> Tag:
    """Updates a tag."""
    return await tag_view.put(
        tag_id,
        tag,
        token_payload,
        guards,
        # roles=["User"],
        # scopes=["api.write"],
    )


@router.delete("/{tag_id}", status_code=200)
async def delete_tag(
    tag_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:  # Tag:
    """Deletes a tag."""
    return await tag_view.delete(
        tag_id,
        token_payload,
        guards,  # roles=["User"], scopes=["api.write"]
    )
