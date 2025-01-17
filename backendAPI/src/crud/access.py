import logging
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import aliased

# from sqlalchemy import union_all
from sqlmodel import SQLModel, and_, delete, or_, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import (  # BaseHierarchy,; IdentityHierarchy,; ResourceHierarchy,
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
    IdentifierTypeLink,
    IdentityHierarchy,
    IdentityHierarchyCreate,
    IdentityHierarchyRead,
    ResourceHierarchy,
    ResourceHierarchyCreate,
    ResourceHierarchyRead,
)

# from core.access import AccessControl


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
        # ResourceHierarchyAlias = aliased(ResourceHierarchyTable)
        ResourceHierarchyAlias = aliased(ResourceHierarchy)

        hierarchy_cte = (
            # select(ResourceHierarchyTable.child_id.label("resource_id"))
            # .where(ResourceHierarchyTable.child_id.in_(base_resource_ids))
            # .cte(name="resource_hierarchy", recursive=True)
            #
            # select(ResourceHierarchyTable.parent_id.label("resource_id"))
            # .where(ResourceHierarchyTable.parent_id.in_(base_resource_ids))
            # .cte(recursive=True)
            select(ResourceHierarchy.parent_id.label("resource_id"))
            .where(ResourceHierarchy.parent_id.in_(base_resource_ids))
            .cte(recursive=True)
        )

        hierarchy_cte = hierarchy_cte.union_all(
            # select(ResourceHierarchyAlias.parent_id.label("resource_id")).where(
            #     ResourceHierarchyAlias.child_id == hierarchy_cte.c.resource_id,
            select(ResourceHierarchyAlias.child_id.label("resource_id")).where(
                ResourceHierarchyAlias.parent_id == hierarchy_cte.c.resource_id,
                ResourceHierarchyAlias.inherit.is_(True),
            ),
            # base_resource_ids,
        )

        # # Include the base_resource_ids in the result
        # final_query = select(base_resource_ids).union_all(select(hierarchy_cte))

        # return final_query

        return hierarchy_cte

    # TBD: change back into double underscore __:
    def __get_identity_inheritance_common_table_expression(
        self, base_identity_id: UUID
    ):
        """Checks if the resource inherits permissions from a parent resource"""
        # IdentityHierarchyAlias = aliased(IdentityHierarchyTable)
        IdentityHierarchyAlias = aliased(IdentityHierarchy)

        hierarchy_cte = (
            # select(IdentityHierarchyTable.child_id.label("identity_id"))
            # .where(IdentityHierarchyTable.child_id == base_identity_id)
            # .cte(recursive=True)
            select(IdentityHierarchy.child_id.label("identity_id"))
            .where(IdentityHierarchy.child_id == base_identity_id)
            .cte(recursive=True)
            # .cte(name="identity_hierarchy", recursive=True)
        )

        hierarchy_cte = hierarchy_cte.union_all(
            select(IdentityHierarchyAlias.parent_id.label("identity_id")).where(
                IdentityHierarchyAlias.child_id == hierarchy_cte.c.identity_id,
                IdentityHierarchyAlias.inherit.is_(True),
            ),
            # select(literal(base_identity_id).label("identity_id")),
        )

        # Include the base_identity_id in the result
        # final_query = select(literal(base_identity_id).label("identity_id")).union_all(
        #     hierarchy_cte
        # )
        # final_query = hierarchy_cte.union_all(
        #     select(literal(base_identity_id).label("identity_id"))
        # )

        # return final_query

        # print(
        #     "=== AccessPolicyCRUD.__get_identity_inheritance_common_table_expression - final_query ==="
        # )
        # print(hierarchy_cte.compile())
        # print(hierarchy_cte.compile().params)

        # Include the base_identity_id in the result
        # base_identity_id_select = select(literal(base_identity_id).label("identity_id"))
        # final_query = base_identity_id_select.union_all(hierarchy_cte)

        # print(
        #     "=== AccessPolicyCRUD.__get_identity_inheritance_common_table_expression - final_query ==="
        # )
        # print(final_query.compile())
        # print(final_query.compile().params)

        # return final_query

        return hierarchy_cte

    def __always_allow(
        self,
        policy: AccessPolicyCreate,
        current_user: CurrentUserData,
    ):
        # print("=== AccessPolicyCRUD.__always_allow - policy ===")
        # print(policy)
        # print("=== AccessPolicyCRUD.__always_allow - current_user ===")
        # print(current_user)
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
        # - find all resources of the given type and action that the user has permission to access through resource inheritance
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance)
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access and admin override

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
            # TBD: for consistency this could be refactored into a subquery;
            # but there might be slight performance advantages in using a join instead.
            # can public resources inherit permissions? => yes!
            # DEFINITELY NEEDS to be refactored into subquery!!!
            ###### old #######
            # if model != AccessPolicy:
            #     statement = statement.join(
            #         AccessPolicy, model.id == AccessPolicy.resource_id
            #     )
            #     statement = statement.where(AccessPolicy.resource_id == model.id)
            # statement = statement.where(AccessPolicy.action.in_(action))
            # statement = statement.where(AccessPolicy.public)
            #################
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
            # for resource hierarchy:
            # get all parent resource id's, that the resource inherits from
            #
            # change the current_user.user_id to be
            # current_user.user_id AND parent identity id's for all parents, that the identity inherits from
            # subquery = (
            #     select(AccessPolicy.resource_id)
            #     .where(AccessPolicy.action.in_(action))
            #     .where(
            #         or_(
            #             AccessPolicy.identity_id == current_user.user_id,
            #             AccessPolicy.public,
            #         )
            #     )
            # )

            ####### refactor into this #######
            #
            # move this into a function, that takes the current_user
            # and returns the resource_hierarchy_cte
            # make sure to include the base_resource_ids in the result!
            # __get_accessible_resource_ids(action, current_user) -> cte
            #
            # Create the common table expression (CTE) for the identity hierarchy
            identity_hierarchy_cte = (
                self.__get_identity_inheritance_common_table_expression(
                    current_user.user_id
                )
            )  # omit this line if no current_user (for public resources)

            # Base resources for access check
            base_resource_ids = select(AccessPolicy.resource_id).where(
                AccessPolicy.action.in_(action),
                or_(
                    # TBD: add in later:
                    AccessPolicy.identity_id.in_(
                        select(identity_hierarchy_cte.c.identity_id)
                    ),  # omit the or_ and this line if no current_user (for public resources)
                    AccessPolicy.identity_id == current_user.user_id,
                    AccessPolicy.public,
                ),
            )
            # print("=== AccessPolicyCRUD.filters_allowed - base_resource_ids ===")
            # print(base_resource_ids.compile())
            # print(base_resource_ids.compile().params)

            # Create the common table expression (CTE) for the resource hierarchy
            resource_hierarchy_cte = (
                self.__get_resource_inheritance_common_table_expression(
                    base_resource_ids
                )
            )

            # print("=== AccessPolicyCRUD.filters_allowed - resource_hierarchy_cte ===")
            # print(resource_hierarchy_cte.compile())

            # Subquery to get accessible resource IDs including inherited access
            # This filters again only the resources, that the user has direct access to - not what I want here!
            # Is the following redundant now?
            # subquery = select(AccessPolicy.resource_id).where(
            #     AccessPolicy.action.in_(action),
            #     or_(
            #         # TBD: add in later
            #         AccessPolicy.identity_id.in_(
            #             select(identity_hierarchy_cte.c.identity_id)
            #         ),  # omit the or_ and this line if no current_user (for public resources)
            #         AccessPolicy.identity_id == current_user.user_id,
            #         AccessPolicy.public,
            #     ),
            #     or_(
            #         AccessPolicy.resource_id.in_(
            #             select(resource_hierarchy_cte.c.resource_id)
            #         ),
            #         AccessPolicy.resource_id.in_(base_resource_ids),
            #     ),
            # )

            # print("=== AccessPolicyCRUD.filters_allowed - subquery ===")
            # print(subquery.compile())
            # print(subquery.compile().params)

            #######################

        # print("=== AccessPolicyCRUD.filters_allowed - subquery ===")
        # print(subquery.compile())
        # print(subquery.compile().params)
        # print("\n")

        # if subquery:
        # if (model == AccessPolicy) or (model == AccessLog):
        #     statement = statement.where(model.resource_id.in_(subquery))
        # else:
        #     statement = statement.where(model.id.in_(subquery))

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

        # print("=== AccessPolicyCRUD.filters_allowed - statement ===")
        # print(statement.compile())
        # print(statement.compile().params)
        # print("\n")

        return statement

        ############################################################
        # OK - this could be a good start - from ChatGPT4o:
        # from sqlalchemy import select, or_, union_all
        # from sqlalchemy.orm import aliased
        # from sqlmodel import Session, SQLModel, Field
        # from typing import List
        # import uuid

        # class AccessPolicy(SQLModel, table=True):
        #     resource_id: uuid.UUID = Field(primary_key=True)
        #     action: str
        #     identity_id: uuid.UUID
        #     public: bool

        # class ResourceHierarchy(SQLModel, table=True):
        #     parent_id: uuid.UUID
        #     child_id: uuid.UUID
        #     inherit: bool

        # class IdentityHierarchy(SQLModel, table=True):
        #     parent_id: uuid.UUID
        #     child_id: uuid.UUID
        #     inherit: bool

        # def get_resource_hierarchy_cte(base_resource_ids: List[uuid.UUID]):
        #     ResourceHierarchyAlias = aliased(ResourceHierarchy)

        #     # Start with the base resources
        #     # Hmmm, looks to get all the fist parents of the base resources
        #     base_resources = select(ResourceHierarchy.parent_id).where(
        #         ResourceHierarchy.child_id.in_(base_resource_ids),
        #         ResourceHierarchy.inherit.is_(True)
        #     )

        #     # Recursive CTE to find all parent resources that inherit access
        #     hierarchy_cte = (
        #         select(
        #             ResourceHierarchy.child_id.label('resource_id')
        #         )
        #         .where(ResourceHierarchy.child_id.in_(base_resource_ids))
        #         .cte(name='resource_hierarchy', recursive=True)
        #     )

        #     hierarchy_cte = hierarchy_cte.union_all(
        #         select(
        #             ResourceHierarchyAlias.parent_id.label('resource_id')
        #         ).where(
        #             ResourceHierarchyAlias.child_id == hierarchy_cte.c.resource_id,
        #             ResourceHierarchyAlias.inherit.is_(True)
        #         )
        #     )

        #     return hierarchy_cte

        # def get_identity_hierarchy_cte(base_identity_id: uuid.UUID):
        #     IdentityHierarchyAlias = aliased(IdentityHierarchy)

        #     hierarchy_cte = (
        #         select(
        #             IdentityHierarchy.child_id.label('identity_id')
        #         )
        #         .where(IdentityHierarchy.child_id == base_identity_id)
        #         .cte(name='identity_hierarchy', recursive=True)
        #     )

        #     hierarchy_cte = hierarchy_cte.union_all(
        #         select(
        #             IdentityHierarchyAlias.parent_id.label('identity_id')
        #         ).where(
        #             IdentityHierarchyAlias.child_id == hierarchy_cte.c.identity_id,
        #             IdentityHierarchyAlias.inherit.is_(True)
        #         )
        #     )

        #     return hierarchy_cte

        # # corresponds to existing filters_allowed function:
        # def get_accessible_resource_ids(action: List[str], current_user, session: Session):
        #     # Base identity id is the current user id
        #     base_identity_id = current_user.user_id

        #     # Create the CTE for the identity hierarchy
        #     identity_hierarchy_cte = get_identity_hierarchy_cte(base_identity_id)

        #     # Base resources for access check
        #     base_resource_ids = select(AccessPolicy.resource_id).where(
        #         AccessPolicy.action.in_(action),
        #         or_(
        #             AccessPolicy.identity_id.in_(select(identity_hierarchy_cte.c.identity_id)),
        #             AccessPolicy.public
        #         )
        #     )

        #     # Create the CTE for the resource hierarchy
        #     resource_hierarchy_cte = get_resource_hierarchy_cte(base_resource_ids)

        #     # Subquery to get accessible resource IDs including inherited access
        #     subquery = (
        #         select(AccessPolicy.resource_id)
        #         .where(
        #             AccessPolicy.action.in_(action),
        #             or_(
        #                 AccessPolicy.identity_id.in_(select(identity_hierarchy_cte.c.identity_id)),
        #                 AccessPolicy.public,
        #             ),
        #             AccessPolicy.resource_id.in_(select(hierarchy_cte.c.resource_id))
        #         )
        #     )

        #     return subquery

        # def get_statement(action: List[str], current_user, session: Session):
        #     subquery = get_accessible_resource_ids(action, current_user, session)

        #     statement = select(model).where(model.id.in_(subquery))
        #     return statement

        # Example usage
        # session = Session(engine)
        # result = session.execute(get_statement(action, current_user, session)).all()

        ############################################################

        # ###### Refactor this into a subquery and filter the results for the  the main query statement #####
        # # this is becoming two different functions - one for resources and one for policies
        # # consider splitting this into two functions
        # if model == AccessPolicy:
        #     subquery = select(AccessPolicy.resource_id).where(
        #         and_(
        #             AccessPolicy.identity_id == current_user.user_id,
        #             AccessPolicy.action
        #             == own,  # why is the AccessPolicy retrieval limited to owners only here - this should be done in the AccessPolicyCRUD (create, read, update, delete methods!)
        #         )
        #     )
        #     statement = statement.filter(AccessPolicy.resource_id.in_(subquery))
        # elif model == AccessLog:
        #     subquery = select(AccessPolicy.resource_id)
        #     subquery = subquery.where(AccessPolicy.action.in_(action))
        #     subquery = subquery.where(
        #         or_(
        #             AccessPolicy.identity_id == current_user.user_id,
        #             AccessPolicy.public,
        #         )
        #     )
        #     #     .where(
        #     #     and_(
        #     #         AccessPolicy.identity_id == current_user.user_id,
        #     #         AccessPolicy.action == own,
        #     #     )
        #     # )
        #     # print("=== AccessPolicyCRUD.filters_allowed - subquery ===")
        #     # print(subquery.compile())
        #     # print(subquery.compile().params)

        #     # return subquery

        #     # subquery_results = self.session.exec(subquery)
        #     # subquery_results = subquery_results.all()

        #     # print("=== AccessPolicyCRUD.filters_allowed - subquery_results ===")
        #     # for result in subquery_results:
        #     #     pprint(result)

        #     statement = statement.filter(AccessLog.resource_id.in_(subquery))
        #     # statement = statement.join(
        #     #     AccessPolicy, AccessLog.resource_id == AccessPolicy.resource_id
        #     # )
        #     # statement = statement.where(
        #     #     AccessPolicy.resource_id == AccessLog.resource_id
        #     # )
        #     # statement = statement.where(AccessPolicy.action.in_(action))
        #     # statement = statement.where(
        #     #     or_(
        #     #         AccessPolicy.identity_id == current_user.user_id,
        #     #         AccessPolicy.public,
        #     #     )
        #     # )
        # else:
        #     statement = statement.join(
        #         AccessPolicy, model.id == AccessPolicy.resource_id
        #     )
        #     statement = statement.where(AccessPolicy.resource_id == model.id)
        #     statement = statement.where(AccessPolicy.action.in_(action))
        #     statement = statement.where(
        #         or_(
        #             AccessPolicy.identity_id == current_user.user_id,
        #             AccessPolicy.public,
        #         )
        #     )
        # #################################

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

            async with self:
                # print("=== AccessPolicyCRUD.allows - query ===")
                # print(query.compile())
                # print(query.compile().params)

                # Only one policy per resource - action - identity combination is allowed!
                response = await self.session.exec(query)
                results = response.all()

            for result in results:
                if result.resource_id == resource_id:
                    return True
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=403, detail="Forbidden.")

        return False

    async def check_access(
        self,
        current_user: CurrentUserData,
        resource_id: UUID,
    ) -> AccessPermission:
        """Checks the access level of the user to the resource."""
        # print("=== check_access - current_user ===")
        # print(current_user)
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

            # Reading the access policies for the resource from database
            # - not working, finds access policies from other users as well!:
            # query = select(AccessPolicy)
            # query = query.where(AccessPolicy.resource_id == resource_id)
            # query_own = self.filters_allowed(
            #     query, own, current_user=current_user
            # ).subquery()
            # query_write = self.filters_allowed(
            #     query, write, current_user=current_user
            # ).subquery()
            # query_read = self.filters_allowed(
            #     query, read, current_user=current_user
            # ).subquery()

            # combined_query = union_all(
            #     select(query_own), select(query_write), select(query_read)
            # )

            # async with self:
            #     # response = await self.session.exec(query)
            #     response = await self.session.exec(combined_query)
            #     results = response.all()

            # print("=== AccessPolicyCRUD.check_access - results ===")
            # print(results)

            # access_level = None
            # if results:
            #     for result in results:
            #         print("=== AccessPolicyCRUD.check_access - result ===")
            #         print(result)
            #         # TBD: should not be necessary to check for the resource_id again here!
            #         # The query is doing this already!
            #         if result.resource_id == resource_id:
            #             print("=== AccessPolicyCRUD.check_access - result ===")
            #             print(result)
            #             if result.action == own:
            #                 return AccessPermission(
            #                     resource_id=resource_id,
            #                     action=own,
            #                 )  # can be returned directly, as it's the highest access level
            #             elif result.action == write:
            #                 print(
            #                     "=== AccessPolicyCRUD.check_access - write triggered ==="
            #                 )
            #                 access_level = write
            #             elif result.action == read and access_level != write:
            #                 print(
            #                     "=== AccessPolicyCRUD.check_access - read triggered ==="
            #                 )
            #                 access_level = read
            # print("=== AccessPolicyCRUD.check_access - access_level ===")
            # print(access_level)
            # return AccessPermission(
            #     resource_id=resource_id,
            #     action=access_level,
            # )
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=403, detail="Forbidden.")

    async def create(
        self,
        policy: AccessPolicyCreate,
        current_user: CurrentUserData,
        allow_override: bool = False,
        *args,
    ) -> AccessPolicyRead:
        """Creates a new access control policy."""
        # Note: the current_user is the one who creates the policy for the identity_id in the policy!
        try:
            # TBD: remove this, as it's already done through typing the arguments of the method?
            policy = AccessPolicy.model_validate(policy)
            # policy = AccessPolicy(**policy.model_dump())

            # TBD: add access control checks here:
            # only owners of parent resources and Admins can create policies
            # current_user = CurrentUserData(
            #     user_id=policy.identity_id,
            #     # how do i get the roles and groups here?
            # )

            # Every user can create a policy for themselves:
            # Really? That means everyone can give itself owner rights -
            # just because they know their own identity_id and the resource_id?
            # TBD: the following if check - should go out!
            # current_user needs to the be the owner of the resource
            # to create a new policy for it - or admin. Inheritance is handled inside the allows method.

            # Current user creates a policy for another identity.
            # Current user needs to own the resource to grant others access (share) it.
            # inheritance is handled inside the allows method.
            # if not await self.allows(
            #     current_user=current_user,
            #     resource_id=policy.resource_id,
            #     action=own,
            # ):
            #     raise HTTPException(status_code=403, detail="Forbidden.")

            # Hmmm - How could there ever get a policy created for a newly created resource?
            # Does this only come to life after hierarchies are implemented?
            # Yes - should definitely check if user has write access on the parent resource!
            # All endpoints that utilize the inheritance should then call the
            # create_as_child(object, parent) -> where the parent access gets checked.
            # Furthermore the instantiation of BaseCRUD needs
            # to get all possible parent models as List[SQLModel]

            # TBD: refactor into using filters_allowed method!
            # print("=== AccessPolicyCRUD.create - policy ===")
            # print(policy)
            # print("=== AccessPolicyCRUD.create - current_user ===")
            # print(current_user)

            # print("=== AccessPolicyCRUD.create - policy ===")
            # print(policy)
            # print("=== AccessPolicyCRUD.create - current_user ===")
            # print(current_user)

            # print("=== AccessPolicyCRUD.create - allow_standalone ===")
            # print(allow_standalone)
            # print(
            #     "=== AccessPolicyCRUD.create - self.__always_allow(policy, current_user) ==="
            # )
            # print(self.__always_allow(policy, current_user))

            if allow_override or self.__always_allow(policy, current_user):
                # print("=== access check skipped ===")
                pass
            else:
                # print("=== access check not skipped ===")
                # if not self.__always_allow(policy, current_user):
                try:
                    await self.read(
                        current_user=current_user,
                        resource_id=policy.resource_id,
                        action=own,
                        # public=policy.public,  # This does not make sense - the policy does not need to be public if set to true!
                    )
                    # print("=== AccessPolicyCRUD.create - response ===")
                    # print(response)
                except Exception as e:
                    logger.error(f"Error in reading policy: {e}")
                    raise HTTPException(
                        status_code=404, detail="Access policy not found."
                    )

            # if not response:
            #     raise HTTPException(
            #         status_code=404, detail="Access policy not found."
            #     )
            # query.session = self.filters_allowed(query.session, own, current_user=current_user)
            # access_request = AccessRequest(
            #     resource_id=policy.resource_id,
            #     action=own,
            #     current_user=current_user,
            # )
            # await self.allows(access_request)

            # if not await self.allows(access_request):
            # except Exception as e:
            #     logger.error(f"Error in creating policy: {e}")
            #     raise HTTPException(status_code=403, detail="Forbidden.")

            # print("=== AccessPolicyCRUD.create - policy ===")
            # print(policy)

            # Works:
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
        # Or what resources haas another user with identity_id access to?
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
            # feels dangerous to have resource_id and action to be optional
            # but might be the right thing to do!

            # access_request = AccessRequest(
            #     resource_id=resource_id,
            #     action=own,
            #     current_user=current_user,
            # )
            # await self.allows(access_request)

            # query = select(AccessPolicy)

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

            # print("=== AccessPolicyCRUD.read - query ===")
            # print(query.compile())
            # print(query.compile().params)

            response = await self.session.exec(query)
            results = response.all()

            # print("=== AccessPolicyCRUD.read - results ===")
            # print(results)

            if not results:
                raise HTTPException(status_code=404, detail="Access policy not found.")

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

    # similar to update - but deletes old and creates a new policy
    async def change(
        self,
        current_user: Optional["CurrentUserData"],
        access_policy: AccessPolicyUpdate,
    ) -> AccessPolicyRead:
        """Updates an access control policy."""
        # reuses delete and create methods

        try:
            # TBD: should the attribute public be a part of the update?
            # => yes, needs to, because it's a mandatory part of the AccessPolicyCreate,
            # which AccessPolicyUpdate inherits from!
            # TBD: add business logic: can last owner delete it's owner rights?
            # => yes, but only if there is another owner left - should be handled in delete!
            # TBD: what about downgrading from own to write or read? Permission inheritance?
            old_policy = AccessPolicy(
                resource_id=access_policy.resource_id,
                identity_id=access_policy.identity_id,
                action=access_policy.action,
                public=access_policy.public,
            )
            await self.delete(current_user, old_policy)
            new_policy = AccessPolicyCreate(
                resource_id=access_policy.resource_id,
                identity_id=access_policy.identity_id,
                action=access_policy.new_action,
                public=access_policy.public,
            )
            # print("=== AccessPolicyCRUD.change - new_policy ===")
            # pprint(new_policy)
            return await self.create(new_policy, current_user)

        except Exception as e:
            logger.error(f"Error in updating policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found.")

    # TBD: enable delete all policies for a resource / for an identity
    async def delete(
        self,
        current_user: Optional["CurrentUserData"],
        access_policy: AccessPolicyDelete,
        # resource_id: Optional[UUID] = None,
        # identity_id: Optional[UUID] = None,
        # action: Optional[Action] = None,
        # public: Optional[bool] = None,
    ) -> None:
        """Deletes an access control policy."""

        # To delete a policy, current user needs to be owner of the resource or Admin!

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

            # print("=== AccessPolicyCRUD.delete - statement ===")
            # print(statement.compile())
            # print(statement.compile().params)

            response = await self.session.exec(statement)
            # await self.session.exec(statement)
            # print("=== AccessPolicyCRUD.delete - response ===")
            # pprint(response.rowcount)
            await self.session.commit()
            # results = response.all()
            # print("=== AccessPolicyCRUD.delete - results ===")
            # pprint(results)
            if response.rowcount == 0:
                # print("no policy to delete")
                raise HTTPException(status_code=404, detail="Access policy not found.")
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

    # def add_log_to_session(
    #     self,
    #     access_log: AccessLogCreate,
    #     session: AsyncSession,
    # ) -> AsyncSession:
    #     """Adds creation of access log to existing session."""
    #     try:
    #         access_log = AccessLog.model_validate(access_log)
    #         session.add(access_log)
    #         return session
    #     except Exception as e:
    #         logger.error(f"Error in adding log to session: {e}")
    #         raise HTTPException(status_code=400, detail="Bad request: logging failed.")

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

    # async def log_access(
    #     self,
    #     access_log: AccessLogCreate,
    # ) -> AccessLog:
    #     """Logs an access attempt to the database."""
    #     logger.info("Writing an access log to the database.")
    #     access_log = AccessLog.model_validate(access_log)
    #     # TBD: add access control checks here:
    #     # request is known from self.current_user, object and method is write here
    #     # No - this is logging - no need for access control here!
    #     try:
    #         session = self.session
    #         session.add(access_log)
    #         await session.commit()
    #         await session.refresh(access_log)
    #         return access_log
    #     except Exception as e:
    #         logger.error(f"Error in logging: {e}")
    #         raise HTTPException(status_code=400, detail="Bad request: logging failed")

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

            # print("=== AccessLoggingCRUD.read - statement ===")
            # print(statement.compile())
            # print(statement.compile().params)

            response = await session.exec(statement)
            results = response.all()

            # print("=== AccessLoggingCRUD.read - results ===")
            # pprint(results)

            if not results:
                raise HTTPException(status_code=404, detail="Access logs not found.")

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
        current_user: CurrentUserData,
        resource_id: UUID,
    ):
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
        current_user: CurrentUserData,
        resource_id: UUID,
        action: Action = Action.own,
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

    async def read_resource_access_count(
        self,
        current_user: CurrentUserData,
        resource_id: UUID,
    ):
        """Reads the number of access logs for a resource id."""
        try:
            access_count = await self.read(
                current_user, resource_id, required_action=Action.read, status_code=None
            )
            return len(access_count)
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access logs not found.")

    # # Do we need current_user here?
    # # TBD: create a generic read method and use it here.
    # # TBD implement crud tests for this?
    # async def read_log_by_identity_id(self, identity_id: UUID) -> list[AccessLogRead]:
    #     """Reads access logs by identity id."""
    #     logger.info("Reading identity access logs from the database.")
    #     try:
    #         session = self.session
    #         query = select(AccessLog).where(
    #             AccessLog.identity_id == identity_id,
    #         )
    #         response = await session.exec(query)
    #         results = response.all()
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading log: {e}")
    #         raise HTTPException(status_code=404, detail="Log not found")

    # # Do we need current_user here?
    # # TBD: create a generic read method and use it here.
    # # TBD: implement more crud tests for this?
    # async def read_log_by_resource_id(
    #     self, resource_id: UUID  # ,   resource_type: ResourceType
    # ) -> list[AccessLogRead]:
    #     """Reads access logs by resource id and type."""
    #     logger.info("Reading resource access logs from the database.")
    #     try:
    #         session = self.session
    #         query = select(AccessLog).where(
    #             AccessLog.resource_id == resource_id,
    #         )
    #         response = await session.exec(query)
    #         results = response.all()
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading log: {e}")
    #         raise HTTPException(status_code=404, detail="Log not found")

    # # TBD: create a generic read method and use it here.
    # async def read_log_created(self, resource_id: UUID) -> AccessLogRead:
    #     """Reads first access log with action "Own" for resource id and type - corresponds to create."""
    #     logger.info("Reading create information from access logs in database.")
    #     try:
    #         session = self.session
    #         query = (
    #             select(AccessLog)
    #             .where(
    #                 AccessLog.resource_id == resource_id,
    #             )
    #             .order_by(AccessLog.time)
    #             .limit(1)
    #         )
    #         response = await session.exec(query)
    #         result = response.one()
    #         return result
    #     except Exception as e:
    #         logger.error(f"Error in reading log: {e}")
    #         raise HTTPException(status_code=404, detail="Log not found")


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
            # print("=== BaseHierarchyCRUD.create - parent_id ===")
            # print(parent_id)

            # query = select(IdentifierTypeLink)
            # results = await self.session.exec(query)
            # print("=== BaseHierarchyCRUD.create - results ===")
            # print(results.all())

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

            # print("=== BaseHierarchyCRUD.create - statement ===")
            # print(statement.compile())
            # print(statement.compile().params)

            result = await self.session.exec(statement)

            # print("=== BaseHierarchyCRUD.create - result ===")
            # print(result.all())

            parent_type = result.one()

            # print("=== BaseHierarchyCRUD.create - parent_type ===")
            # print(parent_type)

            # print("=== BaseHierarchyCRUD.create - child_type ===")
            # print(child_type)

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
            # TBD: is a condition required id only parent_id or child_id is provided?
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

            # print("=== BaseHierarchyCRUD.read_children - results ===")
            # pprint(results)

            if not results:
                raise HTTPException(status_code=404, detail="No children found.")

            return results
        except Exception as err:
            logger.error(f"Error in reading hierarchy: {err}")
            raise HTTPException(status_code=404, detail="Hierarchy not found.")

    # TBD: potentially make parent_id optional:
    # in case a child gets deleted and all parent-child relations to all parents need to be deleted
    async def delete(
        self,
        parent_id: UUID,
        child_id: UUID,
        current_user: CurrentUserData,
    ) -> None:
        """Deletes a parent-child relationship."""
        try:
            model_alias = aliased(self.model)
            subquery = (
                select(model_alias.child_id)
                .where(
                    and_(
                        model_alias.parent_id == parent_id,
                        model_alias.child_id == child_id,
                    )
                )
                .join(
                    IdentifierTypeLink,
                    IdentifierTypeLink.id == model_alias.child_id,
                )
            )
            subquery = self.policy_crud.filters_allowed(
                subquery, Action.own, IdentifierTypeLink, current_user
            )
            statement = delete(self.model).where(
                and_(
                    self.model.child_id.in_(subquery),
                    self.model.parent_id == parent_id,
                )
            )
            # statement = (
            #     delete(self.model)
            #     .where(
            #         and_(
            #             self.model.parent_id == parent_id,
            #             self.model.child_id == child_id,
            #         )
            #     )
            #     .join(
            #         IdentifierTypeLink,
            #         IdentifierTypeLink.id == self.model.child_id,
            #     )
            # )
            # statement = self.policy_crud.filters_allowed(
            #     statement, Action.own, IdentifierTypeLink, current_user
            # )

            # print("=== BaseHierarchyCRUD.read_children - statement ===")
            # print(statement.compile())
            # pprint(statement.compile().params)

            response = await self.session.exec(statement)
            await self.session.commit()
            if response.rowcount == 0:
                raise HTTPException(status_code=404, detail="Hierarchy not found.")
        except Exception as e:
            logger.error(f"Error in deleting hierarchy: {e}")
            raise HTTPException(status_code=404, detail="Hierarchy not found.")


