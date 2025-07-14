import logging
from uuid import UUID

from fastapi import APIRouter

from crud.public_resource import PublicResourceCRUD
from models.public_resource import (
    PublicResource,
    PublicResourceCreate,
    PublicResourceRead,
    PublicResourceUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)
async def post_protected_resource(
    public_resource: PublicResourceCreate,
) -> PublicResource:
    """Creates a new public resource."""
    logger.info("POST public resource")
    async with PublicResourceCRUD() as crud:
        created_public_resource = await crud.create(public_resource)
    return created_public_resource


@router.get("/", status_code=200)
async def get_all_public_resources() -> list[PublicResourceRead]:
    """Returns all public_resources."""
    logger.info("GET all public_resources")
    async with PublicResourceCRUD() as crud:
        response = await crud.read_all()
    return response


@router.get("/{public_resource_id}", status_code=200)
async def get_public_resource_by_id(public_resource_id: UUID) -> PublicResourceRead:
    """Returns a public_resource."""
    logger.info("GET public_resource")
    async with PublicResourceCRUD() as crud:
        response = await crud.read_by_id(public_resource_id)
    return response


@router.put("/{public_resource_id}")
async def update_public_resource(
    public_resource_id: UUID,
    public_resource: PublicResourceUpdate,
) -> PublicResource:
    """Updates a public_resource."""
    logger.info("PUT public_resource")
    async with PublicResourceCRUD() as crud:
        old_public_resource = await crud.read_by_id(public_resource_id)
        response = await crud.update(old_public_resource, public_resource)
    return response


@router.delete("/{public_resource_id}")
async def delete_public_resource(public_resource_id: UUID) -> PublicResource:
    """Deletes a public_resource."""
    logger.info("DELETE public_resource")
    async with PublicResourceCRUD() as crud:
        response = await crud.delete(public_resource_id)
    return response
