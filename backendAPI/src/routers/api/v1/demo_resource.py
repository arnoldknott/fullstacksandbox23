import logging
import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException

from core.security import get_access_token_payload
from .base import BaseView

from .category import get_category_by_id
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

demo_resource_view = BaseView(DemoResourceCRUD, DemoResource)

# TBD: remove old version from before refactoring:
# @router.post("/", status_code=201)
# async def post_demo_resource(
#     demo_resource: DemoResourceCreate,
# ) -> DemoResource:
#     """Creates a new demo resource."""
#     logger.info("POST demo resource")
#     # print("=== demo_resource.category_id ===")
#     # print(demo_resource.category_id)
#     if demo_resource.category_id:
#         async with CategoryCRUD() as crud:
#             await crud.read_by_id(demo_resource.category_id)
#     async with DemoResourceCRUD() as crud:
#         created_demo_resource = await crud.create(demo_resource)
#     return created_demo_resource
#     # crud = DemoResourceCRUD()


# Post requires a user!
@router.post("/", status_code=201)
async def post_category(
    demo_resource: DemoResourceCreate,
    token_payload=Depends(get_access_token_payload),
) -> DemoResource:
    """Creates a new demo resource."""
    demo_resource_db = await demo_resource_view.post(
        demo_resource,
        token_payload,
        scopes=["api.write"],
        roles=["User"],
    )
    if demo_resource_db.category_id:
        await get_category_by_id(demo_resource_db.category_id, token_payload)
    return demo_resource_db


# TBD: remove old version from before refactoring:
# @router.get("/")
# async def get_all_demo_resources() -> List[DemoResource]:
#     """Returns all demo resource."""
#     logger.info("GET all demo resource")
#     async with DemoResourceCRUD() as crud:
#         response = await crud.read_all()
#     # crud = DemoResourceCRUD()
#     # response = await crud.read_all()
#     return response


# @router.get("/{resource_id}")
# async def get_demo_resource_by_id(resource_id: str) -> DemoResourceRead:
#     """Returns a demo resource."""
#     logger.info("GET demo resource")
#     # crud = DemoResourceCRUD()
#     try:
#         resource_id = uuid.UUID(resource_id)
#     except ValueError:
#         logger.error("Resource ID is not a universal unique identifier (uuid).")
#         raise HTTPException(status_code=400, detail="Invalid resource id")
#     async with DemoResourceCRUD() as crud:
#         response = await crud.read_by_id_with_childs(resource_id)
#     return response


# The get functions are totally public
# TBD: still a policy is needed for the fine grained access control to make the resource public!
# The default create only grants "own" access to the user, how creates it!
@router.get("/", status_code=200)
async def get_categories(
    # token_payload=Depends(get_access_token_payload),
) -> list[DemoResourceRead]:
    """Returns all protected resources."""
    return await demo_resource_view.get(
        # token_payload,
        # roles=["User"],
    )


@router.get("/{demo_resource_id}", status_code=200)
async def get_demo_resource_by_id(
    demo_resource_id: str,
    # token_payload=Depends(get_access_token_payload),
) -> DemoResourceRead:
    """Returns a demo resource."""
    return await demo_resource_view.get_by_id(
        demo_resource_id,
        # token_payload,
        # roles=["User"],
    )


# TBD: remove the old version after refactoring:
# @router.put("/{resource_id}")
# async def update_demo_resource(
#     resource_id: str,
#     demo_resource: DemoResourceUpdate,
# ) -> DemoResource:
#     """Updates a demo resource."""
#     logger.info("PUT demo resource")
#     # print("=== demo_resource ===")
#     # print(demo_resource)
#     # crud = DemoResourceCRUD()
#     try:
#         resource_id = uuid.UUID(resource_id)
#     except ValueError:
#         logger.error("Resource ID is not a universal unique identifier (uuid).")
#         raise HTTPException(status_code=400, detail="Invalid resource id")
#     async with DemoResourceCRUD() as crud:
#         old_resource = await crud.read_by_id(resource_id)
#         updated_resource = await crud.update(old_resource, demo_resource)
#     return updated_resource


@router.put("/{demo_resource_id}", status_code=200)
async def put_category(
    demo_resource_id: str,
    demo_resource: DemoResourceUpdate,
    token_payload=Depends(get_access_token_payload),
) -> DemoResource:
    """Updates a category."""
    return await demo_resource_view.put(
        demo_resource_id,
        demo_resource,
        token_payload,
        roles=["User"],
        scopes=["api.write"],
    )


# # TBD: remove the old version after refactoring:
# @router.delete("/{resource_id}")
# async def delete_demo_resource(resource_id: str) -> DemoResource:
#     """Deletes a demo resource."""
#     logger.info("DELETE demo resource")
#     # crud = DemoResourceCRUD()
#     try:
#         resource_id = uuid.UUID(resource_id)
#     except ValueError:
#         logger.error("Resource ID is not a universal unique identifier (uuid).")
#         raise HTTPException(status_code=400, detail="Invalid resource id")
#     async with DemoResourceCRUD() as crud:
#         result = await crud.delete(resource_id)
#     # print("=== result ===")
#     # print(result)
#     return result


@router.delete("/{demo_resource_id}", status_code=200)
async def delete_demo_resource(
    demo_resource_id: str,
    token_payload=Depends(get_access_token_payload),
) -> DemoResource:
    """Deletes a protected resource."""
    return await demo_resource_view.delete(
        demo_resource_id, token_payload, roles=["User"], scopes=["api.write"]
    )


# TBD: refactor into using the new BaseView - but this is a link table,
# so probably base view and base crud need a new method for linking.
# This method should then be reusable for all link tables:
# like sharing, tagging, creating hierarchies etc.
@router.post("/{resource_id}/tag/")
async def add_tag_to_demo_resource(
    resource_id: str,
    tag_ids: Annotated[
        List[uuid.UUID], Query()
    ],  # TBD: move the arguments from Query to json!
) -> DemoResourceRead:
    """Adds a tag to a demo resource."""
    logger.info("POST demo resource")
    try:
        resource_id = uuid.UUID(resource_id)
    except ValueError:
        logger.error("Resource ID is not a universal unique identifier (uuid).")
        raise HTTPException(status_code=400, detail="Invalid resource id")
    # sShould not be necessary, as FastAPI should do this automatically
    # try:
    #     tag_ids = uuid.UUID(tag_id)
    # except ValueError:
    #     logger.error("Tag ID is not a universal unique identifier (uuid).")
    #     raise HTTPException(status_code=400, detail="Invalid tag id")
    async with DemoResourceCRUD() as crud:
        result = await crud.add_tag(resource_id, tag_ids)
    return result
