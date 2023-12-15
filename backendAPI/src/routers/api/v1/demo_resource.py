import logging
from typing import List

from core.databases import get_async_session
from crud.demo_resource import DemoResourceCRUD
from fastapi import APIRouter, Depends
from models.demo_resource import DemoResource, DemoResourceIn
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)  # change to 201 - this is just to try the tests!
async def post_demo_resource(
    demo_resource: DemoResourceIn, session: AsyncSession = Depends(get_async_session)
) -> DemoResource:
    """Creates a new demo resource."""
    logger.info("POST demo resource")
    crud = DemoResourceCRUD(session)
    created_demo_resource = await crud.create_resource(demo_resource)
    return created_demo_resource


# Let the tests fail first!
@router.get("/")
async def get_demo_resource(
    session: AsyncSession = Depends(get_async_session),
) -> List[DemoResource]:
    """Returns all demo resource."""
    logger.info("GET all demo resource")
    # return [{"description": "ok"}]
    crud = DemoResourceCRUD(session)
    response = await crud.read_resources()
    return response


# @router.get("/{resource_id}")
# async def get_demo_resource(
#     resource_id: int, session: AsyncSession = Depends(get_async_session)
# ) -> DemoResource:
#     """Returns a demo resource."""
#     logger.info("GET demo resource")
#     crud = DemoResourceCRUD(session)
#     response = crud.read_resource_by_id(resource_id)
#     return response


# @router.put("/{resource_id}")

# @router.delete("/{resource_id}")
