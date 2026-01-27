import logging
from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

# from pprint import pprint
from fastapi import HTTPException
from sqlalchemy.orm import aliased

# from sqlalchemy import union_all
from sqlmodel import SQLModel, and_, delete, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import (
    Action,
    CurrentUserData,
    IdentityType,
    ResourceType,
)
from models.access import (
    AccessLog,
    AccessLogCreate,
    AccessLogRead,
    AccessPermission,
    AccessPolicy,
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessPolicyRead,
    AccessPolicyUpdate,
    AccessRequest,
    BaseHierarchy,
    BaseHierarchyCreate,
    IdentifierTypeLink,
    IdentityHierarchy,
    IdentityHierarchyRead,
    ResourceHierarchy,
    ResourceHierarchyRead,
)

logger = logging.getLogger(__name__)

read = Action.read
write = Action.write
own = Action.own


class AccessPolicyCRUD:
    """CRUD for access control policies"""

    def __init__(self):
        """Initializes the CRUD for access control policies."""
        self.session = None

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    def __get_resource_inheritance_common_table_expression(
        self,
        base_resource_ids: select,  # TBD: change this to List[UUID]?
    ):
        """Checks if the resource inherits permissions from a parent resource"""
        ResourceHierarchyAlias = aliased(ResourceHierarchy)

        hierarchy_cte = (
            select(ResourceHierarchy.parent_id.label("resource_id"))
            .where(ResourceHierarchy.parent_id.in_(base_resource_ids))
            .cte(recursive=True)
        )

        hierarchy_cte = hierarchy_cte.union_all(
            select(ResourceHierarchyAlias.child_id.label("resource_id")).where(
                ResourceHierarchyAlias.parent_id == hierarchy_cte.c.resource_id,
                ResourceHierarchyAlias.inherit.is_(True),
            ),
        )

        return hierarchy_cte

    def __get_identity_inheritance_common_table_expression(
        self, base_identity_id: UUID
    ):
        """Checks if the resource inherits permissions from a parent resource"""
        IdentityHierarchyAlias = aliased(IdentityHierarchy)

        hierarchy_cte = (
            select(IdentityHierarchy.child_id.label("identity_id"))
            .where(IdentityHierarchy.child_id == base_identity_id)
            .cte(recursive=True)
        )

        hierarchy_cte = hierarchy_cte.union_all(
            select(IdentityHierarchyAlias.parent_id.label("identity_id")).where(
                IdentityHierarchyAlias.child_id == hierarchy_cte.c.identity_id,
                IdentityHierarchyAlias.inherit.is_(True),
            ),
        )

        return hierarchy_cte

    def __always_allow(
        self,
        policy: AccessPolicyCreate,
        current_user: CurrentUserData,
    ):

        if "Admin" in current_user.azure_token_roles:
            return True
        # users can always create access policy for their own user object:
        elif policy.resource_id == current_user.user_id:
            return True
        # users can always create read access policy for azure groups, they are member of:
        elif (
            current_user.azure_token_groups
            and policy.resource_id in current_user.azure_token_groups
            and policy.action == write
        ):
            return True
        else:
            # print("=== AccessPolicyCRUD.__always_allow - policy ===")
            # print(policy)
            # print("=== AccessPolicyCRUD.__always_allow - current_user ===")
            # print(current_user)
            return False

    def filters_allowed(
        self,
        statement: select,
        action: "Action",
        model: SQLModel = AccessPolicy,
        current_user: Optional["CurrentUserData"] = None,
    ):
        """Finds all resources of a certain type and action that the user has permission to access"""
        # TBD: implement this
        # ✔︎ find all public resources of the given type and action
        # ✔︎ find all resources of the given type and action that the user has permission to access
        # ✔︎ find all resources of the given type and action that the user has permission to access through resource inheritance
        # ✔︎ find all resources of the given type and action that the user has permission to access through group membership (identity inheritance)
        # ✔︎ find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance
        # ✔︎ find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access
        # ✔︎ find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access and admin override

        # Permission overrides:
        # own includes write and read
        # write includes read
        if action == read:
            # action = ["own", "write", "read"]
            action = [own, write, read]
        elif action == write:
            # action = ["own", "write"]
            action = [own, write]
        elif action == own:
            # action = ["own"]
            action = [own]
        else:
            # TBD: write test for this: if pydantic works on verifying action types,
            # a 422 or type error should be raised before this line!
            logger.error("Invalid action provided.")
            raise HTTPException(status_code=400, detail="Bad request: invalid action.")

        # TBD: for inheritance:
        # - wherever resource_id is used, it needs to check inheritance from Resource hierarchy recursively (self-join) until no parent found any more
        # - wherever identity_id is used, it needs to check inheritance from Identity hierarchy recursively (self-join) until no parent found any more
        # get all parent resource id's, that the resource inherits from
        # get all parent identity id's, that the identity inherits from
        # How do all the actions get into play - do I really need to check all possible combinations for the required action?

        # only public resources can be accessed without a user:
        if not current_user:
            # TBD: refactor into using resource hierarchy and access policy also for public resources!
            # The only thing, that is different here is, that
            # - there is no identity_id to check and
            # - public must be set to true
            subquery = (
                select(AccessPolicy.resource_id)
                .where(AccessPolicy.action.in_(action))
                .where(AccessPolicy.public)
            )
            if (model == AccessPolicy) or (model == AccessLog):
                statement = statement.where(model.resource_id.in_(subquery))
            else:
                statement = statement.where(model.id.in_(subquery))
            # TBD: avoid a return in the the middle of the function!
            return statement
        # Admins can access everything:
        elif (
            current_user.azure_token_roles and "Admin" in current_user.azure_token_roles
        ):
            # TBD: avoid a return in the the middle of the function!
            return statement
        # Users can access the resources, they have permission for including public resources:
        else:
            # Create the common table expression (CTE) for the identity hierarchy
            identity_hierarchy_cte = (
                self.__get_identity_inheritance_common_table_expression(
                    current_user.user_id
                )
            )

            # Base resources for access check
            base_resource_ids = select(AccessPolicy.resource_id).where(
                AccessPolicy.action.in_(action),
                or_(
                    AccessPolicy.identity_id.in_(
                        select(identity_hierarchy_cte.c.identity_id)
                    ),
                    AccessPolicy.identity_id == current_user.user_id,
                    AccessPolicy.public,
                ),
            )

            # Create the common table expression (CTE) for the resource hierarchy
            resource_hierarchy_cte = (
                self.__get_resource_inheritance_common_table_expression(
                    base_resource_ids
                )
            )

        if (model == AccessPolicy) or (model == AccessLog):
            statement = statement.where(
                or_(
                    # TBD: both should be returned in the new function "__get_accessible_resource_ids"
                    model.resource_id.in_(
                        select(resource_hierarchy_cte.c.resource_id)
                    ),  # all inherited resources
                    model.resource_id.in_(
                        # subquery
                        base_resource_ids
                    ),  # all resources with direct access
                )
            )
        else:
            statement = statement.where(
                or_(
                    model.id.in_(
                        select(resource_hierarchy_cte.c.resource_id)
                    ),  # all inherited resources
                    model.id.in_(
                        # subquery
                        base_resource_ids
                    ),  # all resources with direct access
                )
            )

        return statement

    async def allows(
        self,
        access_request: AccessRequest,
    ) -> bool:
        """Checks if the user has permission including inheritance to perform the action on the resource"""
        resource_id = access_request.resource_id
        action = access_request.action
        current_user = access_request.current_user

        # Necessary as otherwise an empty database could never get data into it.
        if (
            current_user
            and current_user.azure_token_roles
            and "Admin" in current_user.azure_token_roles
        ):
            return True

        try:
            query = select(AccessPolicy)
            if resource_id:
                query = query.where(
                    AccessPolicy.resource_id == resource_id,
                )

            query = self.filters_allowed(query, action, current_user=current_user)

            # TBD: refactor for correct session handling!
            async with self:
                # Only one policy per resource - action - identity combination is allowed!
                response = await self.session.exec(query)
                results = response.all()

            for result in results:
                if result.resource_id == resource_id:
                    return True
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            print("=== Error in AccessPolicyCRUD.ALLOWS - fails ===")
            raise HTTPException(status_code=403, detail="Forbidden.")

        return False

    async def check_access(
        self,
        resource_id: UUID,
        current_user: Optional[CurrentUserData] = None,
    ) -> AccessPermission:
        """Checks the access level of the user to the resource."""
        try:
            if await self.allows(
                AccessRequest(
                    resource_id=resource_id,
                    action=own,
                    current_user=current_user,
                )
            ):
                return AccessPermission(
                    resource_id=resource_id,
                    action=own,
                )
            elif await self.allows(
                AccessRequest(
                    resource_id=resource_id,
                    action=write,
                    current_user=current_user,
                )
            ):
                return AccessPermission(
                    resource_id=resource_id,
                    action=write,
                )
            elif await self.allows(
                AccessRequest(
                    resource_id=resource_id,
                    action=read,
                    current_user=current_user,
                )
            ):
                return AccessPermission(
                    resource_id=resource_id,
                    action=read,
                )
            else:
                return AccessPermission(
                    resource_id=resource_id,
                    action=None,
                )

        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=403, detail="Forbidden.")

    async def create(
        self,
        policy: AccessPolicyCreate,
        current_user: Optional[CurrentUserData] = None,
        allow_override: bool = False,
        *args,
    ) -> AccessPolicyRead:
        """Creates a new access control policy.

        Args:
            policy: The access policy to create
            current_user: The user creating the policy (optional if allow_override=True)
            allow_override: If True, bypasses all authorization checks

        Raises:
            HTTPException(403): If authorization checks fail
            HTTPException(409): If policy already exists
        """
        # Note: the current_user is the one who creates the policy for the identity_id in the policy!
        try:
            policy = AccessPolicy.model_validate(policy)

            # Handle authorization
            if allow_override:
                # When overriding without authentication, only public policies allowed
                if not current_user and not policy.public:
                    raise HTTPException(status_code=403, detail="Forbidden.")
                # Skip all authorization checks
                pass
            elif not current_user:
                # current_user required when not overriding
                raise HTTPException(status_code=403, detail="Forbidden.")
            elif self.__always_allow(policy, current_user):
                # User has inherent permission (admin, own resource, group member)
                pass
            else:
                # Check explicit access via read
                response = await self.read(
                    current_user=current_user,
                    resource_id=policy.resource_id,
                    action=own,
                )
                if not response:
                    raise HTTPException(
                        status_code=404, detail="Access policy not found."
                    )

            self.session.add(policy)
            await self.session.commit()
            await self.session.refresh(policy)
            return policy
        except Exception as err:
            if "duplicate key value violates unique constraint" in str(err):
                raise HTTPException(
                    status_code=409,
                    detail="Access policy for identity and resource already exists. Update instead of create.",
                )
            else:
                logger.error(f"Error in creating policy: {err}")
                print(err)
                raise HTTPException(status_code=403, detail="Forbidden.")

    async def read(
        self,
        # Who is requesting the policies?
        current_user: Optional["CurrentUserData"] = None,
        # What policy is requested? (The identity can be another user!)
        # For example look at who else has access to the resource with resource_id?
        # Or what resources has another user with identity_id access to?
        # and what actions for the above?
        identity_id: Optional[UUID] = None,
        identity_type: Optional[IdentityType] = None,
        resource_id: Optional[UUID] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[Action] = None,
        public: Optional[bool] = None,
    ) -> List[AccessPolicyRead]:
        """Reads access control policies based on the provided parameters."""

        try:
            query = select(AccessPolicy)
            query = self.filters_allowed(query, own, current_user=current_user)

            # TBD: write tests for admin case?
            # for admin access, resource_id and action can be None!

            if identity_id is not None:
                query = query.where(AccessPolicy.identity_id == identity_id)
            if identity_type is not None:
                query = query.join(
                    IdentifierTypeLink,
                    IdentifierTypeLink.id == AccessPolicy.resource_id,
                    # note: the queried identity is a the resource_id in the AccessRequest!
                ).where(IdentifierTypeLink.type == identity_type)
            if resource_id is not None:
                query = query.where(AccessPolicy.resource_id == resource_id)
            if resource_type is not None:
                query = query.join(
                    IdentifierTypeLink,
                    IdentifierTypeLink.id == AccessPolicy.resource_id,
                ).where(IdentifierTypeLink.type == resource_type)
            if action is not None:
                query = query.where(AccessPolicy.action == action)
            if public is True:
                query = query.where(AccessPolicy.public)

            response = await self.session.exec(query)
            results = response.all()

            if not results:
                return []

            return results
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found.")

    async def read_access_policies_by_resource_id(
        self,
        current_user: CurrentUserData,
        resource_id: UUID,
    ) -> List[AccessPolicyRead]:
        """Returns all access policies by resource id."""
        try:
            access_policies = await self.read(current_user, resource_id=resource_id)
            return access_policies
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access policies not found.")

    async def read_access_policies_by_resource_type(
        self,
        current_user: CurrentUserData,
        resource_type: ResourceType,
    ) -> List[AccessPolicyRead]:
        """Returns all access policies by resource type."""
        try:
            access_policies = await self.read(current_user, resource_type=resource_type)
            return access_policies
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access policies not found.")

    async def read_access_policies_for_identity(
        self,
        current_user: CurrentUserData,
        identity_id: UUID,
    ) -> List[AccessPolicyRead]:
        """Returns a User with linked Groups from the database."""
        try:
            access_policies = await self.read(current_user, identity_id=identity_id)
            return access_policies
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access policies not found.")

    async def read_access_policies_by_identity_type(
        self,
        current_user: CurrentUserData,
        identity_type: IdentityType,
    ) -> List[AccessPolicyRead]:
        """Returns all access policies by resource type."""
        try:
            access_policies = await self.read(current_user, identity_type=identity_type)
            return access_policies
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access policies not found.")

    # strictly not fulfilling REST principles for PUT operations, as the id of the access policy changes.
    # TBD: refactor this to keep the id of the access policy.
    async def update(
        self,
        current_user: Optional["CurrentUserData"],
        access_policy: AccessPolicyUpdate,
    ) -> AccessPolicyRead:
        """Deletes an existing policy if exists already and creates a new access control policy."""

        try:
            # TBD: add business logic: can last owner delete it's owner rights?
            # => no, there needs to be another owner left, so last downgrade from owner should not be accepted.
            updated_policy = None
            # Creates a new policy if action not provided but new_action is provided.
            if not hasattr(access_policy, "action"):
                query = select(AccessPolicy).where(
                    AccessPolicy.resource_id == access_policy.resource_id
                )
                query = self.filters_allowed(query, own, current_user=current_user)
                access_check_response = await self.session.exec(query)
                current_access_policy = access_check_response.unique().all()
                if not current_access_policy:
                    logger.info("Access policy not found for update.")
                    raise HTTPException(
                        status_code=404, detail="Access policy not found."
                    )
                new_policy = AccessPolicyCreate(
                    resource_id=access_policy.resource_id,
                    identity_id=access_policy.identity_id,
                    action=access_policy.new_action,
                    public=access_policy.public,
                )
                updated_policy = await self.create(new_policy, current_user)
            else:
                old_policy = AccessPolicy(
                    resource_id=access_policy.resource_id,
                    identity_id=access_policy.identity_id,
                    action=access_policy.action,
                    public=access_policy.public,
                )
                query = select(AccessPolicy).where(
                    AccessPolicy.resource_id == old_policy.resource_id,
                    AccessPolicy.identity_id == old_policy.identity_id,
                    AccessPolicy.action == old_policy.action,
                    AccessPolicy.public == old_policy.public,
                )
                query = self.filters_allowed(query, own, current_user=current_user)
                access_check_response = await self.session.exec(query)
                current_access_policy = access_check_response.unique().one()
                if not current_access_policy:
                    logger.info("Access policy not found for update.")
                    raise HTTPException(
                        status_code=404, detail="Access policy not found."
                    )

                await self.delete(current_user, old_policy)
                new_policy = AccessPolicy(
                    id=current_access_policy.id,  # keep the id of the old policy
                    resource_id=access_policy.resource_id,
                    identity_id=access_policy.identity_id,
                    action=access_policy.new_action,
                    public=access_policy.public,
                )
                self.session.add(new_policy)
                await self.session.commit()
                await self.session.refresh(new_policy)
                updated_policy = new_policy
            return updated_policy

        except Exception as e:
            logger.error(f"Error in updating policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found.")

    # TBD: enable delete all policies for a resource / for an identity
    async def delete(
        self,
        current_user: Optional["CurrentUserData"],
        access_policy: AccessPolicyDelete,
    ) -> int:
        """Deletes an access control policy."""

        try:
            resource_id, identity_id, action, public = (
                access_policy.resource_id,
                access_policy.identity_id,
                access_policy.action,
                access_policy.public,
            )

            # # This where is extremely important to only delete the requested policy!
            # TBD: write tests, where one or more of those parameters are None/not provided!
            statement = delete(AccessPolicy)
            statement = self.filters_allowed(statement, own, current_user=current_user)
            if resource_id:
                statement = statement.where(AccessPolicy.resource_id == resource_id)
            if identity_id:
                statement = statement.where(AccessPolicy.identity_id == identity_id)
            if action:
                statement = statement.where(AccessPolicy.action == action)
            # TBD: check here if identity_id is not None and public is not None: either one needs to be left!
            # or create a AccessPolicyDelete model, that has all fields optional,
            # but uses the same validation as AccessPolicyCreate
            if public is not None:
                statement.where(AccessPolicy.public == public)

            # TBD: at least one owner needs to be left!

            response = await self.session.exec(statement)

            await self.session.commit()

            return response.rowcount

        except Exception as e:
            logger.error(f"Error in deleting policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found.")


