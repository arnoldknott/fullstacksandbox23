import uuid
import logging
from pprint import pprint
from datetime import datetime
from typing import TYPE_CHECKING, Generic, Type, TypeVar, Optional, List

from models.access import AccessPolicy, AccessLog, IdentifierTypeLink
from crud.access import AccessPolicyCRUD, AccessLoggingCRUD
from core.databases import get_async_session

# from core.access import AccessControl
from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlalchemy.dialects.postgresql import insert
from sqlmodel.ext.asyncio.session import AsyncSession

# from sqlalchemy.sql import distinct


if TYPE_CHECKING:
    pass
from core.types import CurrentUserData, Action, ResourceType, IdentityType

logger = logging.getLogger(__name__)

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
            self.entity_type = ResourceType(base_model.__name__)
        elif base_model.__name__ in IdentityType.list():
            self.entity_type = IdentityType(base_model.__name__)
        else:
            raise ValueError(
                f"{base_model.__name__} is not a valid ResourceType or IdentityType"
            )
        self.policy_CRUD = AccessPolicyCRUD()
        # self.access_control = AccessControl(self.policy_CRUD)
        self.logging_CRUD = AccessLoggingCRUD()

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    # move to AccessPolicyCRUD?
    async def _write_policy(
        self,
        resource_id: uuid.UUID,
        action: Action,
        current_user: "CurrentUserData",
    ):
        """Creates an access policy entry."""
        access_policy = AccessPolicy(
            resource_id=resource_id,
            action=action,
            identity_id=current_user.user_id,
        )
        # This needs a round-trip to database, as the policy-CRUD takes care of access control
        async with self.policy_CRUD as policy_CRUD:
            await policy_CRUD.create(access_policy, current_user)

    # move to AccessLoggingCRUD?
    def _add_log_to_session(
        self,
        object_id: uuid.UUID,
        action: Action,
        current_user: "CurrentUserData",
        status_code: int,
    ):
        """Creates an access log entry."""
        # print("=== CRUD - base - _add_log_to_session ===")
        # print("=== CRUD - base - _add_log_to_session - object_id ===")
        # pprint(object_id)
        # print("=== CRUD - base - _add_log_to_session - action ===")
        # pprint(action)
        # print("=== CRUD - base - _add_log_to_session - current_user ===")
        # pprint(current_user)
        # print("=== CRUD - base - _add_log_to_session - status_code ===")
        # pprint(status_code)
        # This code makes trouble with separate resource and identity link tables
        # as the logs are also written, when the resource id is actually an identity id
        # but models cannot be defined with a union of two foreign keys for resource_id
        access_log = AccessLog(
            resource_id=object_id,
            action=action,
            identity_id=current_user.user_id,
            status_code=status_code,
        )
        self.session.add(access_log)

    async def _write_log(
        self,
        object_id: uuid.UUID,
        action: Action,
        current_user: "CurrentUserData",
        status_code: int,
    ):
        """Creates an access log entry."""
        # access_log = AccessLogCreate(
        #     resource_id=object_id,
        #     action=action.value,
        #     # if public access, current_user is None
        #     identity_id=current_user.user_id if current_user else None,
        #     status_code=status_code,
        # )
        self._add_log_to_session(object_id, action, current_user, status_code)
        await self.session.commit()

        # TBD: fix primary key error in logging_CRUD
        # async with self.logging_CRUD as logging_CRUD:
        #     await logging_CRUD.log_access(access_log)

    def _add_identifier_type_link_to_session(
        self,
        object_id: uuid.UUID,
    ):
        """Adds resource type link entry to session."""
        identifier_type_link = IdentifierTypeLink(
            id=object_id,
            type=self.entity_type,
        )
        # statement = insert(ResourceTypeLink).values(
        #     id=object_id,
        #     type=self.entity_type,
        # )
        # print(
        #     "=== CRUD - base - _add_identifier_type_link_to_session - identifier_type_link ==="
        # )
        # pprint(identifier_type_link)
        # print(
        #     "=== CRUD - base - _add_identifier_type_link_to_session - identifier_type_link.model_dump() ==="
        # )
        # pprint(identifier_type_link.model_dump())
        statement = insert(IdentifierTypeLink).values(identifier_type_link.model_dump())
        statement = statement.on_conflict_do_nothing(index_elements=["id"])
        return statement
        # await self.session.exec(inde)
        # self.session.add(identifier_type_link)
        # await self.session.commit()
        # await self.session.refresh(identifier_type_link)
        # return identifier_type_link

    async def _write_identifier_type_link(
        self,
        object_id: uuid.UUID,
    ):
        """Creates an resource type link entry."""
        statement = self._add_identifier_type_link_to_session(object_id)
        await self.session.exec(statement)
        await self.session.commit()

    async def create(
        self,
        object: BaseSchemaTypeCreate,
        current_user: "CurrentUserData",
    ) -> BaseModelType:
        """Creates a new object."""
        logger.info("BaseCRUD.create")
        try:
            # TBD: refactor into hierarchy check
            # requires hierarchy checks to be in place: otherwise a user can never create a resource
            # as the AccessPolicy CRUD create checks, if the user is owner of the resource (that's not created yet)
            # needs to be fixed in the core access control by implementing a hierarchy check
            session = self.session
            Model = self.model
            database_object = Model.model_validate(object)
            # self._add_identifier_type_link_to_session(database_object.id)
            # self._add_log_to_session(database_object.id, own, current_user, 201)
            session.add(database_object)
            # TBD: merge the sessions for creating the policy and the log
            # maybe ven together creating the object
            # but we need the id of the object for the policy and the log
            # TBD: add creating the ResourceTypeLink entry with object_id and self.entity_type
            # this should be doable in the same database call as the access policy and the access log creation.
            await session.commit()
            await session.refresh(database_object)
            # TBD: create the statements in the methods, but execute together - less round-trips to database
            await self._write_identifier_type_link(database_object.id)
            await self._write_policy(database_object.id, own, current_user)
            await self._write_log(database_object.id, own, current_user, 201)
            return database_object
        except Exception as e:
            await self._write_log(database_object.id, own, current_user, 404)
            logger.error(f"Error in BaseCRUD.create: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} not found",  # Or "Forbidden." here?
            )

    async def create_public(
        self,
        object: BaseSchemaTypeCreate,
        current_user: "CurrentUserData",
    ) -> BaseModelType:
        """Creates a new object with public access."""
        database_object = await self.create(object, current_user)

        public_access_policy = AccessPolicy(
            resource_id=database_object.id,
            # entity_type=self.entity_type,
            action=read,
            public=True,
        )
        async with self.policy_CRUD as policy_CRUD:
            await policy_CRUD.create(public_access_policy, current_user)

        return database_object

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
        # TBD: consider allowing any return value - that might enable more flexibility, especially for select_args and functions!
        """Generic read method with optional parameters for select_args, filters, joins, order_by, group_by, limit and offset."""

        # statement = select(self.model if not select_args else *select_args)
        # TBD: select_args are not compatible with the return type of the method!
        statement = select(*select_args) if select_args else select(self.model)
        # statement = statement.join(
        #     AccessPolicy, self.model.id == AccessPolicy.resource_id
        # )
        # statement = statement.join(
        #     ResourceTypeLink, self.model.id == ResourceTypeLink.resource_id
        # )
        statement = self.policy_CRUD.filters_allowed(
            statement=statement,
            action=read,
            model=self.model,
            current_user=current_user,
        )
        # if not access_conditions:
        #     statement = select(self.model if not select_args else select_args)
        # if access_conditions:
        #     statement = statement.join(
        #         AccessPolicy, self.model.id == AccessPolicy.resource_id
        #     ).where(*access_conditions)
        #     # statement = (
        #     #     select(self.model if not select_args else select_args)
        #     #     .join(AccessPolicy, self.model.id == AccessPolicy.resource_id)
        #     #     .where(*access_conditions)
        #     # )

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

        # print("=== CRUD - base - read - statement ===")
        # print(statement.compile())
        # print(statement.compile().params)
        response = await self.session.exec(statement)
        results = response.all()
        # print("=== CRUD - base - read - results ===")
        # pprint(results)
        for result in results:
            await self._write_log(result.id, read, current_user, 200)
            # logs = await self.session.get(AccessLog, result.id)
            # log_results = logs.all()
            # print("=== CRUD - base - read - log_results ===")
            # pprint(log_results)

        if not results:
            # print("=== self.model.__name__ ===")
            # print(self.model.__name__)
            # print("=== self.entity_type ===")
            # print(self.entity_type)
            logger.info(f"No objects found for {self.model.__name__}")
            for result in results:
                await self._write_log(result.id, read, current_user, 404)
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found."
            )

        return results

    async def read_by_id(
        self,
        id: uuid.UUID,
        current_user: Optional["CurrentUserData"] = None,
    ):
        """Reads an object by id."""
        object = await self.read(
            current_user=current_user,
            filters=[self.model.id == id],
        )
        return object[0]

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
    #     join_conditions = self.policy_CRUD.filters_allowed(
    #         entity_type=self.entity_type,
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
    #     # if not await self.policy_CRUD.allows(
    #     #     current_user=current_user,
    #     #     resource_id=object_id,
    #     #     entity_type=self.entity_type,
    #     #     action=read,
    #     # ):
    #     #     raise HTTPException(status_code=403, detail="Access denied")
    #     session = self.session
    #     model = self.model
    #     join_conditions = self.policy_CRUD.filters_allowed(
    #         entity_type=self.entity_type,
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
            # access_conditions = self.policy_CRUD.filters_allowed(
            #     entity_type=self.entity_type,
            #     action=write,
            #     user=current_user,
            # )
            # if not access_conditions:
            #     statement = select(self.model).where(self.model.id == object_id)
            # else:
            #     statement = (
            #         select(self.model)
            #         .where(self.model.id == object_id)
            #         .join(AccessPolicy, self.model.id == AccessPolicy.resource_id)
            #         .where(*access_conditions)
            #     )

            # After refactoring to pass the statement:
            # statement = select(self.model, AccessPolicy).where(
            #     self.model.id == object_id
            # )
            # statement = select(self.model).distinct().where(self.model.id == object_id)
            statement = select(self.model).where(self.model.id == object_id)

            statement = self.policy_CRUD.filters_allowed(
                statement=statement,
                action=write,
                model=self.model,
                current_user=current_user,
            )

            # statement = select(self.model).where(self.model.id == object_id)
            # print("=== CRUD - base - update - statement ===")
            # print(statement.compile())
            # print(statement.compile().params)

            response = await session.exec(statement)

            # print("=== CRUD - base - update - response.all() ===")
            # print(response.all())

            old = response.one()

            # print("=== CRUD - base - update - old ===")
            # print(old)

            if old is None:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )
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
            self._add_log_to_session(object_id, write, current_user, 200)
            await session.commit()
            await session.refresh(object)
            # TBD: add exception handling here!
            # TBD: add access logging here!
            # await self._write_log(object_id, write, current_user, 200)
            return object
        except Exception as e:
            await self._write_log(object_id, write, current_user, 404)
            logger.error(f"Error in BaseCRUD.update: {e}")
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not updated."
            )

    async def delete(
        self,
        current_user: "CurrentUserData",
        object_id: uuid.UUID,
    ) -> BaseModelType:
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write or delete here
        """Deletes an object."""
        # session = self.session
        # model = self.model
        try:
            # ### This should be ready to go:
            # access_conditions = self.policy_CRUD.filters_allowed(
            #     entity_type=self.entity_type,
            #     action=write,
            #     user=current_user,
            # )
            # if not access_conditions:
            #     statement = select(model).where(self.model.id == object_id)
            # else:
            #     statement = (
            #         select(model)
            #         .where(model.id == object_id)
            #         .join(AccessPolicy, model.id == AccessPolicy.resource_id)
            #         .where(*access_conditions)
            #     )

            # After refactoring to pass the statement:
            statement = select(self.model).distinct().where(self.model.id == object_id)
            # statement = statement.join(
            #     AccessPolicy, self.model.id == AccessPolicy.resource_id
            # )
            statement = self.policy_CRUD.filters_allowed(
                statement=statement,
                action=write,
                model=self.model,
                current_user=current_user,
            )

            response = await self.session.exec(statement)
            object = response.one()
            if object is None:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )
            ####

            # TBD: refactor into try-except block and add logging
            ### TBD delete old version from before refactoring:
            # object = await session.get(model, object_id)
            # if object is None:
            #     raise HTTPException(status_code=404, detail="Object not found")
            ###
            await self.session.delete(object)
            self._add_log_to_session(object_id, own, current_user, 200)
            await self.session.commit()
            # await self._write_log(object_id, own, current_user, 200)
            return object
        except Exception as e:
            await self._write_log(object_id, own, current_user, 404)
            logger.error(f"Error in BaseCRUD.delete: {e}")
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not deleted."
            )

    # TBD: add share / permission methods - maybe in an inherited class BaseCRUDPermissions?
    # TBD: for the hierarchies, do we need more methods here or just a new method in the BaseCRUD?
    # like sharing, tagging, creating hierarchies etc.
    # or just a number of endpoints for doing the hierarchy: add child, remove child, ...?
    # share with different permissions - like actions?
