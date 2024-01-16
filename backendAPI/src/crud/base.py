from datetime import datetime
from typing import Generic, Type, TypeVar

from core.databases import get_async_session
from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

BaseModelType = TypeVar("BaseModelType", bound=SQLModel)
BaseSchemaTypeCreate = TypeVar("BaseSchemaTypeCreate", bound=SQLModel)
BaseSchemaTypeUpdate = TypeVar("BaseSchemaTypeUpdate", bound=SQLModel)


class BaseCRUD(Generic[BaseModelType, BaseSchemaTypeCreate, BaseSchemaTypeUpdate]):
    """Base class for CRUD operations."""

    def __init__(
        self,
        base_model: Type[BaseModelType],
    ):
        """Provides a database session for CRUD operations."""
        self.session = None
        self.model = base_model

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def create(self, object: BaseSchemaTypeCreate) -> BaseModelType:
        """Creates a new object."""
        session = self.session
        Model = self.model
        database_object = Model.model_validate(object)
        session.add(database_object)
        await session.commit()
        await session.refresh(database_object)
        return database_object

    # TBD: add skip and limit
    # async def read_all(self, skip: int = 0, limit: int = 100)  -> list[BaseModelType]:
    async def read_all(self) -> list[BaseModelType]:
        """Returns all objects."""
        session = self.session
        model = self.model
        statement = select(model)
        # statement = select(self.model).offset(skip).limit(limit)
        response = await session.exec(statement)
        if response is None:
            raise HTTPException(status_code=404, detail="No objects found")
        return response.all()

    async def read_by_id(self, object_id: int) -> BaseModelType:
        """Returns an object by id."""
        session = self.session
        model = self.model
        object = await session.get(model, object_id)
        if object is None:
            raise HTTPException(status_code=404, detail="Object not found")
        return object

    async def update(
        self, old: BaseModelType, new: BaseSchemaTypeUpdate
    ) -> BaseModelType:
        """Updates an object."""
        session = self.session
        if hasattr(old, "last_updated_at"):
            old.last_updated_at = datetime.now()
        updated = new.model_dump(exclude_unset=True)
        for key, value in updated.items():
            if key == "id" or key == "created_at" or key == "updated_at":
                continue
            setattr(old, key, value)
        object = old
        session.add(object)
        await session.commit()
        await session.refresh(object)
        return object

    async def delete(self, object_id: int) -> BaseModelType:
        """Deletes an object."""
        session = self.session
        model = self.model
        object = await session.get(model, object_id)
        if object is None:
            raise HTTPException(status_code=404, detail="Object not found")
        await session.delete(object)
        await session.commit()
        return object
