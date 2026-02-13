import logging
import uuid
from os import makedirs, path, remove, rename
from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased, class_mapper, contains_eager, foreign, noload
from sqlmodel import SQLModel, asc, delete, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from crud import registry_CRUDs
from crud.access import (
    AccessLoggingCRUD,
    AccessPolicyCRUD,
    BaseHierarchyModelRead,
    IdentityHierarchyCRUD,
    ResourceHierarchyCRUD,
)
from models.access import (
    AccessLogCreate,
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessRequest,
    IdentifierTypeLink,
    IdentityHierarchy,
    ResourceHierarchy,
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
    ],
):
    """Base class for CRUD operations."""

    def __init__(
        self,
        base_model: Type[BaseModelType],
        directory: str = None,
        allow_standalone: Optional[bool] = False,
        allow_public_create: Optional[bool] = False,
        session: Optional[AsyncSession] = None,
    ):
        """Provides a database session for CRUD operations."""
        self.session = session
        self._owns_session = False if session else True
        self.model = base_model
        self.data_directory = directory
        self.allow_standalone = allow_standalone
        self.allow_public_create = allow_public_create
        if base_model.__name__ in ResourceType.list():
            self.entity_type = ResourceType(self.model.__name__)
            self.type = ResourceType
            self.hierarchy_CRUD = ResourceHierarchyCRUD
            self.hierarchy = ResourceHierarchy
            self.relations = ResourceHierarchy.relations
        elif base_model.__name__ in IdentityType.list():
            self.entity_type = IdentityType(self.model.__name__)
            self.type = IdentityType
            self.hierarchy_CRUD = IdentityHierarchyCRUD
            self.hierarchy = IdentityHierarchy
            self.relations = IdentityHierarchy.relations
        else:
            raise ValueError(
                f"{base_model.__name__} is not a valid ResourceType or IdentityType"
            )

        self.policy_crud = (
            AccessPolicyCRUD(session=self.session) if session else AccessPolicyCRUD()
        )
        self.logging_crud = (
            AccessLoggingCRUD(session=self.session) if session else AccessLoggingCRUD()
        )

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        if self.session is None:
            self.session = await get_async_session()
            self.policy_crud = AccessPolicyCRUD(session=self.session)
            self.logging_crud = AccessLoggingCRUD(session=self.session)
            self._owns_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        if self._owns_session:
            await self.session.close()
            self.session = None
            self._owns_session = False

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
        type: IdentityType = None,
    ):
        """Adds resource type link entry to session."""
        type = type or self.entity_type
        identifier_type_link = IdentifierTypeLink(
            id=object_id,
            type=self.entity_type,
        )

        statement = insert(IdentifierTypeLink).values(identifier_type_link.model_dump())
        statement = statement.on_conflict_do_nothing(index_elements=["id"])
        return statement

    async def _write_identifier_type_link(
        self, object_id: uuid.UUID, type: IdentityType = None
    ):
        """Creates an resource type link entry."""
        statement = self._add_identifier_type_link_to_session(object_id, type)
        await self.session.exec(statement)
        await self.session.commit()

    async def _get_types_from_ids(
        self, ids: List[uuid.UUID]
    ) -> List[IdentityType | ResourceType]:
        """Gets the resource types for a list of object IDs."""
        statement = select(IdentifierTypeLink).where(IdentifierTypeLink.id.in_(ids))
        response = await self.session.exec(statement)
        return response.all()

    async def check_identifier_type_link(
        self,
        object_id: uuid.UUID,
    ):
        """Checks if a resource type link of an object_id refers to a type self_model."""
        statement = select(IdentifierTypeLink).where(
            IdentifierTypeLink.id == object_id,
            IdentifierTypeLink.type == self.entity_type,
        )
        response = await self.session.exec(statement)
        result = response.unique().one()
        if not result:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found."
            )
        return True

    def _provide_data_directory(
        self,
    ):
        """Checks if a file path exists and if not creates it."""
        try:
            if not path.exists(f"/data/appdata/{self.data_directory}"):
                makedirs(f"/data/appdata/{self.data_directory}")
            return True
        except Exception as e:
            raise Exception(f"Path not found: {e}")

    async def create(  # noqa: C901
        self,
        object: BaseSchemaTypeCreate,
        current_user: Optional["CurrentUserData"] = None,
        parent_id: Optional[uuid.UUID] = None,
        inherit: Optional[bool] = False,
        # TBD: add tests in protected resource to check public and public_action creation:
        public: Optional[bool] = False,
        public_action: Optional[Action] = None,
    ) -> BaseModelType:
        """Creates a new object.

        Supports both authenticated and public resource creation:
        - Authenticated: Creates access log + owner policy + optional public policy
        - Public: Only creates public access policy (no owner, no log)

        Public creation requires:
        - self.allow_public_create = True
        - public = True
        - current_user = None
        """
        logger.info("BaseCRUD.create")

        try:
            # Early validation
            if inherit and not parent_id:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot inherit permissions without a parent.",
                )

            # Determine if this is a public (unauthenticated) creation
            is_public_creation = (
                self.allow_public_create and public and not current_user
            )

            # Validate that current_user is present when required
            if not is_public_creation and not current_user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required.",
                )
            elif not current_user:
                public_user_id = uuid.uuid4()
                await self._write_identifier_type_link(
                    public_user_id, IdentityType.public
                )
                current_user = CurrentUserData(user_id=public_user_id)

            if parent_id or self.allow_standalone:
                if not self.allow_standalone:
                    parent_access_request = AccessRequest(
                        resource_id=parent_id,
                        action=write,
                        current_user=current_user,
                    )
                    # if not await self.policy_crud.allows(parent_access_request):
                    if not await self.policy_crud.allows(parent_access_request):
                        logger.error(f"Parent {parent_id} does not allow write access.")
                        raise HTTPException(status_code=403, detail="Forbidden.")
                    # check if requested parent exists:
                    query = select(IdentifierTypeLink).where(
                        IdentifierTypeLink.id == parent_id
                    )
                    parent_response = await self.session.exec(query)
                    parent_results = parent_response.one()
                    if not parent_results:
                        raise HTTPException(
                            status_code=404, detail="Parent resource does not exist."
                        )
                # async with self.policy_CRUD as policy_CRUD:
            else:
                # TBD: is it only admin that can create stand-alone resources?
                logger.error(
                    "Parent not provided and standalone creation is not allowed."
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"{self.model.__name__} - Forbidden.",
                )

            # Create and add database object
            database_object = self.model.model_validate(object)
            await self._write_identifier_type_link(database_object.id)
            self.session.add(database_object)

            # Create access log
            # if not is_public_creation:
            access_log = AccessLogCreate(
                resource_id=database_object.id,
                action=own,
                identity_id=current_user.user_id,
                status_code=201,
            )
            await self.logging_crud.create(access_log)

            # TBD: merge the sessions for creating the policy and the log
            # maybe together with creating the object
            # but we need the id of the object for the policy and the log
            # The id is already available after model_validate!
            # TBD: add creating the ResourceTypeLink entry with object_id and self.entity_type
            # this should be doable in the same database call as the access policy and the access log creation.
            # self._add_identifier_type_link_to_session(database_object.id)

            # TBD: create the statements in the methods, but execute together - less round-trips to database
            # await self._write_identifier_type_link(database_object.id)
            # await self._write_policy(database_object.id, own, current_user)
            # That's what session handling is for - it depends on where to exec() the session.

            # Create owner access policy
            # if not is_public_creation:
            access_policy = AccessPolicyCreate(
                resource_id=database_object.id,
                action=own,
                identity_id=current_user.user_id,
            )

            await self.policy_crud.create(
                access_policy, current_user, allow_override=True
            )
            if parent_id:
                await self.add_child_to_parent(
                    parent_id=parent_id,
                    child_id=database_object.id,
                    current_user=current_user,
                    inherit=inherit,
                )

            # Commit the object to the database
            await self.session.commit()
            await self.session.refresh(database_object)

            # Create public access policy
            if public:
                if not public_action:
                    public_action = read
                public_access_policy = AccessPolicyCreate(
                    resource_id=database_object.id,
                    action=public_action,
                    public=True,
                )
                # async with self.policy_CRUD as policy_CRUD:
                await self.policy_crud.create(
                    public_access_policy,
                    current_user=current_user,  # Will be None for public creation
                    allow_override=True,  # Always True - public policies don't need authorization
                )

            return database_object

        except Exception as e:
            await self.session.rollback()
            # Only log errors for authenticated users
            if not is_public_creation:
                try:
                    access_log = AccessLogCreate(
                        resource_id=database_object.id,
                        action=own,
                        identity_id=current_user.user_id,
                        status_code=404,
                    )
                    await self.logging_crud.create(access_log)
                    # await self._write_log(database_object.id, own, current_user, 404)
                except Exception as log_error:
                    logger.error(
                        f"Error in BaseCRUD.create of an object of type {self.model}, action: {own}, current_user: {current_user}, status_code: {404} results in  {log_error}"
                    )
            logger.error(f"Error in BaseCRUD.create: {e}")
            raise HTTPException(
                status_code=403,
                detail=f"{self.model.__name__} - Forbidden.",
            )

    async def create_file(
        self,
        file: UploadFile,
        current_user: "CurrentUserData",
        parent_id: Optional[uuid.UUID] = None,
        inherit: Optional[bool] = False,
    ) -> BaseModelType:
        """Creates new files."""
        file_object = await self.create(
            object={"name": file.filename},
            current_user=current_user,
            parent_id=parent_id,
            inherit=inherit,
        )
        try:
            self._provide_data_directory()
            disk_file = open(
                f"/data/appdata/{self.data_directory}/{file.filename}", "wb"
            )
            disk_file.write(file.file.read())
            return file_object
        except Exception as e:
            logger.error(f"Error in BaseCRUD.create_file {file.filename}: {e}")
            raise HTTPException(
                status_code=403,
                detail=f"{self.model.__name__} - Forbidden.",
            )

    # async def create_public(
    #     self,
    #     object: BaseSchemaTypeCreate,
    #     current_user: "CurrentUserData",
    #     parent_id: Optional[uuid.UUID] = None,
    #     inherit: Optional[bool] = False,
    #     action: Action = read,
    # ) -> BaseModelType:
    #     """Creates a new object with public access."""
    #     database_object = await self.create(object, current_user, parent_id, inherit)

    #     public_access_policy = AccessPolicyCreate(
    #         resource_id=database_object.id,
    #         action=action,
    #         public=True,
    #     )
    #     async with self.policy_CRUD as policy_CRUD:
    #         await policy_CRUD.create(
    #             public_access_policy,
    #             current_user,
    #             allow_override=self.allow_standalone,
    #         )

    #     return database_object

    async def add_child_to_parent(
        self,
        child_id: uuid.UUID,
        parent_id: uuid.UUID,
        current_user: "CurrentUserData",
        inherit: Optional[bool] = False,
    ) -> BaseHierarchyModelRead:
        """Adds a member of this class to a parent (of another entity type)."""
        hierarchy_CRUD = self.hierarchy_CRUD(session=self.session)
        hierarchy = await hierarchy_CRUD.create(
            current_user=current_user,
            parent_id=parent_id,
            child_type=self.entity_type,
            child_id=child_id,
            inherit=inherit,
        )

        return hierarchy

    async def reorder_children(
        self,
        parent_id: uuid.UUID,
        child_id: uuid.UUID,
        position: str,
        other_child_id: Optional[uuid.UUID],
        current_user: "CurrentUserData",
    ) -> None:
        """Reorders the children of a parent."""
        # async with self.hierarchy_CRUD as hierarchy_CRUD:
        hierarchy_CRUD = self.hierarchy_CRUD(session=self.session)
        hierarchy = await hierarchy_CRUD.reorder_children(
            current_user=current_user,
            parent_id=parent_id,
            child_id=child_id,
            position=position,
            other_child_id=other_child_id,
        )

        return hierarchy

    # TBD: implement a create_if_not_exists method
    # or UPSERT (update or insert)

    # TBD: add "skip_services: Optional[bool] = False"
    # to avoid calling orchestrator from services
    # otherwise it creates a loop!
    # TBD: add skip and limit
    # use with pagination:
    # Model = await model_crud.read(order_by=[Model.name], limit=10)
    # Model = await model_crud.read(order_by=[Model.name], limit=10, offset=10)
    async def read(  # noqa: C901
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
        try:
            # TBD: select_args are not compatible with the return type of the method!
            statement = select(*select_args) if select_args else select(self.model)

            statement = self.policy_crud.filters_allowed(
                statement=statement,
                action=read,
                model=self.model,
                current_user=current_user,
            )

            # query relationships:
            for relationship in class_mapper(self.model).relationships:
                # Determine the related model, the relevant hierarchy and relations based on self.entity_type
                related_model = self.type.get_model(relationship.mapper.class_.__name__)
                related_attribute = getattr(self.model, relationship.key)
                related_type = self.type(related_model.__name__)
                related_statement = select(related_model.id)
                # related_statement = self.policy_CRUD.filters_allowed(
                related_statement = self.policy_crud.filters_allowed(
                    related_statement,
                    action=read,
                    model=related_model,
                    current_user=current_user,
                )

                # Check if self.entity_type is a key in relations, i.e. the model is a parent in the hierarchy
                aliased_hierarchy = aliased(self.hierarchy)
                for parent, children in self.relations.items():
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
                        if self.hierarchy == ResourceHierarchy:
                            statement = statement.order_by(asc(aliased_hierarchy.order))
                        else:
                            statement = statement.order_by(asc(related_model.id))
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
                        # here no ordering, as parents don't have an order seen from the child:
                        statement = statement.order_by(asc(related_model.id))

                count_related_statement = select(func.count()).select_from(
                    related_statement.alias()
                )
                related_count = await self.session.exec(count_related_statement)
                count = related_count.one()

                if count == 0:
                    statement = statement.options(noload(related_attribute))
                else:
                    statement = statement.where(
                        or_(
                            related_model.id
                            == None,  # noqa E711: comparison to None should be 'if cond is None:'
                            related_model.id.in_(related_statement),
                        )
                    ).options(contains_eager(related_attribute))

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

            response = await self.session.exec(statement)
            results = response.unique().all()

            if not results:
                logger.info(f"No objects found for {self.model.__name__}")
                return []

            for result in results:
                # TBD: add logging to accessed children!
                access_log = AccessLogCreate(
                    resource_id=result.id,  # result might not be available here?
                    action=read,
                    identity_id=current_user.user_id if current_user else None,
                    status_code=200,
                )
                await self.logging_crud.create(access_log)

            return results
        except Exception as err:
            try:
                access_log = AccessLogCreate(
                    resource_id=result.id,
                    action=read,
                    identity_id=current_user.user_id if current_user else None,
                    status_code=404,
                )
                await self.logging_crud.create(access_log)
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
        if not object:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found."
            )
        return object[0]

    async def read_file_by_id(
        self,
        id: uuid.UUID,
        current_user: Optional["CurrentUserData"] = None,
    ):
        """Reads a file from disk by id."""

        file = await self.read_by_id(id, current_user)
        return FileResponse(
            f"/data/appdata/{self.data_directory}/{file.name}", filename=file.name
        )

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

            statement = self.policy_crud.filters_allowed(
                statement=statement,
                action=write,
                model=self.model,
                current_user=current_user,
            )
            response = await session.exec(statement)
            current = response.unique().one()
            if current is None:
                logger.info(f"Object with id {object_id} not found")
                raise HTTPException(
                    status_code=404, detail=f"{self.model.__name__} not found."
                )
            updated = new.model_dump(exclude_unset=True)
            for key, value in updated.items():
                setattr(current, key, value)
            session.add(current)
            access_log = AccessLogCreate(
                resource_id=current.id,
                action=write,
                identity_id=current_user.user_id,
                status_code=200,
            )
            await self.logging_crud.create(access_log)
            await session.commit()
            await session.refresh(current)
            return current
        except Exception as e:
            await session.rollback()
            try:
                access_log = AccessLogCreate(
                    resource_id=current.id,
                    action=write,
                    identity_id=current_user.user_id,
                    status_code=404,
                )
                await self.logging_crud.create(access_log)
            except Exception as log_error:
                logger.error(
                    f"Error in BaseCRUD.update with parameters object_id: {object_id}, action: {write}, current_user: {current_user}, status_code: {404} results in {log_error}"
                )
            logger.error(f"Error in BaseCRUD.update: {e}")
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not updated."
            )

    async def update_file(
        self, file_id: uuid.UUID, current_user: "CurrentUserData", file: UploadFile
    ) -> BaseModelType:
        """Updates a file."""
        try:
            # This does not really change anything in the metadata, but ensures that the access control is applied:
            # TBD: refactor into only checking the access control and not updating the metadata
            old_metadata = await self.read_by_id(file_id, current_user)
            same_metadata = await self.update(current_user, file_id, old_metadata)
            with open(
                f"/data/appdata/{self.data_directory}/{old_metadata.name}", "wb"
            ) as disk_file:
                disk_file.write(file.file.read())
            return same_metadata
        except Exception as e:
            logger.error(f"Error in BaseCRUD.update_file {file_id}: {e}")
            raise HTTPException(
                status_code=403,
                detail=f"{self.model.__name__} - Forbidden.",
            )

    async def update_file_metadata(
        self,
        file_id: uuid.UUID,
        current_user: "CurrentUserData",
        metadata: BaseSchemaTypeUpdate,
    ) -> BaseModelType:
        """Updates a file's metadata and renames the file on disk."""
        try:
            old_metadata = await self.read_by_id(file_id, current_user)
            old_metadata = old_metadata.model_dump()
            new_metadata = await self.update(current_user, file_id, metadata)
            rename(
                f"/data/appdata/{self.data_directory}/{old_metadata["name"]}",
                f"/data/appdata/{self.data_directory}/{new_metadata.name}",
            )
            return new_metadata
        except Exception as e:
            logger.error(f"Error in BaseCRUD.update_metadata_file {file_id}: {e}")
            raise HTTPException(
                status_code=403,
                detail=f"{self.model.__name__} - Forbidden.",
            )

    async def delete(  # noqa: C901
        self,
        current_user: "CurrentUserData",
        object_id: uuid.UUID,
    ) -> None:
        """Deletes an object."""
        try:
            model_alias = aliased(self.model)
            subquery = (
                select(model_alias.id).distinct().where(model_alias.id == object_id)
            )
            # subquery = self.policy_CRUD.filters_allowed(
            subquery = self.policy_crud.filters_allowed(
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
            await self.session.commit()

            # Delete all stand-alone orphan children of the object
            # might leave some children, that the current_user does not have access to,
            # so they might be floating alone - should be ok for now.
            hierarchy_CRUD = self.hierarchy_CRUD(session=self.session)
            children_relationships = await hierarchy_CRUD.read(
                current_user=current_user, parent_id=object_id
            )

            children_ids = [child.child_id for child in children_relationships]
            children_typelinks = await self._get_types_from_ids(children_ids)
            for child in children_typelinks:
                # TBD: refactor to auto recreation, of CRUD instane, when session changes.
                crud = registry_CRUDs.get(child.type)
                crud.session = self.session
                crud.policy_crud.session = self.session  # Add this
                crud.logging_crud.session = self.session  # Add this
                if not crud.allow_standalone:
                    all_parents = await hierarchy_CRUD.read(
                        current_user=current_user, child_id=child.id
                    )
                    if len(all_parents) == 1:
                        # async with crud as child_crud:
                        # child_crud = crud()
                        crud.session = self.session
                        await crud.delete(current_user=current_user, object_id=child.id)

            # Delete all hierarchy entries for the object
            # Delete all parent-child relationships, where object_id is parent:
            try:
                await hierarchy_CRUD.delete(
                    current_user=current_user, parent_id=object_id
                )
            except Exception:
                pass

            # Delete all parent-child relationships, where object_id is child:
            try:
                await hierarchy_CRUD.delete(
                    current_user=current_user, child_id=object_id
                )
            except Exception:
                pass

            # Delete all access policies, where object_id is resource:
            # The resource_id can be an identity_id!
            # TBD: write a test for deleting a policy, where the resource_id is an identity_id
            try:
                # async with self.policy_crud as policy_crud:
                await self.policy_crud.delete(
                    current_user,
                    AccessPolicyDelete(
                        resource_id=object_id,
                    ),
                )
            except Exception:
                pass
            if self.type == IdentityType:
                try:
                    # async with self.policy_crud as policy_crud:
                    await self.policy_crud.delete(
                        current_user,
                        AccessPolicyDelete(identity_id=object_id),
                    )
                except Exception:
                    pass

            # Create the successful access log
            access_log = AccessLogCreate(
                resource_id=object_id,
                action=own,
                identity_id=current_user.user_id,
                status_code=200,
            )
            await self.logging_crud.create(access_log)

            # Leave the identifier type link, as it's referred to the log table, which stays even after deletion
            # Only identifier-type links and logs stay, when a resource is deleted.
            # await self._delete_identifier_type_link(object_id)
            # self.session = self.logging_CRUD.add_log_to_session(
            #     access_log, self.session
            # )
            # self._add_log_to_session(object_id, own, current_user, 200)

            return None

        except Exception as e:
            await self.session.rollback()
            try:
                access_log = AccessLogCreate(
                    resource_id=object_id,
                    action=own,
                    identity_id=current_user.user_id,
                    status_code=404,
                )

                await self.logging_crud.create(access_log)
            except Exception as log_error:
                logger.error(
                    f"Error in BaseCRUD.delete with parameters object_id: {object_id}, action: {own}, current_user: {current_user}, status_code: {404} results in  {log_error}"
                )
            logger.error(f"Error in BaseCRUD.delete: {e}")
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not deleted."
            )

    async def remove_child_from_parent(
        self,
        child_id: uuid.UUID,
        parent_id: uuid.UUID,
        current_user: "CurrentUserData",
    ) -> None:
        """Deletes a member of this class from a parent (of another entity type)."""
        # check if child id refers to a type equal to self.model in identifiertypelink table:
        # if not, raise 404
        # if yes, delete the hierarchy entry
        if await self.check_identifier_type_link(child_id):
            hierarchy_CRUD = self.hierarchy_CRUD(session=self.session)
            deleted_rows = await hierarchy_CRUD.delete(
                current_user=current_user,
                parent_id=parent_id,
                child_id=child_id,
            )
            if deleted_rows == 0:
                raise HTTPException(status_code=404, detail="Hierarchy not found.")
            return None
        else:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found."
            )

    async def delete_file(
        self,
        file_id: uuid.UUID,
        current_user: "CurrentUserData",
    ) -> None:
        """Deletes a file."""
        try:
            file_metadata = await self.read_by_id(file_id, current_user)
            file_metadata = file_metadata.model_dump()
            await self.delete(current_user, file_id)
            remove(f"/data/appdata/{self.data_directory}/{file_metadata["name"]}")
            return None
        except Exception as e:
            logger.error(f"Error in BaseCRUD.delete_file {file_id}: {e}")
            raise HTTPException(
                status_code=403,
                detail=f"{self.model.__name__} - Forbidden.",
            )
