from core.databases import get_async_session
from fastapi import Depends, HTTPException
from models.demo_resource import DemoResource, DemoResourceCreate, DemoResourceUpdate
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# from sqlalchemy.future import select


# class DemoResourceCRUD(BaseCRUD[DemoResource, DemoResourceCreate, DemoResourceUpdate]):
class DemoResourceCRUD:
    """Create, Read, Update, Delete operations for demo resources in database."""

    # pass

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Provides a database session for CRUD operations."""
        self.session = session

    async def create(self, resource: DemoResourceCreate) -> DemoResource:
        """Creates a new resource."""
        database_resource = DemoResource(**resource.model_dump())
        self.session.add(database_resource)
        await self.session.commit()
        await self.session.refresh(database_resource)
        return database_resource

    async def read(self) -> list[DemoResource]:
        """Returns all demo resources."""
        statement = select(DemoResource)
        response = await self.session.exec(statement)
        if response is None:
            raise HTTPException(status_code=404, detail="No resources found")
        return response.all()

    async def read_by_id(self, resource_id: int) -> DemoResource:
        """Returns a demo resource by id."""
        resource = await self.session.get(DemoResource, resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        return resource

    async def update(self, old: DemoResource, new: DemoResourceUpdate) -> DemoResource:
        """Updates a demo resource."""
        for key, value in vars(new).items():  # .model_dump().items():
            if value is not None:
                setattr(old, key, value)
        resource = old
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def delete(self, resource_id: int) -> DemoResource:
        """Deletes a demo resource."""
        resource = await self.session.get(DemoResource, resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        await self.session.delete(resource)
        await self.session.commit()
        return resource
