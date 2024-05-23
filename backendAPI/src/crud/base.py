import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar

# from core.access import AccessControl
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased
from sqlmodel import SQLModel, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD, ResourceHierarchyCRUD
from models.access import AccessLogCreate, AccessPolicyCreate, IdentifierTypeLink

# from sqlalchemy.sql import distinct


if TYPE_CHECKING:
    pass
from core.types import Action, CurrentUserData, IdentityType, ResourceType

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
        self.logging_CRUD = AccessLoggingCRUD()
        self.hierarchy_CRUD = ResourceHierarchyCRUD()

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    # async def _write_policy(
    #     self,
    #     resource_id: uuid.UUID,
    #     action: Action,
    #     current_user: "CurrentUserData",
    # ):
    #     """Creates an access policy entry."""
    #     access_policy = AccessPolicy(
    #         resource_id=resource_id,
    #         action=action,
    #         identity_id=current_user.user_id,
    #     )
    #     # This needs a round-trip to database, as the policy-CRUD takes care of access control
    #     async with self.policy_CRUD as policy_CRUD:
    #         await policy_CRUD.create(access_policy, current_user)

    # move to AccessLoggingCRUD or use/rewrite the on log_access from there?
    # def _add_log_to_session(
    #     self,
    #     object_id: uuid.UUID,
    #     action: Action,
    #     current_user: "CurrentUserData",
    #     status_code: int,
    # ):
    #     """Creates an access log entry."""
    #     access_log = AccessLog(
    #         resource_id=object_id,
    #         action=action,
    #         identity_id=current_user.user_id if current_user else None,
    #         status_code=status_code,
    #     )
    #     self.session.add(access_log)

    # async def _write_log(
    #     self,
    #     object_id: uuid.UUID,
    #     action: Action,
    #     current_user: "CurrentUserData",
    #     status_code: int,
    # ):
    #     """Creates an access log entry."""
    #     self._add_log_to_session(object_id, action, current_user, status_code)
    #     await self.session.commit()

    def _add_identifier_type_link_to_session(
        self,
        object_id: uuid.UUID,
    ):
        """Adds resource type link entry to session."""
        identifier_type_link = IdentifierTypeLink(
            id=object_id,
            type=self.entity_type,
        )

        statement = insert(IdentifierTypeLink).values(identifier_type_link.model_dump())
        statement = statement.on_conflict_do_nothing(index_elements=["id"])
        return statement

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
        parent_id: Optional[uuid.UUID] = None,
        inherit: Optional[bool] = False,
    ) -> BaseModelType:
        """Creates a new object."""
        logger.info("BaseCRUD.create")
        try:
            # TBD: refactor into hierarchy check
            # requires hierarchy checks to be in place: otherwise a user can never create a resource
            # as the AccessPolicy CRUD create checks, if the user is owner of the resource (that's not created yet)
            # needs to be fixed in the core access control by implementing a hierarchy check
            if inherit and not parent_id:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot inherit permissions without a parent.",
                )
            database_object = self.model.model_validate(object)
            # print("=== CRUD - base - create - database_object ===")
            # pprint(database_object)
            await self._write_identifier_type_link(database_object.id)
            self.session.add(database_object)
            # await self.session.commit()
            # await self.session.refresh(database_object)
            access_log = AccessLogCreate(
                resource_id=database_object.id,
                action=own,
                identity_id=current_user.user_id,
                status_code=201,
            )
            async with self.logging_CRUD as logging_CRUD:
                await logging_CRUD.create(access_log)
            # self.session = self.logging_CRUD.add_log_to_session(
            #     access_log, self.session
            # )
            # await self._add_log_to_session(database_object.id, own, current_user, 201)

            # TBD: merge the sessions for creating the policy and the log
            # maybe together with creating the object
            # but we need the id of the object for the policy and the log
            # The id is already available after model_validate!
            # TBD: add creating the ResourceTypeLink entry with object_id and self.entity_type
            # this should be doable in the same database call as the access policy and the access log creation.
            # self._add_identifier_type_link_to_session(database_object.id)
            await self.session.commit()
            await self.session.refresh(database_object)
            # TBD: create the statements in the methods, but execute together - less round-trips to database
            # await self._write_identifier_type_link(database_object.id)
            # await self._write_policy(database_object.id, own, current_user)
            access_policy = AccessPolicyCreate(
                resource_id=database_object.id,
                action=own,
                identity_id=current_user.user_id,
            )
            async with self.policy_CRUD as policy_CRUD:
                await policy_CRUD.create(access_policy, current_user)
            # await self._write_log(database_object.id, own, current_user, 201)
            if parent_id:
                async with self.hierarchy_CRUD as hierarchy_CRUD:
                    await hierarchy_CRUD.create(
                        current_user=current_user,
                        parent_id=parent_id,
                        child_type=self.entity_type,
                        child_id=database_object.id,
                        inherit=inherit,
                    )

            # print("=== CRUD - base - create - database_object ===")
            # pprint(database_object)

            return database_object

        except Exception as e:
            try:
                access_log = AccessLogCreate(
                    resource_id=database_object.id,
                    action=own,
                    identity_id=current_user.user_id,
                    status_code=404,
                )
                async with self.logging_CRUD as logging_CRUD:
                    await logging_CRUD.create(access_log)
                # await self._write_log(database_object.id, own, current_user, 404)
            except Exception as log_error:
                logger.error(
                    f"Error in BaseCRUD.create of an object of type {self.model}, action: {own}, current_user: {current_user}, status_code: {404} results in  {log_error}"
                )
            logger.error(f"Error in BaseCRUD.create: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} not found",  # Or "Forbidden." here?
            )

    async def create_public(
        self,
        object: BaseSchemaTypeCreate,
        current_user: "CurrentUserData",
        parent_id: Optional[uuid.UUID] = None,
        inherit: Optional[bool] = False,
        action: Action = read,
    ) -> BaseModelType:
        """Creates a new object with public access."""
        database_object = await self.create(object, current_user, parent_id, inherit)

        public_access_policy = AccessPolicyCreate(
            resource_id=database_object.id,
            action=action,
            public=True,
        )
        async with self.policy_CRUD as policy_CRUD:
            await policy_CRUD.create(public_access_policy, current_user)
        # async with self.policy_CRUD as policy_CRUD:
        #     await policy_CRUD.create(database_object.id, action, public=True)

        return database_object

    # TBD: implement a create_if_not_exists method

    # TBD: add skip and limit
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
        try:
            # TBD: select_args are not compatible with the return type of the method!
            statement = select(*select_args) if select_args else select(self.model)

            statement = self.policy_CRUD.filters_allowed(
                statement=statement,
                action=read,
                model=self.model,
                current_user=current_user,
            )

            if joins:
                for join in joins:
                    statement = statement.join(join)

            if filters:
                for filter in filters:
                    statement = statement.where(filter)

            # TBD. implement a default order_by:
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
                access_log = AccessLogCreate(
                    resource_id=result.id,
                    action=read,
                    identity_id=current_user.user_id if current_user else None,
                    status_code=200,
                )
                async with self.logging_CRUD as logging_CRUD:
                    await logging_CRUD.create(access_log)
                # await self._write_log(result.id, read, current_user, 200)
            if not results:
                logger.info(f"No objects found for {self.model.__name__}")
                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )

            return results
        except Exception as err:
            try:
                access_log = AccessLogCreate(
                    resource_id=result.id,
                    action=read,
                    identity_id=current_user.user_id if current_user else None,
                    status_code=404,
                )
                async with self.logging_CRUD as logging_CRUD:
                    await logging_CRUD.create(access_log)
                # await self._write_log(result.id, read, current_user, 404)
            except Exception as log_error:
                logger.error(
                    (
                        f"Error in BaseCRUD.read with parameters:"
                        f"select_args: {select_args},"
                        f"filters: {filters},"
                        f"joins: {joins},"
                        f"order_by: {order_by},"
                        f"group_by: {group_by},"
                        f"having: {having},"
                        f"limit: {limit},"
                        f"offset: {offset},"
                        f"action: {read},"
                        f"current_user: {current_user},"
                        f"status_code: {404}"
                        f"results in {log_error}"
                    )
                )
                logger.error(
                    f"Error in BaseCRUD.read for model {self.model.__name__}: {err}"
                )

                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )

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

    async def update(
        self,
        current_user: "CurrentUserData",
        object_id: uuid.UUID,
        new: BaseSchemaTypeUpdate,
    ) -> BaseModelType:
        """Updates an object."""
        session = self.session

        try:
            statement = select(self.model).where(self.model.id == object_id)

            statement = self.policy_CRUD.filters_allowed(
                statement=statement,
                action=write,
                model=self.model,
                current_user=current_user,
            )
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

            # TBD: remove and add logging instead:
            if hasattr(old, "last_updated_at"):
                old.last_updated_at = datetime.now()

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
            access_log = AccessLogCreate(
                resource_id=object.id,
                action=write,
                identity_id=current_user.user_id,
                status_code=200,
            )
            async with self.logging_CRUD as logging_CRUD:
                await logging_CRUD.create(access_log)
            # self.session = self.logging_CRUD.add_log_to_session(
            #     access_log, self.session
            # )
            # self._add_log_to_session(object_id, write, current_user, 200)
            await session.commit()
            await session.refresh(object)
            return object
        except Exception as e:
            try:
                access_log = AccessLogCreate(
                    resource_id=object.id,
                    action=write,
                    identity_id=current_user.user_id,
                    status_code=404,
                )
                async with self.logging_CRUD as logging_CRUD:
                    await logging_CRUD.create(access_log)
                # await self._write_log(object_id, write, current_user, 404)
            except Exception as log_error:
                logger.error(
                    f"Error in BaseCRUD.update with parameters object_id: {object_id}, action: {write}, current_user: {current_user}, status_code: {404} results in  {log_error}"
                )
            logger.error(f"Error in BaseCRUD.update: {e}")
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not updated."
            )

    async def delete(
        self,
        current_user: "CurrentUserData",
        object_id: uuid.UUID,
    ) -> None:  # BaseModelType:
        """Deletes an object."""
        try:
            # statement = select(self.model).distinct().where(self.model.id == object_id)
            # statement = self.policy_CRUD.filters_allowed(
            #     statement=statement,
            #     action=own,
            #     model=self.model,
            #     current_user=current_user,
            # )

            # response = await self.session.exec(statement)
            # object = response.one()
            # if object is None:
            #     logger.info(f"Object with id {object_id} not found")
            #     raise HTTPException(
            #         status_code=404, detail=f"{self.model.__name__} not found."
            #     )
            # # print("=== CRUD - base - delete - object ===")
            # # pprint(object)

            # # TBD: deleting a resource also needs to delete the according access policies!

            # await self.session.delete(object)

            # access_log = AccessLogCreate(
            #     resource_id=object.id,
            #     action=own,
            #     identity_id=current_user.user_id,
            #     status_code=200,
            # )
            # async with self.logging_CRUD as logging_CRUD:
            #     await logging_CRUD.create(access_log)
            # # self.session = self.logging_CRUD.add_log_to_session(
            # #     access_log, self.session
            # # )
            # # self._add_log_to_session(object_id, own, current_user, 200)
            # await self.session.commit()
            # return object

            #### Refactored into subquery:
            model_alias = aliased(self.model)
            subquery = (
                select(model_alias.id).distinct().where(model_alias.id == object_id)
            )
            subquery = self.policy_CRUD.filters_allowed(
                statement=subquery,
                action=own,
                model=model_alias,
                current_user=current_user,
            )

            statement = delete(self.model).where(self.model.id.in_(subquery))
            result = await self.session.exec(statement)

            if result.rowcount == 0:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )

            access_log = AccessLogCreate(
                resource_id=object_id,
                action=own,
                identity_id=current_user.user_id,
                status_code=200,
            )
            async with self.logging_CRUD as logging_CRUD:
                await logging_CRUD.create(access_log)
            # self.session = self.logging_CRUD.add_log_to_session(
            #     access_log, self.session
            # )
            # self._add_log_to_session(object_id, own, current_user, 200)
            await self.session.commit()
            return None

        except Exception as e:
            try:
                access_log = AccessLogCreate(
                    resource_id=object_id,
                    action=own,
                    identity_id=current_user.user_id,
                    status_code=404,
                )
                async with self.logging_CRUD as logging_CRUD:
                    await logging_CRUD.create(access_log)
                # await self._write_log(object_id, own, current_user, 404)
            except Exception as log_error:
                logger.error(
                    f"Error in BaseCRUD.delete with parameters object_id: {object_id}, action: {own}, current_user: {current_user}, status_code: {404} results in  {log_error}"
                )
            logger.error(f"Error in BaseCRUD.delete: {e}")
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not deleted."
            )

    # TBD: add share / permission methods - maybe in an inherited class BaseCRUDPermissions?
    # TBD: for the hierarchies, do we need more methods here or just a new method in the BaseCRUD?
    # => The AccessPolicyCRUD takes care of this!
    # like sharing, tagging, creating hierarchies etc.
    # or just a number of endpoints for doing the hierarchy: add child, remove child, ...?
    # share with different permissions - like actions?
