import logging
import uuid
from dataclasses import dataclass
from os import makedirs, path, remove, rename
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    List,
    Optional,
    Self,
    Type,
    TypeVar,
    cast,
)

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased, class_mapper, contains_eager, foreign, noload
from sqlmodel import SQLModel, asc, col, delete, desc, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from crud import registry_CRUDs
from crud.access import (
    AccessLoggingCRUD,
    AccessPolicyCRUD,
    IdentityHierarchyCRUD,
    ResourceHierarchyCRUD,
    get_types_from_ids,
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
from models.base import BaseExtendedSQLModel, BaseSQLModel

if TYPE_CHECKING:
    pass
from core.types import (
    Action,
    CollectionInclude,
    CollectionSort,
    CurrentUserData,
    IdentityType,
    ResourceType,
    SortDirection,
)

logger = logging.getLogger(__name__)

read = Action.read
write = Action.write
own = Action.own

BaseModelType = TypeVar("BaseModelType", bound=BaseSQLModel)
BaseSchemaTypeCreate = TypeVar("BaseSchemaTypeCreate", bound=SQLModel)
BaseSchemaTypeRead = TypeVar("BaseSchemaTypeRead", bound=SQLModel)
BaseSchemaTypeUpdate = TypeVar("BaseSchemaTypeUpdate", bound=SQLModel)


@dataclass(frozen=True)
class EntityCollectionSnapshot:
    items: list[BaseExtendedSQLModel]
    cursor: int


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
        directory: Optional[str] = None,
        allow_standalone: Optional[bool] = False,
        allow_public_create: Optional[bool] = False,
        session: Optional[AsyncSession] = None,
        extended_model: Optional[Type[SQLModel]] = None,
    ):
        """Provides a database session for CRUD operations.

        The session is typed as non-Optional `AsyncSession` because the contract
        of this class requires usage via `async with crud_instance:` which
        guarantees `__aenter__` populates the session before any method runs.
        When `session=None` is passed in, the attribute is initialised with a
        sentinel cast and replaced inside `__aenter__`.
        """
        # Cast acknowledges the contract: usage outside of `async with` is unsupported.
        self.session: AsyncSession = cast(AsyncSession, session)
        self._owns_session = False if session else True
        self.model = base_model
        self.data_directory = directory
        self.allow_standalone = allow_standalone
        self.allow_public_create = allow_public_create
        self.extended_model = extended_model or getattr(base_model, "Extended", None)
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

    async def __aenter__(self) -> Self:
        """Returns a database session."""
        if not self.session:
            self.session = await get_async_session()
            self.policy_crud = AccessPolicyCRUD(session=self.session)
            self.logging_crud = AccessLoggingCRUD(session=self.session)
            self._owns_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        if self._owns_session:
            await self.session.close()
            self.session = cast(AsyncSession, None)
            self._owns_session = False

    def bind_session(self, session: AsyncSession) -> None:
        """Use a caller-owned session for this CRUD operation."""
        self.session = session
        self.policy_crud = AccessPolicyCRUD(session=session)
        self.logging_crud = AccessLoggingCRUD(session=session)
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
        type: Optional[ResourceType | IdentityType] = None,
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
        self, object_id: uuid.UUID, type: Optional[ResourceType | IdentityType] = None
    ):
        """Creates an resource type link entry."""
        statement = self._add_identifier_type_link_to_session(object_id, type)
        await self.session.exec(statement)
        await self.session.commit()

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
        object: BaseSchemaTypeCreate | dict[str, Any],
        current_user: Optional["CurrentUserData"] = None,
        parent_id: Optional[uuid.UUID] = None,
        inherit: Optional[bool] = False,
        # TBD: add tests in protected resource to check public and public_action creation:
        # TBD: separate concerns and remove creation of additional polices from the create method,
        # as it is not the responsibility of the CRUD to create additional policies,
        # but only to create the resource, access log the creation and give the permission to the creator.
        # Caller should call AccessPolicyCRUD.create to create additional policies, if needed.
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

        is_public_creation = False
        database_object: Optional[BaseModelType] = None
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
            # `id` is populated by `default_factory=uuid.uuid4` on the model field.
            assert database_object.id is not None
            await self._write_identifier_type_link(database_object.id)
            self.session.add(database_object)

            # Create access log
            # if not is_public_creation:
            access_log = AccessLogCreate(
                resource_id=database_object.id,
                action=own,
                identity_id=current_user.user_id if current_user else None,
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

            # Create owner access policy
            # if not is_public_creation:
            access_policy = AccessPolicyCreate(
                resource_id=database_object.id,
                action=own,
                identity_id=current_user.user_id if current_user else None,
            )

            await self.policy_crud.create(
                access_policy, current_user, allow_override=True
            )
            if parent_id:
                hierarchy_CRUD = self.hierarchy_CRUD(session=self.session)

                await hierarchy_CRUD.create(
                    current_user=current_user,
                    parent_id=parent_id,
                    child_id=database_object.id,
                    inherit=inherit,
                )

            # Commit the object to the database
            await self.session.commit()
            await self.session.refresh(database_object)

            # Create public access policy
            # TBD: move this responsibility to the caller -
            # see comments above in the method signature.
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
                    database_object_id: Optional[uuid.UUID] = getattr(
                        database_object, "id", None
                    )
                    if database_object_id and current_user:
                        access_log = AccessLogCreate(
                            resource_id=database_object_id,
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
            object={"name": file.filename or "unnamed"},
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

    # TBD: implement a create_if_not_exists method
    # or UPSERT (update or insert)

    # TBD: add "skip_services: Optional[bool] = False"
    # to avoid calling orchestrator from services
    # otherwise it creates a loop!
    # TBD: add skip and limit
    # limit is already implemented, but also limits the children!
    # use with pagination:
    # Model = await model_crud.read(order_by=[Model.name], limit=10)
    # Model = await model_crud.read(order_by=[Model.name], limit=10, offset=10)
    async def read_entity_snapshot(
        self,
        current_user: Optional["CurrentUserData"] = None,
        includes: Optional[set[CollectionInclude]] = None,
        sort: Optional[CollectionSort] = None,
        direction: SortDirection = SortDirection.ascending,
        parent_id: Optional[uuid.UUID] = None,
    ) -> EntityCollectionSnapshot:
        """Reads an optionally enriched entity collection and mutation cursor."""
        requested_includes = includes or set()
        cursor = await self.logging_crud.read_cursor()
        order_by = None
        if sort == CollectionSort.creation_date:
            creation_date = self.logging_crud.creation_date_expression(
                col(self.model.id)
            )
            date_order = (
                desc(creation_date).nullslast()
                if direction == SortDirection.descending
                else asc(creation_date).nullslast()
            )
            order_by = [date_order, asc(col(self.model.id))]

        filters = None
        if parent_id is not None:
            hierarchy_crud = self.hierarchy_CRUD(session=self.session)
            hierarchies = await hierarchy_crud.read(
                current_user=current_user, parent_id=parent_id
            )
            child_ids = [hierarchy.child_id for hierarchy in hierarchies]
            filters = [col(self.model.id).in_(child_ids)]

        entities = await self.read(
            current_user=current_user, filters=filters, order_by=order_by
        )
        entity_ids = [cast(Any, entity).id for entity in entities]
        date_includes = {
            CollectionInclude.creation_date,
            CollectionInclude.last_modified_date,
        }
        metadata = (
            await self.logging_crud.read_entity_metadata(entity_ids)
            if requested_includes & date_includes
            else {}
        )
        access_rights = (
            await self.policy_crud.read_access_rights(
                entity_ids=entity_ids,
                model=self.model,
                current_user=current_user,
            )
            if CollectionInclude.access_right in requested_includes
            else {}
        )

        if self.extended_model is None:
            raise ValueError(f"{self.model.__name__} has no Extended schema")
        items = []
        for entity in entities:
            item = self.extended_model.model_validate(entity)
            entity_id = cast(Any, entity).id
            entity_metadata = metadata.get(entity_id, {})
            if CollectionInclude.creation_date in requested_includes:
                item.creation_date = entity_metadata.get("creation_date")
            if CollectionInclude.last_modified_date in requested_includes:
                item.last_modified_date = entity_metadata.get("last_modified_date")
            if CollectionInclude.access_right in requested_includes:
                item.access_right = access_rights.get(entity_id)
            items.append(item)

        return EntityCollectionSnapshot(items=items, cursor=cursor)

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
        failed_result: Optional[BaseModelType] = None
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

                # Skip relationships that are not part of the configured hierarchy
                # (e.g. direct-FK side tables like User.user_profile / User.user_account).
                # Their access is governed by access to the parent model, and adding a
                # WHERE on `related_model.id` here without a corresponding join causes
                # cartesian-product SAWarnings; let their declared `lazy=` strategy load them.
                is_hierarchy_relationship = any(
                    (self.entity_type == parent and related_type in children)
                    or (self.entity_type in children and related_type == parent)
                    for parent, children in self.relations.items()
                )
                if is_hierarchy_relationship:
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
                                col(self.model.id)
                                == foreign(col(aliased_hierarchy.parent_id)),
                            )
                            statement = statement.outerjoin(
                                related_model,
                                col(related_model.id)
                                == foreign(col(aliased_hierarchy.child_id)),
                            )
                            if self.hierarchy is ResourceHierarchy:
                                # `aliased_hierarchy` was built from `self.hierarchy`, so in
                                # this branch its underlying class is ResourceHierarchy and
                                # therefore has an `order` column. Pyright cannot follow this
                                # correlation across the `aliased(...)` call.
                                statement = statement.order_by(asc(col(aliased_hierarchy.order)))  # type: ignore[attr-defined]
                            else:
                                statement = statement.order_by(
                                    asc(col(related_model.id))
                                )
                        elif self.entity_type in children and related_type == parent:
                            # self.model is a child, join on child_id
                            statement = statement.outerjoin(
                                aliased_hierarchy,
                                col(self.model.id)
                                == foreign(col(aliased_hierarchy.child_id)),
                            )
                            statement = statement.outerjoin(
                                related_model,
                                col(related_model.id)
                                == foreign(col(aliased_hierarchy.parent_id)),
                            )
                            # here no ordering, as parents don't have an order seen from the child:
                            statement = statement.order_by(asc(col(related_model.id)))

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
                statement = statement.order_by(asc(col(self.model.id)))

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

            failed_result = results[-1]
            # TBD: add logging to accessed children!
            access_logs = [
                AccessLogCreate(
                    resource_id=result.id,  # result might not be available here?
                    action=read,
                    identity_id=current_user.user_id if current_user else None,
                    status_code=200,
                )
                for result in results
            ]
            await self.logging_crud.create_many(access_logs)

            return results
        except Exception as err:
            failed_resource_id = failed_result.id if failed_result is not None else None
            if failed_resource_id is not None:
                try:
                    access_log = AccessLogCreate(
                        resource_id=failed_resource_id,
                        action=read,
                        identity_id=current_user.user_id if current_user else None,
                        status_code=404,
                    )
                    await self.logging_crud.create(access_log)
                except Exception as log_error:
                    logger.error(
                        f"Unable to log failed {self.model.__name__} read: {log_error}"
                    )
            logger.error(
                (
                    f"Error in BaseCRUD.read for model {self.model.__name__} with "
                    f"select_args: {select_args},"
                    f"filters: {filters},"
                    f"joins: {joins},"
                    f"order_by: {order_by},"
                    f"group_by: {group_by},"
                    f"having: {having}, "
                    f"limit: {limit},"
                    f"offset: {offset},"
                    f"action: {read},"
                    f"current_user: {current_user},"
                    f"status_code: {404}"
                    f"results in {err}"
                )
            )
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found."
            ) from err

    async def read_by_id(
        self,
        id: uuid.UUID,
        current_user: Optional["CurrentUserData"] = None,
    ):
        """Reads an object by id."""

        object = await self.read(
            current_user=current_user,
            filters=[col(self.model.id) == id],
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
        file_name = getattr(file, "name", None) or "file"
        return FileResponse(
            f"/data/appdata/{self.data_directory}/{file_name}",
            filename=file_name,
        )

    async def update(
        self,
        current_user: "CurrentUserData",
        object_id: uuid.UUID,
        new: BaseSchemaTypeUpdate | SQLModel,
    ) -> BaseModelType:
        """Updates an object."""
        session = self.session
        try:
            statement = select(self.model).where(col(self.model.id) == object_id)

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
            assert current.id is not None
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
                current_id = (
                    getattr(current, "id", None) if "current" in locals() else None  # type: ignore[possibly-undefined]
                )
                if current_id and current_user:
                    access_log = AccessLogCreate(
                        resource_id=current_id,
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
            old_metadata_name = getattr(old_metadata, "name", None) or "file"
            # Use the read result directly for update; only access control matters here.
            same_metadata = await self.update(current_user, file_id, old_metadata)
            with open(
                f"/data/appdata/{self.data_directory}/{old_metadata_name}",
                "wb",
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
            new_metadata_name = getattr(new_metadata, "name", None) or "file"
            rename(
                f"/data/appdata/{self.data_directory}/{old_metadata['name']}",
                f"/data/appdata/{self.data_directory}/{new_metadata_name}",
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
                select(col(model_alias.id))
                .distinct()
                .where(col(model_alias.id) == object_id)
            )
            # subquery = self.policy_CRUD.filters_allowed(
            subquery = self.policy_crud.filters_allowed(
                statement=subquery,
                action=own,
                model=model_alias,
                current_user=current_user,
            )
            statement = delete(self.model).where(col(self.model.id).in_(subquery))
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
            children_typelinks = await get_types_from_ids(self.session, children_ids)
            for child_id, idx in zip(children_ids, range(len(children_ids))):
                # TBD: refactor to auto recreation, of CRUD instane, when session changes.
                crud_class = registry_CRUDs.get(children_typelinks[idx])
                if crud_class:
                    child_crud = crud_class()
                    child_crud.bind_session(self.session)
                    if not child_crud.allow_standalone:
                        all_parents = await hierarchy_CRUD.read(
                            current_user=current_user, child_id=child_id
                        )
                        if len(all_parents) == 1:
                            await child_crud.delete(
                                current_user=current_user, object_id=child_id
                            )

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
