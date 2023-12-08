from core.databases import get_async_session
from fastapi import Depends
from models.demo_resource import DemoResource
from sqlalchemy.ext.asyncio import AsyncSession


async def create_resource(
    resource: DemoResource, session: AsyncSession = Depends(get_async_session)
) -> DemoResource:
    """Creates a new resource."""
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    return resource
