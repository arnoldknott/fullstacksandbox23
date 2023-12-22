import logging
from typing import Annotated, List

from crud.category import CategoryCRUD
from crud.demo_resource import DemoResourceCRUD
from fastapi import APIRouter, HTTPException, Query
from models.demo_resource import (
    DemoResource,
    DemoResourceCreate,
    DemoResourceRead,
    DemoResourceUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)  # change to 201 - this is just to try the tests!
async def post_demo_resource(
    demo_resource: DemoResourceCreate,
) -> DemoResource:
    """Creates a new demo resource."""
    logger.info("POST demo resource")
    print("=== demo_resource.category_id ===")
    print(demo_resource.category_id)
    if demo_resource.category_id:
        async with CategoryCRUD() as crud:
            await crud.read_by_id(demo_resource.category_id)
    async with DemoResourceCRUD() as crud:
        created_demo_resource = await crud.create(demo_resource)
    return created_demo_resource
    # crud = DemoResourceCRUD()
    # created_demo_resource = await crud.create(demo_resource)
    # return created_demo_resource


@router.get("/")
async def get_all_demo_resources() -> List[DemoResource]:
    """Returns all demo resource."""
    logger.info("GET all demo resource")
    async with DemoResourceCRUD() as crud:
        response = await crud.read_all()
    # crud = DemoResourceCRUD()
    # response = await crud.read_all()
    return response


@router.get("/{resource_id}")
async def get_demo_resource_by_id(resource_id: str) -> DemoResourceRead:
    """Returns a demo resource."""
    logger.info("GET demo resource")
    # crud = DemoResourceCRUD()
    try:
        resource_id = int(resource_id)
    except ValueError:
        logger.error("Resource ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid resource id")
    async with DemoResourceCRUD() as crud:
        response = await crud.read_by_id_with_childs(resource_id)
    return response


@router.put("/{resource_id}")
async def update_demo_resource(
    resource_id: str,
    demo_resource: DemoResourceUpdate,
) -> DemoResource:
    """Updates a demo resource."""
    logger.info("PUT demo resource")
    # print("=== demo_resource ===")
    # print(demo_resource)
    # crud = DemoResourceCRUD()
    try:
        resource_id = int(resource_id)
    except ValueError:
        logger.error("Resource ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid resource id")
    async with DemoResourceCRUD() as crud:
        old_resource = await crud.read_by_id(resource_id)
        updated_resource = await crud.update(old_resource, demo_resource)
    return updated_resource


@router.delete("/{resource_id}")
async def delete_demo_resource(resource_id: str) -> DemoResource:
    """Deletes a demo resource."""
    logger.info("DELETE demo resource")
    # crud = DemoResourceCRUD()
    try:
        resource_id = int(resource_id)
    except ValueError:
        logger.error("Resource ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid resource id")
    async with DemoResourceCRUD() as crud:
        result = await crud.delete(resource_id)
    # print("=== result ===")
    # print(result)
    return result


@router.post("/{resource_id}/tag/")
async def add_tag_to_demo_resource(
    resource_id: str,
    tag_ids: Annotated[
        List[int], Query()
    ],  # TBD: move the arguments from Query to json!
) -> DemoResourceRead:
    """Adds a tag to a demo resource."""
    logger.info("POST demo resource")
    try:
        resource_id = int(resource_id)
    except ValueError:
        logger.error("Resource ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid resource id")
    # sShould not be necessary, as FastAPI should do this automatically
    # try:
    #     tag_ids = int(tag_id)
    # except ValueError:
    #     logger.error("Tag ID is not an integer")
    #     raise HTTPException(status_code=400, detail="Invalid tag id")
    async with DemoResourceCRUD() as crud:
        result = await crud.add_tag(resource_id, tag_ids)
    return result
