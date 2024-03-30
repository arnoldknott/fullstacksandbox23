import uuid
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Generic, Type, TypeVar, Optional, List

from models.access import AccessPolicy, AccessLogCreate
from crud.access import AccessPolicyCRUD, AccessLoggingCRUD
from core.databases import get_async_session
from core.access import AccessControl
from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


if TYPE_CHECKING:
    pass
from core.types import CurrentUserData, Action, ResourceType, IdentityType

logger = logging.getLogger(__name__)

# access_control = core.access_control.AccessControl()
# access_control = AccessControl()
read = Action.read
write = Action.write
own = Action.own

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
        # TBD: consider moving this to the access_control as an override and method specific parameter
        # The endpoints can still be protected by token claims individually - just add roles, scope or groups requirement to the endpoint
    ):
        """Provides a database session for CRUD operations."""
        self.session = None
        self.model = base_model
        if base_model.__name__ in ResourceType.list():
            self.resource_type = ResourceType(base_model.__name__)
        elif base_model.__name__ in IdentityType.list():
            self.resource_type = IdentityType(base_model.__name__)
        else:
            raise ValueError(
                f"{base_model.__name__} is not a valid ResourceType or IdentityType"
            )
        self.policy_CRUD = AccessPolicyCRUD()
        self.access_control = AccessControl(self.policy_CRUD)
        self.logging_CRUD = AccessLoggingCRUD()

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def __write_log(
        self,
        object_id: uuid.UUID,
        action: Action,
        current_user: "CurrentUserData",
        status_code: int,
    ):
        """Creates an access log entry."""
        access_log = AccessLogCreate(
            resource_id=object_id,
            resource_type=self.resource_type,
            action=action.value,
            # if public access, current_user is None
            identity_id=current_user.user_id if current_user else None,
            identity_type=IdentityType.user if current_user else None,
            status_code=status_code,
        )
        async with self.logging_CRUD as logging_CRUD:
            await logging_CRUD.log_access(access_log)

    async def create(
        self,
        object: BaseSchemaTypeCreate,
        # Refactor into this - no longer Optional: create only allowed for authenticated users!
        current_user: "CurrentUserData",
    ) -> BaseModelType:
        """Creates a new object."""
        logger.info("BaseCRUD.create")
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write here
        try:
            # TBD: remove the self.public completely - all handled by fine grained access control now.
            # For public, there's a public override in the access control checks.
            # print("=== BaseCRUD.create - current_user ===")
            # print(current_user)
            # print("=== BaseCRUD.create - type(current_user) ===")
            # print(type(current_user))
            # Not necessary here - anybody how passed the endpoint guards can create anything!
            # But use this protection for all read, update and delete methods!
            # Remove the public and refactor, e.g. for the demo resource to create as public -
            # see second session.add() comment below
            # if not await self.access_control.allows(
            #     user=current_user,
            #     resource_type=self.resource_type,
            #     action=write,
            # ):
            #     raise HTTPException(status_code=403, detail="Access denied")
            session = self.session
            Model = self.model
            database_object = Model.model_validate(object)
            # TBD: refactor into access control
            # if hasattr(database_object, "last_accessed_at") and update_last_access is True:
            #     database_object.last_accessed_at = datetime.now()
            session.add(database_object)
            await session.commit()
            await session.refresh(database_object)
            # No: this crud does not allow creation without current_user: make current_user mandatory"
            access_policy = AccessPolicy(
                resource_id=database_object.id,
                resource_type=self.resource_type,
                action=own,
                identity_id=current_user.user_id,
                identity_type=IdentityType.user,
            )
            # requires hierarchy checks to be in place: otherwise a user can never create a resource
            # as the AccessPolicy CRUD create checks, if the user is owner of the resource (that's not created yet)
            # needs to be fixed in the core access control by implementing a hierarchy check
            async with self.policy_CRUD as policy_CRUD:
                await policy_CRUD.create(access_policy, current_user)
            await self.__write_log(database_object.id, own, current_user, 201)
            return database_object
        except Exception as e:
            await self.__write_log(database_object.id, own, current_user, 404)
            logger.error(f"Error in BaseCRUD.create: {e}")
            raise HTTPException(status_code=404, detail="Object not found")

    # TBD: implement a create_if_not_exists method

    # use with pagination:
    # Model = await model_crud.read(order_by=[Model.name], limit=10)
    # Model = await model_crud.read(order_by=[Model.name], limit=10, offset=10)
    async def read(
        self,
        current_user: Optional["CurrentUserData"] = None,
        select_args: Optional[List] = None,
        filters: Optional[List] = None,
        joins: Optional[List] = None,
        order_by: Optional[List] = None,
        group_by: Optional[List] = None,
        having: Optional[List] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[BaseSchemaTypeRead]:
        """Generic read method with optional parameters for select_args, filters, joins, order_by, group_by, limit and offset."""

        access_conditions = self.access_control.filters_allowed(
            resource_type=self.resource_type,
            action=read,
            user=current_user,
        )
        if not access_conditions:
            statement = select(self.model if not select_args else select_args)
        else:
            statement = (
                select(self.model if not select_args else select_args)
                .join(AccessPolicy, self.model.id == AccessPolicy.resource_id)
                .where(*access_conditions)
            )

        if joins:
            for join in joins:
                statement = statement.join(join)

        if filters:
            for filter in filters:
                statement = statement.where(filter)

        if order_by:
            for order in order_by:
                statement = statement.order_by(order)

        if group_by:
            statement = statement.group_by(*group_by)

        if having:
            statement = statement.having(*having)

        if limit:
            statement = statement.limit(limit)

        if offset:
            statement = statement.offset(offset)

        # print("=== statement ===")
        # print(statement)

        response = await self.session.exec(statement)
        results = response.all()
        for result in results:
            await self.__write_log(result.id, own, current_user, 200)

        if not results:
            # print("=== self.model.__name__ ===")
            # print(self.model.__name__)
            # print("=== self.resource_type ===")
            # print(self.resource_type)
            logger.info(f"No objects found for {self.model.__name__}")
            for result in results:
                await self.__write_log(result.id, own, current_user, 404)
            raise HTTPException(
                status_code=404, detail=f"No {self.model.__name__} found."
            )

        return results

    # TBD: add skip and limit
    # async def read_all(self, skip: int = 0, limit: int = 100)  -> list[BaseModelType]:
    # Changing to return BaseSchemaTypeRead instead of BaseModelType makes read_with_childs obsolete!
    # async def read_all(
    #     self, current_user: Optional["CurrentUserData"] = None
    # ) -> list[BaseSchemaTypeRead]:
    #     return await self.read(current_user=current_user)
    #     # TBD: delete this method, as the default of the read() is the return_all()
    #     # TBD: add access control checks here:
    #     # request is known from self.current_user, object and method is read here
    #     """Returns all objects."""
    #     session = self.session
    #     model = self.model
    #     # TBD: refactor into try-except block and add logging
    #     # Fetch all access policies for the current user

    #     # TBD: delete the version from before refactoring:
    #     # statement = select(model)
    #     # TBD: Refactor into access control:
    #     join_conditions = self.access_control.filters_allowed(
    #         resource_type=self.resource_type,
    #         action=read,
    #         user=current_user,
    #     )
    #     statement = (
    #         select(model)
    #         .join(AccessPolicy, model.id == AccessPolicy.resource_id)
    #         .where(*join_conditions)
    #     )
    #     # statement = select(self.model).offset(skip).limit(limit)
    #     response = await session.exec(statement)
    #     if response is None:
    #         # TBD: add access logging here!
    #         raise HTTPException(status_code=404, detail="No objects found")
    #     # TBD: add access logging here!
    #     return response.all()

    # Changing to return BaseSchemaTypeRead instead of BaseModelType makes read_with_childs obsolete!
    # async def read_by_id(
    #     self,
    #     object_id: uuid.UUID,
    #     current_user: Optional["CurrentUserData"] = None,
    # ) -> BaseSchemaTypeRead:
    #     return await self.read(
    #         current_user=current_user, filters=[self.model.id == object_id]
    #     )
    #     # TBD: add access control checks here:
    #     # request is known from self.current_user, object and method is read here
    #     """Returns an object by id."""
    #     # if not await self.access_control.allows(
    #     #     user=current_user,
    #     #     resource_id=object_id,
    #     #     resource_type=self.resource_type,
    #     #     action=read,
    #     # ):
    #     #     raise HTTPException(status_code=403, detail="Access denied")
    #     session = self.session
    #     model = self.model
    #     join_conditions = self.access_control.filters_allowed(
    #         resource_type=self.resource_type,
    #         action=read,
    #         user=current_user,
    #     )
    #     # generically get the primary key of a model:
    #     # primary_key = next(iter(model.__table__.primary_key.columns)).name

    #     # TBD: delete version before refactoring:
    #     # object = await session.get(model, object_id)
    #     # if object is None:
    #     #     # TBD: add access logging here!
    #     #     raise HTTPException(status_code=404, detail="Object not found")
    #     # if hasattr(object, "last_accessed_at") and update_last_access is True:
    #     #     model.last_accessed_at = datetime.now()
    #     #     session.add(object)
    #     #     await session.commit()
    #     #     await session.refresh(object)
    #     try:
    #         statement = (
    #             select(model)
    #             .where(model.id == object_id)
    #             # TBD: add this back in!!
    #             .join(AccessPolicy, model.id == AccessPolicy.resource_id)
    #             .where(*join_conditions)
    #         )
    #         response = await session.exec(statement)
    #         object = response.one()
    #     except Exception as e:
    #         # TBD: add access logging here!
    #         logger.error(f"Error in BaseCRUD.read_by_id: {e}")
    #         raise HTTPException(status_code=404, detail="Object not found")
    #     # TBD: add access logging here!
    #     return object

    async def update(
        self,
        # Refactor into this:
        current_user: "CurrentUserData",
        # old: BaseModelType,
        object_id: uuid.UUID,
        new: BaseSchemaTypeUpdate,
    ) -> BaseModelType:
        """Updates an object."""
        session = self.session
        # TBD: refactor into try-except block and add logging
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write here

        try:
            ### This should be ready to go:
            access_conditions = self.access_control.filters_allowed(
                resource_type=self.resource_type,
                action=write,
                user=current_user,
            )
            if not access_conditions:
                statement = select(self.model).where(self.model.id == object_id)
            else:
                statement = (
                    select(self.model)
                    .where(self.model.id == object_id)
                    .join(AccessPolicy, self.model.id == AccessPolicy.resource_id)
                    .where(*access_conditions)
                )
            response = await session.exec(statement)
            old = response.one()
            if old is None:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(status_code=404, detail="Object not found.")
            ####

            ### TBD delete old version from before refactoring:
            # old = await session.get(self.model, object_id)
            # if old is None:
            #     logger.info(f"Object with id {object_id} not found")
            #     raise HTTPException(status_code=404, detail="Object not found")
            ###

            # TBD: remove and add logging instead:
            if hasattr(old, "last_updated_at"):
                old.last_updated_at = datetime.now()
            # TBD: Refactor into access control
            # if hasattr(old, "last_accessed_at") and update_last_access is True:
            #     old.last_accessed_at = datetime.now()

            updated = new.model_dump(exclude_unset=True)
            for key, value in updated.items():
                # if key == "id" or key == "created_at" or key == "last_updated_at":
                # if (
                #     key == "created_at"
                #     or key == "last_updated_at"
                #     # or key == "last_accessed_at"
                # ):
                # continue
                setattr(old, key, value)
            object = old
            session.add(object)
            await session.commit()
            await session.refresh(object)
            # TBD: add exception handling here!
            # TBD: add access logging here!
            await self.__write_log(object_id, write, current_user, 200)
            return object
        except Exception as e:
            await self.__write_log(object_id, write, current_user, 404)
            logger.error(f"Error in BaseCRUD.update: {e}")
            raise HTTPException(status_code=404, detail="Object not updated.")

    async def delete(
        self,
        current_user: "CurrentUserData",
        object_id: uuid.UUID,
    ) -> BaseModelType:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write or delete here
        """Deletes an object."""
        session = self.session
        model = self.model
        try:
            ### This should be ready to go:
            access_conditions = self.access_control.filters_allowed(
                resource_type=self.resource_type,
                action=write,
                user=current_user,
            )
            if not access_conditions:
                statement = select(model).where(self.model.id == object_id)
            else:
                statement = (
                    select(model)
                    .where(model.id == object_id)
                    .join(AccessPolicy, model.id == AccessPolicy.resource_id)
                    .where(*access_conditions)
                )
            response = await session.exec(statement)
            object = response.one()
            if object is None:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(status_code=404, detail="Object not found.")
            ####

            # TBD: refactor into try-except block and add logging
            ### TBD delete old version from before refactoring:
            # object = await session.get(model, object_id)
            # if object is None:
            #     raise HTTPException(status_code=404, detail="Object not found")
            ###
            await session.delete(object)
            await session.commit()
            await self.__write_log(object_id, own, current_user, 200)
            return object
        except Exception as e:
            await self.__write_log(object_id, write, current_user, 404)
            logger.error(f"Error in BaseCRUD.delete: {e}")
            raise HTTPException(status_code=404, detail="Object not deleted.")

    # TBD: add share / permission methods - maybe in an inherited class BaseCRUDPermissions?
