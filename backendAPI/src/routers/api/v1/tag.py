import logging
import uuid

from crud.tag import TagCRUD
from fastapi import APIRouter, HTTPException
from models.demo_resource import DemoResource
from models.tag import Tag, TagCreate, TagUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)
async def post_tag(
    tag: TagCreate,
) -> Tag:
    """Creates a new tag."""
    logger.info("POST tag")
    async with TagCRUD() as crud:
        created_tag = await crud.create(tag)
    return created_tag


@router.get("/", status_code=200)
async def get_all_tags() -> list[Tag]:
    """Returns all tags."""
    logger.info("GET all tags")
    async with TagCRUD() as crud:
        response = await crud.read_all()
    return response


@router.get("/{tag_id}")
async def get_tag_by_id(tag_id: str) -> Tag:
    """Returns a tag."""
    logger.info("GET tag")
    try:
        tag_id = uuid.UUID(tag_id)
    except ValueError:
        logger.error("Tag ID is not a universal unique identifier (uuid).")
        raise HTTPException(status_code=400, detail="Invalid tag id")
    async with TagCRUD() as crud:
        response = await crud.read_by_id(tag_id)
    return response


@router.put("/{tag_id}")
async def update_tag(
    tag_id: str,
    tag: TagUpdate,
) -> Tag:
    """Updates a tag."""
    logger.info("PUT tag")
    try:
        tag_id = uuid.UUID(tag_id)
    except ValueError:
        logger.error("Tag ID is not a universal unique identifier (uuid).")
        raise HTTPException(status_code=400, detail="Invalid tag id")
    async with TagCRUD() as crud:
        old_tag = await crud.read_by_id(tag_id)
        response = await crud.update(old_tag, tag)
    return response


@router.delete("/{tag_id}")
async def delete_tag(tag_id: str) -> Tag:
    """Deletes a tag."""
    logger.info("DELETE tag")
    try:
        tag_id = uuid.UUID(tag_id)
    except ValueError:
        logger.error("Tag ID is not a universal unique identifier (uuid).")
        raise HTTPException(status_code=400, detail="Invalid tag id")
    async with TagCRUD() as crud:
        response = await crud.delete(tag_id)
    return response


@router.get("/{tag_id}/demo_resources")
async def get_all_demo_resources_for_tag(tag_id: str) -> list[DemoResource]:
    """Returns all demo resources with tag."""
    logger.info("GET all demo resources with tag")
    try:
        tag_id = uuid.UUID(tag_id)
    except ValueError:
        logger.error("Tag ID is not a universal unique identifier (uuid).")
        raise HTTPException(status_code=400, detail="Invalid tag id")
    async with TagCRUD() as crud:
        response = await crud.read_all_demo_resources(tag_id)
    return response
