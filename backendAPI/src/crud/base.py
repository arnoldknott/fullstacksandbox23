import logging
import uuid
from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar
from pprint import pprint

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import (
    aliased,
    class_mapper,
    contains_eager,
    foreign,
)
from sqlmodel import SQLModel, delete, select, or_, asc

from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from crud.access import (
    AccessLoggingCRUD,
    AccessPolicyCRUD,
    ResourceHierarchyCRUD,
    IdentityHierarchyCRUD,
    BaseHierarchyModelRead,
)
from models.access import (
    AccessLogCreate,
    AccessPolicyCreate,
    IdentifierTypeLink,
    ResourceHierarchy,
    IdentityHierarchy,
)


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
            self.entity_type = ResourceType(self.model.__name__)
            self.types = ResourceType
            self.hierarchy_CRUD = ResourceHierarchyCRUD()
            self.hierarchy = ResourceHierarchy
            self.relations = ResourceHierarchy.relations
        elif base_model.__name__ in IdentityType.list():
            self.entity_type = IdentityType(self.model.__name__)
            self.types = IdentityType
            self.hierarchy_CRUD = IdentityHierarchyCRUD()
            self.hierarchy = IdentityHierarchy
            self.relations = IdentityHierarchy.relations
        else:
            raise ValueError(
                f"{base_model.__name__} is not a valid ResourceType or IdentityType"
            )

        # TBD: move to to the init: get all possible parent-child relations for the entity_type there!

        # if self.entity_type in ResourceType:
        #     related_model = ResourceType.get_model(relationship.mapper.class_.__name__)

        # elif self.entity_type in IdentityType:
        #     related_model = IdentityType.get_model(relationship.mapper.class_.__name__)

        self.policy_CRUD = AccessPolicyCRUD()
        self.logging_CRUD = AccessLoggingCRUD()
        # moved to the if-block to check which hierarchy is relevant.
        # self.hierarchy_CRUD = (
        #     ResourceHierarchyCRUD()
        # )  # TBD. are the occasions, where I would need the IdentityHierarchyCRUD() here?

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
                await self.add_child_to_parent(
                    parent_id=parent_id,
                    child_id=database_object.id,
                    current_user=current_user,
                    inherit=inherit,
                )
                # async with self.hierarchy_CRUD as hierarchy_CRUD:
                #     await hierarchy_CRUD.create(
                #         current_user=current_user,
                #         parent_id=parent_id,
                #         child_type=self.entity_type,
                #         child_id=database_object.id,
                #         inherit=inherit,
                #     )

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

    async def add_child_to_parent(
        self,
        parent_id: uuid.UUID,
        child_id: uuid.UUID,
        current_user: "CurrentUserData",
        inherit: Optional[bool] = False,
    ) -> BaseHierarchyModelRead:
        """Adds a member of this class to a parent (of another entity type)."""
        async with self.hierarchy_CRUD as hierarchy_CRUD:
            hierarchy = await hierarchy_CRUD.create(
                current_user=current_user,
                parent_id=parent_id,
                child_type=self.entity_type,
                child_id=child_id,
                inherit=inherit,
            )

        return hierarchy

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
            # statement = (
            #     self.session.select(*select_args)
            #     if select_args
            #     else self.session.select(self.model)
            # )

            statement = self.policy_CRUD.filters_allowed(
                statement=statement,
                action=read,
                model=self.model,
                current_user=current_user,
            )

            # query relationships:
            for relationship in class_mapper(self.model).relationships:
                # Determine the related model, the relevant hierarchy and relations based on self.entity_type
                related_model = self.types.get_model(
                    relationship.mapper.class_.__name__
                )
                # if self.entity_type in ResourceType:
                # related_model = ResourceType.get_model(
                #     relationship.mapper.class_.__name__
                # )
                # hierarchy_aliased = aliased(ResourceHierarchy)
                # relations = (
                #     ResourceHierarchyRelationships.relations
                # )
                # relations = ResourceHierarchy.relations
                # TBD: move to to the init: get all possible parent-child relations for the entity_type there!
                # elif self.entity_type in IdentityType:
                # related_model = IdentityType.get_model(
                #     relationship.mapper.class_.__name__
                # )
                # hierarchy_aliased = aliased(IdentityHierarchy)
                # relations = IdentityHierarchyRelationships.relations
                # relations = IdentityHierarchy.relations

                # if relationship.mapper.class_.__name__ in ResourceType.list():
                #     related_model = ResourceType.get_model(
                #         relationship.mapper.class_.__name__
                #     )
                # elif relationship.mapper.class_.__name__ in IdentityType.list():
                #     related_model = IdentityType.get_model(
                #         relationship.mapper.class_.__name__
                #     )

                related_attribute = getattr(self.model, relationship.key)

                # subquery = select(child_model)
                # subquery = self.policy_CRUD.filters_allowed(
                #     statement=subquery,
                #     action=read,
                #     model=child_model,
                #     current_user=current_user,
                # )
                # print("=== CRUD - base - read - subquery ===")
                # statement = statement.add_columns(child_model)
                # statement = statement.join(
                #     child_model,
                #     child_model.id == ResourceHierarchyRelationships.child_id,
                # )
                # statement = statement.where(
                #     ResourceHierarchyRelationships.parent_id == self.model.id
                # )
                # statement = self.policy_CRUD.filters_allowed(
                #     statement=statement,
                #     action=read,
                #     model=child_model,
                #     current_user=current_user,
                # )
                # statement = statement.options(selectinload(relationship))
                # statement = statement.options(joinedload(relationship))
                # statement = statement.options(contains_eager(child_model)).options(
                #     subqueryload(subquery)
                # )
                # subquery = select(AccessPolicy.resource_id).where(
                #     AccessPolicy.identity_id == current_user.user_id,
                #     AccessPolicy.action == read,
                # )
                # statement = statement.options(
                #     joinedload(self.model.relationship)  # , innerjoin=True)
                #     # somewhere I need to at the join conditions through hierarchy table!
                # ).with_loader_criteria(child_model, child_model.id.in_(subquery))

                # statement = statement.options(joinedload(self.model.child_model))
                # statement = statement.add_columns(child_model)
                # statement = statement.join(
                #     ResourceHierarchy, self.model.id == ResourceHierarchy.parent_id
                # )
                # statement = statement.join(
                #     child_model, ResourceHierarchy.child_id == child_model.id
                # )
                # statement = self.policy_CRUD.filters_allowed(
                #     statement=statement,
                #     action=read,
                #     model=child_model,
                #     current_user=current_user,
                # )

                # child_query = select(child_model)
                # child_query = child_query.join(
                #     ResourceHierarchy, self.model.id == ResourceHierarchy.parent_id
                # )
                # child_query = child_query.join(
                #     child_model, ResourceHierarchy.child_id == child_model.id
                # )
                # statement = statement.options(joinedload(child_query))

                # print("=== CRUD - base - read - self.model ===")
                # print(self.model)
                # print("=== CRUD - base - read - relationship ===")
                # print(relationship)
                # print("=== CRUD - base - read - child_model ===")
                # print(child_model)

                # print("\n")

                # print("=== CRUD - base - read - child_attribute ===")
                # print(child_attribute)

                # print("\n")

                print("============ The type associated with the model ============")
                print("=== CRUD - base - read - self.entity_type ===")
                print(self.entity_type)
                print("\n")

                print(
                    "============ This specific relationship inside the model ============"
                )
                print("=== CRUD - base - read - relationship ===")
                print(relationship)
                print("=== CRUD - base - read - relationship.key ===")
                print(relationship.key)
                print("=== CRUD - base - read - relationship.mapper ===")
                print(relationship.mapper)
                print("=== CRUD - base - read - related_attribute ===")
                print(related_attribute)
                print("=== CRUD - base - read - related_model ===")
                print(related_model)

                related_type = self.types(related_model.__name__)

                print("=== CRUD - base - read - related_type ===")
                print(related_type)

                # print("=== CRUD - base - read - relationship.mapper.class_ ===")
                # print(relationship.mapper.class_)
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__name__ ==="
                # )
                # print(relationship.mapper.class_.__name__)
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__table__ ==="
                # )
                # print(relationship.mapper.class_.__table__)
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__table__.name ==="
                # )
                # print(relationship.mapper.class_.__table__.name)
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__table__.columns ==="
                # )
                # print(relationship.mapper.class_.__table__.columns)
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__table__.columns.keys() ==="
                # )
                # print(relationship.mapper.class_.__table__.columns.keys())
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__table__.columns.values() ==="
                # )
                # print(relationship.mapper.class_.__table__.columns.values())
                # print(
                #     "=== CRUD - base - read - relationship.mapper.class_.__table__.columns.items() ==="
                # )
                # print(relationship.mapper.class_.__table__.columns.items())
                print("\n")

                related_statement = select(related_model.id)
                related_statement = self.policy_CRUD.filters_allowed(
                    related_statement,
                    action=read,
                    model=related_model,
                    current_user=current_user,
                )

                # if self.entity_type in ResourceType:
                #     hierarchy_aliased = aliased(ResourceHierarchy)
                # elif self.entity_type in IdentityType:
                #     hierarchy_aliased = aliased(IdentityHierarchy)
                # else:
                #     raise ValueError(f"{self.entity_type} type not found.")

                # statement = statement.outerjoin(
                #     hierarchy_aliased,
                #     self.model.id == hierarchy_aliased.parent_id,
                # )
                # statement = statement.outerjoin(
                #     related_model, hierarchy_aliased.child_id == related_model.id
                # )

                print(
                    "============ All relations of the whole application ============"
                )
                print("=== CRUD - base - read - self.relations ===")
                pprint(self.relations)
                print("=== CRUD - base - read - self.relations.keys() ===")
                pprint(self.relations.keys())
                print("=== CRUD - base - read - self.relations.values() ===")
                pprint(self.relations.values())
                print("\n")

                # TBD: refactor to get the children and parents into the init()?!
                # Check if self.entity_type is a key in relations, i.e. the model is a parent in the hierarchy
                aliased_hierarchy = aliased(self.hierarchy)

                for parent, children in self.relations.items():
                    print("=== CRUD - base - read - app_relation ===")
                    print(parent)
                    print("=== CRUD - base - read - children ===")
                    print(children)
                    # print("=== CRUD - base - read - type(app_relation) ===")
                    # print(type(app_relation))
                    if self.entity_type == parent and related_type in children:
                        # self.model is a parent, join on parent_id
                        statement = statement.outerjoin(
                            aliased_hierarchy,
                            self.model.id == foreign(aliased_hierarchy.parent_id),
                        )
                        statement = statement.outerjoin(
                            related_model,
                            related_model.id == foreign(aliased_hierarchy.child_id),
                        )
                    elif self.entity_type in children and related_type == parent:
                        # self.model is a child, join on child_id
                        statement = statement.outerjoin(
                            aliased_hierarchy,
                            self.model.id == foreign(aliased_hierarchy.child_id),
                        )
                        statement = statement.outerjoin(
                            related_model,
                            related_model.id == foreign(aliased_hierarchy.parent_id),
                        )

                # if self.entity_type in self.relations.keys():
                #     # self.model is a parent, join on parent_id
                #     statement = statement.outerjoin(
                #         aliased_hierarchy,
                #         self.model.id == foreign(aliased_hierarchy.parent_id),
                #     )
                #     statement = statement.outerjoin(
                #         related_model,
                #         related_model.id == foreign(aliased_hierarchy.child_id),
                #     )

                # # Check if self.entity_type is in the values of relations, i.e. the model is child in the hierarchy
                # # TBD: This is wrong: the values needs to be aligned with a specific key in the relations dict
                # # not just child of anything - but child of the parent, that is requested in the model -> relationship
                # # This does not take into account, that the model might be a child and a parent at the same time!
                # elif any(
                #     self.entity_type in values for values in self.relations.values()
                # ):
                #     # self.model is a child, join on child_id
                #     print("=== CRUD - base - read - finding parents ===")
                #     statement = statement.outerjoin(
                #         aliased_hierarchy,
                #         self.model.id == foreign(aliased_hierarchy.child_id),
                #     )
                #     statement = statement.outerjoin(
                #         related_model,
                #         related_model.id == foreign(aliased_hierarchy.parent_id),
                #     )

                # print("=== CRUD - base - read - child_statement ===")
                # print(child_statement.compile())
                # print(child_statement.compile().params)

                # limit the child_model to the ones, that are in the child_statement
                # and allows the parents, that don't have children in child_statement
                statement = statement.where(
                    or_(
                        related_model.id == None,
                        related_model.id.in_(related_statement),
                    )
                ).options(contains_eager(related_attribute))

                # statement = statement.join(
                #     child_model,
                #     child_model.id.in_(child_statement),

                # ).options(contains_eager(child_attribute))

            if joins:
                for join in joins:
                    statement = statement.join(join)

            if filters:
                for filter in filters:
                    statement = statement.where(filter)

            if order_by:
                for order in order_by:
                    statement = statement.order_by(order)
            elif hasattr(self.model, "id"):
                statement = statement.order_by(asc(self.model.id))

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
            # print("\n")

            response = await self.session.exec(statement)
            results = response.unique().all()

            # await self.session.flush()

            # print("=== CRUD - base - read - results ===")
            # pprint(results)
            # print("\n")

            for result in results:

                # print("=== CRUD - base - read - validated results ===")
                # pprint(result)
                # print("\n")

                # TBD: add logging to accessed children!
                access_log = AccessLogCreate(
                    resource_id=result.id,  # result might not be available here?
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

        # print("=== CRUD - base - read_by_id - current_user ===")
        # print(current_user)

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
            old = response.unique().one()
            # print("=== CRUD - base - update - old ===")
            # print(old)
            if old is None:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )
            ####

            updated = new.model_dump(exclude_unset=True)
            for key, value in updated.items():
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