class ResourceHierarchyCRUD(
    BaseHierarchyCRUD[ResourceHierarchyCreate, ResourceHierarchy, ResourceHierarchyRead]
):
    """CRUD for resource hierarchies."""

    def __init__(self):
        # super().__init__(ResourceHierarchy, ResourceHierarchyTable)
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
            # print("=== other_child_id ===")
            # print(other_child_id)

            # Ensure user has write permissions on parent resource:
            parent_access_request = AccessRequest(
                resource_id=parent_id,
                action=Action.write,
                current_user=current_user,
            )
            if not await self.policy_crud.allows(parent_access_request):
                raise HTTPException(status_code=403, detail="Forbidden.")
            # Alternative - same as above in create()
            # TBD: decide which one to use and consider replacing the above with this one!
            # it's anyways making another round trip to the database!
            # statement = select(IdentifierTypeLink.type)
            # statement = self.policy_crud.filters_allowed(
            #     statement, Action.write, IdentifierTypeLink, current_user
            # )
            # statement = statement.where(IdentifierTypeLink.id == parent_id)

            # result = await self.session.exec(statement)
            # parent_type = result.one()

            # parent_model = ResourceType.get_model(parent_type)

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
    BaseHierarchyCRUD[IdentityHierarchyCreate, IdentityHierarchy, IdentityHierarchyRead]
):
    """CRUD for resource hierarchies."""

    def __init__(self):
        super().__init__(IdentityHierarchy, IdentityHierarchy)
