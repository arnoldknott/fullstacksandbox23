from core.databases import get_async_session
from fastapi import Depends, HTTPException
from models.demo_resource import DemoResource, DemoResourceIn
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# from sqlalchemy.future import select


class DemoResourceCRUD:
    """Create, Read, Update, Delete operations for demo resources in database."""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Provides a database session for CRUD operations."""
        self.session = session

    async def create_resource(self, resource: DemoResourceIn) -> DemoResource:
        """Creates a new resource."""
        database_resource = DemoResource(**resource.model_dump())
        self.session.add(database_resource)
        await self.session.commit()
        await self.session.refresh(database_resource)
        return database_resource

    async def read_resources(self) -> list[DemoResource]:
        """Returns all demo resources."""
        statement = select(DemoResource)
        response = await self.session.exec(statement)
        if response is None:
            raise HTTPException(status_code=404, detail="No resources found")
        return response.all()

    async def read_resource_by_id(self, resource_id: int) -> DemoResource:
        """Returns a demo resource by id."""
        resource = await self.session.get(DemoResource, resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource

    async def update_resource(self, resource: DemoResource) -> DemoResource:
        """Updates a demo resource."""
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def delete_resource(self, resource_id: int) -> DemoResource:
        """Deletes a demo resource."""
        statement = select(DemoResource).where(DemoResource.id == int(resource_id))
        result = await self.session.exec(statement)
        resource = result.first()
        self.session.delete(resource)
        await self.session.commit()
        return resource