class AccessLoggingCRUD:
    """Logging access attempts to database."""

    def __init__(self):
        self
        self.policy_crud = AccessPolicyCRUD()

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def create(self, access_log: AccessLogCreate) -> AccessLog:
        """Creates an access log entry."""
        try:
            access_log = AccessLog.model_validate(access_log)
            self.session.add(access_log)
            await self.session.commit()
            await self.session.refresh(access_log)

            # print("=== AccessLoggingCRUD.create - access_log ===")
            # pprint(access_log)

            return access_log
        except Exception as e:
            logger.error(f"Error in creating log: {e}")
            raise HTTPException(status_code=400, detail="Bad request: logging failed.")

    async def read(
        self,
        current_user: Optional["CurrentUserData"] = None,
        resource_id: Optional[UUID] = None,
        identity_id: Optional[UUID] = None,
        action: Optional[Action] = None,
        ascending_order_by: Optional[str] = None,
        descending_order_by: Optional[str] = None,
        limit: Optional[int] = None,
        status_code: Optional[int | None] = 200,
        required_action: Optional[Action] = Action.own,
    ) -> List[AccessLogRead]:
        """Reads access logs based on the provided parameters."""
        try:
            session = self.session
            statement = select(AccessLog)
            statement = self.policy_crud.filters_allowed(
                statement, required_action, AccessLog, current_user
            )
            if resource_id:
                statement = statement.where(AccessLog.resource_id == resource_id)
            if identity_id:
                statement = statement.where(AccessLog.identity_id == identity_id)
            if action:
                statement = statement.where(AccessLog.action == action)
            if status_code:
                statement = statement.where(AccessLog.status_code == status_code)
            if ascending_order_by:
                statement = statement.order_by(ascending_order_by.asc())
            if descending_order_by:
                statement = statement.order_by(descending_order_by.desc())
            if limit:
                statement = statement.limit(limit)

            response = await session.exec(statement)
            results = response.all()

            if not results:
                return []

            return results
        except Exception as e:
            logger.error(f"Error in reading log: {e}")
            raise HTTPException(status_code=404, detail="Access logs not found.")

    async def read_access_logs_by_resource_id_and_identity_id(
        self,
        current_user: CurrentUserData,
        resource_id: Optional[UUID] = None,
        identity_id: Optional[UUID] = None,
    ) -> List[AccessLogRead]:
        """Returns all access logs by resource id."""
        try:
            access_logs = await self.read(
                current_user,
                resource_id=resource_id,
                identity_id=identity_id,
                status_code=None,
            )
            return access_logs
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access logs not found.")

    async def read_resource_created_at(
        self,
        resource_id: UUID,
        current_user: Optional["CurrentUserData"] = None,
    ) -> datetime:
        """Reads the first access log with action "Own" for a resource id - corresponds to create."""
        try:
            first_owner_entry = await self.read(
                current_user,
                resource_id,
                status_code=201,
                action=Action.own,
                ascending_order_by=AccessLog.time,
                limit=1,
                required_action=Action.read,
            )
            return first_owner_entry[0].time
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access logs not found.")

    async def read_resource_last_accessed_at(
        self,
        resource_id: UUID,
        action: Action = Action.own,
        current_user: Optional["CurrentUserData"] = None,
    ) -> AccessLogRead:
        """Reads the last access log for a resource id."""
        try:
            last_accessed_entry = await self.read(
                current_user,
                resource_id,
                descending_order_by=AccessLog.time,
                limit=1,
                status_code=None,
                required_action=action,
            )
            return last_accessed_entry[0]
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access logs not found.")

    async def read_resource_last_modified_at(
        self,
        resource_id: UUID,
        current_user: Optional["CurrentUserData"] = None,
    ) -> datetime:
        """Reads the last modification (or creation) date for a resource id."""
        try:
            last_write_log = await self.read(
                current_user,
                resource_id,
                status_code=200,
                action=Action.write,
                descending_order_by=AccessLog.time,
                limit=1,
                required_action=Action.read,
            )
            if last_write_log:
                last_write_date = last_write_log[0].time
            else:
                last_write_date = await self.read_resource_created_at(
                    resource_id=resource_id, current_user=current_user
                )
            return last_write_date
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access logs not found.")

    async def read_resource_access_count(
        self,
        resource_id: UUID,
        current_user: Optional["CurrentUserData"] = None,
    ):
        """Reads the number of access logs for a resource id."""
        try:
            access_count = await self.read(
                current_user, resource_id, required_action=Action.read, status_code=None
            )
            if len(access_count) == 0:
                print(
                    "=== AccessLoggingCRUD.read_resource_access_count - no access logs found ==="
                )
                raise HTTPException(status_code=404, detail="Access logs not found.")
            return len(access_count)
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access logs not found.")


