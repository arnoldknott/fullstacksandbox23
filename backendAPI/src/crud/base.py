from datetime import datetime
from typing import TYPE_CHECKING, Generic, Type, TypeVar

from core.databases import get_async_session
from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

# from core.security import AccessControl

if TYPE_CHECKING:
    pass
# from core.security import CurrentUserData


BaseModelType = TypeVar("BaseModelType", bound=SQLModel)
BaseSchemaTypeCreate = TypeVar("BaseSchemaTypeCreate", bound=SQLModel)
BaseSchemaTypeRead = TypeVar("BaseSchemaTypeRead", bound=SQLModel)
BaseSchemaTypeUpdate = TypeVar("BaseSchemaTypeUpdate", bound=SQLModel)


class BaseCRUD(
    Generic[
        BaseModelType,
        BaseSchemaTypeCreate,
        BaseSchemaTypeRead,
        BaseSchemaTypeUpdate,
    ]
):
    """Base class for CRUD operations."""

    def __init__(
        self,
        base_model: Type[BaseModelType],
        # current_user: Optional["CurrentUserData"] = None,# not good: don't store user_data in the CRUD class. only pass it around.
    ):
        """Provides a database session for CRUD operations."""
        self.session = None
        self.model = base_model
        # self.current_user: Optional["CurrentUserData"] = current_user

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def create(
        self,
        object: BaseSchemaTypeCreate,
        update_last_access: bool = True,  # Refactor: remove this parameter and make it part of the access control checks, as well as the access_logs_table
        # Refactor into this:
        # current_user: "CurrentUserData",
    ) -> BaseModelType:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write here
        """Creates a new object."""
        # print("=== BaseCRUD.create - current_user ===")
        # print(current_user)
        session = self.session
        Model = self.model
        # TBD: refactor into try-except block and add logging
        database_object = Model.model_validate(object)
        if hasattr(database_object, "last_accessed_at") and update_last_access is True:
            database_object.last_accessed_at = datetime.now()
        session.add(database_object)
        await session.commit()
        await session.refresh(database_object)
        return database_object

    # TBD: implement a create_if_not_exists method

    # TBD: add skip and limit
    # async def read_all(self, skip: int = 0, limit: int = 100)  -> list[BaseModelType]:
    # Changing to return BaseSchemaTypeRead instead of BaseModelType makes read_with_childs obsolete!
    async def read_all(self) -> list[BaseSchemaTypeRead]:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is read here
        """Returns all objects."""
        session = self.session
        model = self.model
        # TBD: refactor into try-except block and add logging
        statement = select(model)
        # statement = select(self.model).offset(skip).limit(limit)
        response = await session.exec(statement)
        if response is None:
            raise HTTPException(status_code=404, detail="No objects found")
        return response.all()

    # Changing to return BaseSchemaTypeRead instead of BaseModelType makes read_with_childs obsolete!
    async def read_by_id(
        self,
        object_id: int,
        update_last_access: bool = True,  # Refactor: remove this parameter and make it part of the access control checks, as well as the access_logs_table
        # Refactor into this:
        # current_user: "CurrentUserData",
    ) -> BaseSchemaTypeRead:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is read here
        """Returns an object by id."""
        session = self.session
        model = self.model
        object = await session.get(model, object_id)
        if object is None:
            raise HTTPException(status_code=404, detail="Object not found")
        if hasattr(object, "last_accessed_at") and update_last_access is True:
            model.last_accessed_at = datetime.now()
            session.add(object)
            await session.commit()
            await session.refresh(object)
        return object

    async def update(
        self,
        old: BaseModelType,
        new: BaseSchemaTypeUpdate,
        update_last_access: bool = True,  # Refactor: remove this parameter and make it part of the access control checks, as well as the access_logs_table
        # Refactor into this:
        # current_user: "CurrentUserData",
    ) -> BaseModelType:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write here
        """Updates an object."""
        session = self.session
        # TBD: refactor into try-except block and add logging
        if hasattr(old, "last_updated_at"):
            old.last_updated_at = datetime.now()
        if hasattr(old, "last_accessed_at") and update_last_access is True:
            old.last_accessed_at = datetime.now()
        updated = new.model_dump(exclude_unset=True)
        for key, value in updated.items():
            # if key == "id" or key == "created_at" or key == "last_updated_at":
            if (
                key == "created_at"
                or key == "last_updated_at"
                or key == "last_accessed_at"
            ):
                continue
            setattr(old, key, value)
        object = old
        session.add(object)
        await session.commit()
        await session.refresh(object)
        return object

    async def delete(self, object_id: int) -> BaseModelType:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write or delete here
        """Deletes an object."""
        session = self.session
        model = self.model
        # TBD: refactor into try-except block and add logging
        object = await session.get(model, object_id)
        if object is None:
            raise HTTPException(status_code=404, detail="Object not found")
        await session.delete(object)
        await session.commit()
        return object

    # TBD: add share / permission methods - maybe in an inherited class BaseCRUDPermissions?
