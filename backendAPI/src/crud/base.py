from typing import Generic, Type, TypeVar

from core.databases import get_async_session
from fastapi import Depends, HTTPException
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
        session: AsyncSession = Depends(get_async_session),
    ):
        """Provides a database session for CRUD operations."""
        self.session = session
        self.model = base_model

    async def create(self, object: BaseSchemaTypeCreate) -> BaseModelType:
        """Creates a new object."""
        session = self.session
        model = self.model
        # database_object = BaseModelType(**object.model_dump())
        # database_object = jsonable_encoder(object)
        database_object = model(**object.model_dump())
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
        for key, value in vars(new).items():  # .model_dump().items():
            if value is not None:
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

    # highly inspired by
    # https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/311939e6409d46c6547075095c051863c1cc0de2/src/backend/app/app/crud/base.py
    # async def get(
    #     self, id: Any, session: AsyncSession = Depends(get_async_session)
    # ) -> Optional[BaseModelType]:
    #     """Returns a model by id."""
    #     statement = select(self.model).where(self.model.id == id)
    #     result = await session.exec(statement)
    #     return result.first()

    # async def get_multi(
    #     self,
    #     *,
    #     skip: int = 0,
    #     limit: int = 100,
    #     session: AsyncSession = Depends(get_async_session)
    # ) -> List[BaseModelType]:
    #     """Returns multiple models."""
    #     statement = select(self.model).offset(skip).limit(limit)
    #     result = await session.exec(statement)
    #     return result.all()

    # async def create(
    #     self,
    #     *,
    #     obj_in: BaseSchemaTypeCreate,
    #     session: AsyncSession = Depends(get_async_session)
    # ) -> BaseModelType:
    #     """Creates a new model."""
    #     obj_in_data = jsonable_encoder(obj_in)
    #     db_obj = self.model(**obj_in_data)
    #     session.add(db_obj)
    #     await session.commit()
    #     await session.refresh(db_obj)
    #     return db_obj

    # async def update(
    #     self,
    #     *,
    #     db_obj: BaseModelType,
    #     obj_in: Union[BaseSchemaTypeUpdate, Dict[str, Any]],
    #     session: AsyncSession = Depends(get_async_session)
    # ) -> BaseModelType:
    #     """Updates a model."""
    #     obj_data = jsonable_encoder(db_obj)
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
    #     for field in obj_data:
    #         if field in update_data:
    #             setattr(db_obj, field, update_data[field])
    #     session.add(db_obj)
    #     await session.commit()
    #     await session.refresh(db_obj)
    #     return db_obj

    # async def delete(
    #     self, *, id: int, session: AsyncSession = Depends(get_async_session)
    # ) -> BaseModelType:
    #     """Deletes a model."""
    #     obj = await session.get(self.model, id)
    #     session.delete(obj)
    #     await session.commit()
    #     return obj