BaseHierarchyModel = TypeVar("BaseHierarchyModel", bound=SQLModel)
BaseHierarchyModelCreate = TypeVar("BaseHierarchyModelCreate", bound=SQLModel)
BaseHierarchyModelRead = TypeVar("BaseHierarchyModelRead", bound=SQLModel)


class BaseHierarchyCRUD(
    Generic[
        BaseHierarchyModel,
        BaseHierarchyModelCreate,
        BaseHierarchyModelRead,
    ]
):
    """Base CRUD for hierarchies."""

    def __init__(self, hierarchy: BaseHierarchy, base_model: Type[BaseHierarchyModel]):
        self.session = None
        self.hierarchy = hierarchy
        self.model = base_model
        self.policy_crud = AccessPolicyCRUD()

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def create(
        self,
        current_user: CurrentUserData,
        parent_id: UUID,
        child_type: ResourceType,
        child_id: UUID,
        inherit: Optional[bool] = False,
    ) -> BaseHierarchyModelRead:
        """Checks access and type matching and potentially creates parent-child relationship."""
        try:
            child_access_request = AccessRequest(
                resource_id=child_id,
                action=Action.own,
                current_user=current_user,
            )
            if not await self.policy_crud.allows(child_access_request):
                raise HTTPException(status_code=403, detail="Forbidden.")
            statement = select(IdentifierTypeLink.type)
            # only selects, the IdentifierTypeLinks, that the user has write access to.
            statement = self.policy_crud.filters_allowed(
                statement, Action.write, IdentifierTypeLink, current_user
            )
            statement = statement.where(IdentifierTypeLink.id == parent_id)

            result = await self.session.exec(statement)

            parent_type = result.one()

            allowed_children = self.hierarchy.get_allowed_children_types(parent_type)
            if child_type in allowed_children:
                relation = self.model(
                    parent_id=parent_id,
                    child_id=child_id,
                    inherit=inherit,
                )
                relation = self.model.model_validate(relation)
                self.session.add(relation)
                await self.session.commit()
                await self.session.refresh(relation)
                return relation
            else:
                logger.error("Bad request: child type not allowed for parent.")
                raise HTTPException(
                    status_code=403,
                    detail="Bad request: child type not allowed for parent.",
                )
        except Exception as err:
            logger.error(f"Error in creating hierarchy: {err}")
            raise HTTPException(status_code=403, detail="Forbidden.")

    # TBD: consider exposing as endpoint and/or sock.io event?
    # Currently not absolutely necesary,
    # as all children get transferred in the read event of a parent resource
    async def read(
        self,
        current_user: CurrentUserData,
        parent_id: Optional[UUID] = None,
        child_id: Optional[UUID] = None,
    ) -> List[BaseHierarchyModelRead]:
        """Reads all parent-child relationships."""
        try:
            if parent_id is None and child_id is None:
                raise HTTPException(
                    status_code=400, detail="Bad request: no id provided."
                )

            identifier_type_link_parent = aliased(IdentifierTypeLink)
            identifier_type_link_child = aliased(IdentifierTypeLink)
            # TBD: is a condition required if only parent_id or child_id is provided?
            statement = (
                select(self.model)
                .join(
                    identifier_type_link_parent,
                    identifier_type_link_parent.id == self.model.parent_id,
                )
                .join(
                    identifier_type_link_child,
                    identifier_type_link_child.id == self.model.child_id,
                )
            )
            statement = self.policy_crud.filters_allowed(
                statement, Action.read, identifier_type_link_parent, current_user
            )
            statement = self.policy_crud.filters_allowed(
                statement, Action.read, identifier_type_link_child, current_user
            )
            if parent_id:
                statement = statement.where(self.model.parent_id == parent_id)
            if child_id:
                statement = statement.where(self.model.child_id == child_id)

            response = await self.session.exec(statement)
            results = response.all()

            if not results:
                return []

            return results
        except Exception as err:
            logger.error(f"Error in reading hierarchy: {err}")
            raise HTTPException(status_code=404, detail="Hierarchy not found.")

    # TBD: potentially make parent_id optional:
    # in case a child gets deleted and all parent-child relations to all parents need to be deleted
    async def delete(
        self,
        current_user: CurrentUserData,
        parent_id: Optional[UUID] = None,
        child_id: Optional[UUID] = None,
    ) -> int:
        """Deletes a parent-child relationship."""
        if parent_id is None and child_id is None:
            logger.error("Error in deleting hierarchy:")
            raise HTTPException(
                status_code=422,
                detail="At least one of parent_id and child_id are required.",
            )
        try:
            model_alias = aliased(self.model)
            subquery = select(model_alias.child_id).join(
                IdentifierTypeLink,
                IdentifierTypeLink.id == model_alias.child_id,
            )
            if parent_id and child_id:
                subquery = subquery.where(
                    and_(
                        model_alias.parent_id == parent_id,
                        model_alias.child_id == child_id,
                    )
                )
            elif parent_id:
                subquery = subquery.where(model_alias.parent_id == parent_id)
            elif child_id:
                subquery = subquery.where(model_alias.child_id == child_id)
            subquery = self.policy_crud.filters_allowed(
                subquery, Action.own, IdentifierTypeLink, current_user
            )
            statement = delete(self.model)
            if parent_id and child_id:
                statement = statement.where(
                    and_(
                        self.model.child_id.in_(subquery),
                        self.model.parent_id == parent_id,
                    )
                )
            if parent_id:
                statement = statement.where(self.model.parent_id == parent_id)
            if child_id:
                statement = statement.where(self.model.child_id == child_id)

            response = await self.session.exec(statement)
            await self.session.commit()

            return response.rowcount
        except Exception as e:
            logger.error(f"Error in deleting hierarchy: {e}")
            raise HTTPException(status_code=404, detail="Hierarchy not found.")


class ResourceHierarchyCRUD(
    BaseHierarchyCRUD[BaseHierarchyCreate, ResourceHierarchy, ResourceHierarchyRead]
):
    """CRUD for resource hierarchies."""

    def __init__(self):
        super().__init__(ResourceHierarchy, ResourceHierarchy)

    async def create(
        self,
        current_user: CurrentUserData,
        parent_id: UUID,
        child_type: ResourceType,
        child_id: UUID,
        inherit: Optional[bool] = False,
    ) -> ResourceHierarchy:
        """Creates a new resource hierarchy."""
        hierarchy = await super().create(
            current_user, parent_id, child_type, child_id, inherit
        )

        # Add order to the hierarchy:

        # Get the next order value
        result = await self.session.exec(
            select(func.max(ResourceHierarchy.order)).where(
                ResourceHierarchy.parent_id == parent_id
            )
        )
        max_order = result.one_or_none()
        next_order = (max_order or 0) + 1

        # Update the hierarchy with the order value:
        hierarchy.order = next_order
        await self.session.commit()
        await self.session.refresh(hierarchy)

        return hierarchy

    async def reorder_children(  # noqa: C901
        self,
        current_user: CurrentUserData,
        parent_id: UUID,
        child_id: UUID,
        position: str,
        other_child_id: Optional[UUID] = None,
    ) -> None:
        """Reorders the children of a parent resource."""
        try:
            # Ensure user has write permissions on parent resource:
            parent_access_request = AccessRequest(
                resource_id=parent_id,
                action=Action.write,
                current_user=current_user,
            )
            if not await self.policy_crud.allows(parent_access_request):
                raise HTTPException(status_code=403, detail="Forbidden.")

            # Fetch the children of the parent resource
            child_access_request = AccessRequest(
                resource_id=child_id,
                action=Action.write,
                current_user=current_user,
            )
            if not await self.policy_crud.allows(child_access_request):
                raise HTTPException(status_code=403, detail="Forbidden.")

            if other_child_id:
                other_child_access_request = AccessRequest(
                    resource_id=other_child_id,
                    action=Action.write,
                    current_user=current_user,
                )
                if not await self.policy_crud.allows(other_child_access_request):
                    raise HTTPException(status_code=403, detail="Forbidden.")

            # Get all children of the parent resource - no matter the access rights:
            statement = select(self.model)
            statement = statement.where(self.model.parent_id == parent_id)
            statement = statement.order_by(self.model.order)
            children = await self.session.exec(statement)
            children = children.all()

            # Find the old and new positions of the child
            old_position = None
            moving_child = None
            new_position = None
            for child in children:
                if child.child_id == child_id:
                    old_position = child.order
                    moving_child = child
                if other_child_id and child.child_id == other_child_id:
                    if position == "before":
                        new_position = child.order - 1
                    elif position == "after":
                        new_position = child.order

            if old_position < new_position:
                moving_child.order = new_position
                for i in range(old_position, new_position):
                    children[i].order = i
            else:
                moving_child.order = new_position + 1
                for i in range(new_position, old_position - 1):
                    children[i].order += 1

            # Update the database
            await self.session.commit()

        except Exception as err:
            logger.error(f"Error in reordering children: {err}")
            raise HTTPException(status_code=403, detail="Forbidden.")


class IdentityHierarchyCRUD(
    BaseHierarchyCRUD[BaseHierarchyCreate, IdentityHierarchy, IdentityHierarchyRead]
):
    """CRUD for resource hierarchies."""

    def __init__(self):
        super().__init__(IdentityHierarchy, IdentityHierarchy)
