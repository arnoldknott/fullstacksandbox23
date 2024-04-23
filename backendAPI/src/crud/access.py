import logging
from uuid import UUID

from pprint import pprint

from typing import List, Optional
from sqlmodel import select, delete, or_, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import CurrentUserData, Action

# from core.access import AccessControl

from fastapi import HTTPException
from models.access import (
    AccessPolicyCreate,
    AccessPolicy,
    AccessPolicyRead,
    AccessRequest,
    AccessLogCreate,
    AccessLog,
    AccessLogRead,
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
        # self.access_control = AccessControl(self)

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def __check_resource_inheritance(self):
        """Checks if the resource inherits permissions from a parent resource"""
        # TBD: check the inheritance flag in the resource hierarchy table and stop, if not inherited!
        pass

    async def __check_identity_inheritance(self):
        """Checks if the resource inherits permissions from a parent resource"""
        # TBD: check if the identity inherits permissions from a parent identity (aka group)
        pass

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

        # action, current_user, resrouce_id = (
        #     access_request.action,
        #     access_request.current_user,
        #     access_request.resource_id,
        # )

        # print("=== core.access - AccessCRUD - filters_allowed - action ===")
        # pprint(action)

        # Permission overrides:
        # own includes write and read
        # write includes read
        if action == read:
            action = ["own", "write", "read"]
        elif action == write:
            action = ["own", "write"]
        elif action == own:
            action = ["own"]
        else:
            # TBD: write test for this: if pydantic works on varying action types,
            # a 422 or type error should be raised before this line!
            logger.error("Invalid action provided.")
            raise HTTPException(status_code=400, detail="Bad request: invalid action.")

        # print("=== core.access - AccessCRUD - filters_allowed - model ===")
        # print(model)
        # print("=== core.access - AccessCRUD - filters_allowed - current_user ===")
        # pprint(current_user)
        # print("=== core.access - AccessCRUD - filters_allowed - statement ===")
        # pprint(statement.compile())
        # pprint(statement.compile().params)
        # print("=== core.access - AccessCRUD - filters_allowed - action ===")
        # print(action)

        # print("=== core.access - AccessCRUD - filters_allowed - action ===")
        # print(action)

        # print("=== core.access - AccessControl - filters_allowed - current_user ===")
        # pprint(current_user)

        if not current_user:
            if model != AccessPolicy:
                statement = statement.join(
                    AccessPolicy, model.id == AccessPolicy.resource_id
                )
                statement = statement.where(AccessPolicy.resource_id == model.id)
            statement = statement.where(AccessPolicy.action.in_(action))
            statement = statement.where(AccessPolicy.public)
        elif "Admin" in current_user.roles:
            pass
        else:
            if model != AccessPolicy:
                statement = statement.join(
                    AccessPolicy, model.id == AccessPolicy.resource_id
                )
                statement = statement.where(AccessPolicy.resource_id == model.id)
            statement = statement.where(AccessPolicy.action.in_(action))
            statement = statement.where(
                or_(
                    AccessPolicy.identity_id == current_user.user_id,
                    AccessPolicy.public,
                )
            )

        # print("=== core.access - AccessControl - statement ===")
        # print(statement)

        return statement

    async def allows(
        self,
        # resource_id: UUID,
        # action: "Action",
        # current_user: Optional["CurrentUserData"] = None,
        access_request: AccessRequest,
    ) -> bool:
        """Checks if the user has permission including inheritance to perform the action on the resource"""
        resource_id = access_request.resource_id
        action = access_request.action
        current_user = access_request.current_user

        # TBD: move the logging to the BaseCrud? Or keep it here together with the Access Control?
        # loggingCRUD = AccessLoggingCRUD()
        # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
        # Don't include the identity in the query, as public resources are not assigned to any identity!
        # TBD: implement "public" override: check if the resource is public for requested action and return True if it is!

        # print("=== AccessPolicyCRUD.allows - resource_id ===")
        # pprint(resource_id)

        # print("=== AccessPolicyCRUD.allows - current_user ===")
        # pprint(current_user)

        # Necessary as otherwise an empty database could never get data into it.
        if current_user and current_user.roles and "Admin" in current_user.roles:
            return True

        try:
            query = select(AccessPolicy).where(
                AccessPolicy.resource_id == resource_id,
            )
            if resource_id:
                query = query.where(
                    AccessPolicy.resource_id == resource_id,
                )

            query = self.filters_allowed(query, action, current_user=current_user)
            # query = self.filters_allowed(query, access_request)
            # print("=== AccessPolicyCRUD.allows - query ===")
            # print(query.compile())
            # print(query.compile().params)

            # Only one policy per resource - action - identity combination is allowed!
            response = await self.session.exec(query)
            results = response.one()

            # print("=== AccessPolicyCRUD.allows - results ===")
            # print(results)

            if results.resource_id == resource_id and results.action == action:
                return True
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=403, detail="Forbidden.")

        return False

    async def create(
        self, policy: AccessPolicyCreate, current_user: CurrentUserData
    ) -> AccessPolicyRead:
        """Creates a new access control policy."""
        # Note: the current_user is the one who creates the policy for the identity_id in the policy!
        # print("=== AccessPolicyCRUD.create - current_user ===")
        # pprint(current_user)
        # print("=== AccessPolicyCRUD.create - policy ===")
        # pprint(policy)
        try:
            # session = self.session
            # TBD: remove this, as it's already done through typing the arguments of the method?
            policy = AccessPolicy.model_validate(policy)
            # TBD: add access control checks here:
            # only owners and Admins can create policies
            # current_user = CurrentUserData(
            #     user_id=policy.identity_id,
            #     # how do i get the roles and groups here?
            # )

            # TBD: take Action hierarchy into account:
            # if a user can own, they can also write and read
            # if a user can write, they can also read
            # If a user gets upgraded here - delete the lower level policies?
            # Only have the highest access level in the database?

            # Every user can create a policy for themselves:
            # Really? That means everyone can give itself owner rights -
            # just because they know their own identity_id and the resource_id?
            # TBD: the following if check - should go out!
            # current_user needs to the be the owner of the resource
            # to create a new policy for it - or admin. Inheritance is handled inside the allows method.

            # if policy.identity_id != current_user.user_id:
            # Current user creates a policy for another identity.
            # Current user needs to own the resource to grant others access (share) it.
            # inheritance is handled inside the allows method.
            # if not await self.allows(
            #     current_user=current_user,
            #     resource_id=policy.resource_id,
            #     # resource_type=policy.resource_type,
            #     action=own,
            # ):

            # Hmmm - How could there ever get a policy created for a newly created resource?
            # Does this only come to life after hierarchies are implemented?
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
            # pprint(policy)
            self.session.add(policy)
            await self.session.commit()
            await self.session.refresh(policy)
            # print("=== AccessPolicyCRUD.create - policy ===")
            # print(policy)
            # TBD: write sharing to Access Control Log?
            return policy
        except Exception as e:
            # TBD: write sharing attempt to Access Control Log?
            # access_log = AccessLogCreate(
            #     identity_id=current_user.user_id,
            #     identity_type="User"
            #     resource_id=policy.resource_id if policy.resource_id else None,
            #     resource_type=policy.resource_type if policy.resource_type else None,
            #     action=own,
            #     status_code=403,  # TBD: could be 201 if a new resource is created
            # )
            # await loggingCRUD.log_access(access_log)
            logger.error(f"Error in creating policy: {e}")
            raise HTTPException(status_code=403, detail="Forbidden.")

    async def add_child(
        self,
        policy: AccessPolicyCreate,
        parent_resource_id: int,
        current_user: CurrentUserData,
    ):
        """Adds a child policy to a parent policy."""
        # TBD: make sure, that current_user has owner rights in parent_resource or is Admin
        # put that into the access_control in core.access AccessControl.allows or so?
        # TBD should this be a method of AccessPolicyCRUD or AccessControl?
        pass

    # Isn't this starting to become a bit silly? Reading, what you know already?
    async def read(
        self,
        # Who is requesting the policies?
        # access_request: AccessRequest,
        current_user: Optional["CurrentUserData"] = None,
        # policy_id: Optional[int] = None,
        # What policy is requested? (The identity can be another user!)
        # For example look at who else has access to the resource with resource_id?
        # Or what resources haas another user with identity_id access to?
        # and what actions for the above?
        # access_policy: Optional[AccessPolicy] = None,
        identity_id: Optional[UUID] = None,
        resource_id: Optional[int] = None,
        action: Optional[Action] = None,
        public: Optional[bool] = None,
    ) -> List[AccessPolicyRead]:
        """Reads access control policies based on the provided parameters."""
        # TBD: current_user is the one who reads the policies for the identity_id in the policy!

        # identity_id, resource_id, action, public = (
        #     access_policy.identity_id,
        #     access_policy.resource_id,
        #     access_policy.action,
        #     access_policy.public,
        # )

        # TBD: add some access checks here:
        # if current_user is Admin: allow all.
        # otherwise: identity_id must be either current_user.id or a group the current_user is member of.
        # if no identity id, the resource needs to be public

        try:
            # session = self.session
            query = select(AccessPolicy)

            # print("=== AccessPolicyCRUD.read - current_user ===")
            # pprint(current_user)
            # print("=== AccessPolicyCRUD.read - query ===")
            # print(query)
            # TBD: consider access control checks here:
            # not using the allows - here it's just about building the query to get the policies!

            # TBD: can a method from core - access control be used here?
            # if not current_user:
            #     # The difference to access from core is the missing join here
            #     # otherwise it would be a self join and .resource_id needs to be equal to .id
            #     query = query.where(AccessPolicy.action == own)
            #     query = query.where(AccessPolicy.public)
            # elif "Admin" in current_user.roles:
            #     pass
            # else:
            #     # The difference to access from core is the missing join here
            #     # otherwise it would be a self join and .resource_id needs to be equal to .id
            #     # TBD: write test for this: needs to ensure,
            #     # that only resources get returned, where the current_user is owner or
            #     # the resource is publicly owned
            #     query = query.where(AccessPolicy.action == own)
            #     query = query.where(
            #         or_(
            #             AccessPolicy.identity_id == current_user.user_id,
            #             AccessPolicy.public,
            #         )
            #     )

            # TBD: consider moving validation to the parameters of the method?
            # current user needs to be owner of the resource / admin to read the policies for it
            # to create a new policy for it - or admin. Inheritance is handled inside the allows method.
            # access_request = AccessRequest(
            #     resource_id=resource_id,
            #     action=own,
            #     current_user=current_user,
            # )
            # await self.allows(access_request)

            # await self.allows(resource_id, own, current_user)

            query = self.filters_allowed(query, read, current_user=current_user)

            # # Don't read by policy_id at all? Only by identity_id, resource_id and action?
            # if policy_id is not None:
            #     if (
            #         identity_id is not None
            #         or resource_id is not None
            #         or action is not None
            #     ):
            #         raise ValueError(
            #             "Policy ID cannot be provided with other parameters."
            #         )
            #     query = query.where(AccessPolicy.id == policy_id)
            # else:
            if identity_id is not None:
                query = query.where(AccessPolicy.identity_id == identity_id)
            if resource_id is not None:
                query = query.where(AccessPolicy.resource_id == resource_id)
            if action is not None:
                query = query.where(AccessPolicy.action == action)
            if public is True:
                query = query.where(AccessPolicy.public)

            # query = select(AccessPolicy)

            # print("=== AccessPolicyCRUD.read - query ===")
            # print(query.compile())
            # print(query.compile().params)

            response = await self.session.exec(query)
            results = response.all()

            # print("=== AccessPolicyCRUD.read - results ===")
            # pprint(results)

            if not results:
                raise HTTPException(status_code=404, detail="Access policy not found.")

            return results
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found.")

    async def read_access_policies_for_resource(
        self,
        resource_id: UUID,
        current_user: CurrentUserData,
    ):
        """Returns all access policies by resource id."""
        try:
            access_policies = await self.read(current_user, resource_id=resource_id)
            return access_policies
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Access policies not found.")

    async def read_access_policies_for_identity(
        self,
        identity_id: UUID,
        current_user: CurrentUserData,
    ):
        """Returns a User with linked Groups from the database."""
        try:
            filters = [
                AccessPolicy.identity_id == identity_id,
            ]
            access_policies = await self.read(current_user, filters=filters)
            return access_policies
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="AccessPolicies not found.")

    async def delete(
        self,
        current_user: Optional["CurrentUserData"],
        # policy_id: Optional[int] = None,
        access_policy: AccessPolicy,
        # access_request: AccessRequest,
        # identity_id: Optional[UUID] = None,
        # resource_id: Optional[int] = None,
        # action: Optional[Action] = None,
    ) -> None:
        """Deletes an access control policy."""

        # TBD: add some access checks here:
        # if current_user is Admin: allow all.
        # otherwise: identity_id must be either current_user.id or a group the current_user is member of.
        # if no identity id, the resource needs to be public
        # current_user must have own rights on the resource to delete a policy

        # TBD: leave the access control for delete to the read method here
        # or make another allows method call here?

        # To delete a policy, current user needs to be owner of the resource or Admin!

        try:
            # session = self.session

            # if policy_id is not None:
            #     if (
            #         identity_id is not None
            #         or resource_id is not None
            #         or action is not None
            #     ):
            #         raise ValueError(
            #             "Policy ID cannot be provided with other parameters."
            #         )
            #     policy = await session.get(AccessPolicy, policy_id)
            #     if policy is None:
            #         logger.error(
            #             f"Error in deleting policy: policy {policy_id} not found"
            #         )
            #         raise HTTPException(
            #             status_code=404, detail="Access policy not found"
            #         )
            #     await session.delete(policy)
            # else:

            resource_id, identity_id, action, public = (
                access_policy.resource_id,
                access_policy.identity_id,
                access_policy.action,
                access_policy.public,
            )

            # access_request = AccessRequest(
            #     resource_id=resource_id,
            #     action=own,
            #     current_user=current_user,
            # )
            # await self.allows(access_request)

            # policies = await self.read(
            #     identity_id=identity_id,
            #     resource_id=resource_id,
            #     action=action,
            # )
            # for policy in policies:
            #     policy = await self.session.get(AccessPolicy, policy_id)
            #     if policy is None:
            #         logger.error(
            #             f"Error in deleting policy: policy {policy_id} not found"
            #         )
            #         raise HTTPException(
            #             status_code=404, detail="Access policy not found"
            #         )
            #     await self.session.delete(policy)

            # TBD: make sure to write tests for this - especially that nothing undesired gets deleted!
            # access_request = AccessRequest(
            #     resource_id=access_policy.resource_id,
            #     action=own,
            #     current_user=current_user,
            # )

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
            if public is not None:
                statement.where(AccessPolicy.public == public)

            await self.session.exec(statement)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Error in deleting policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found")


class AccessLoggingCRUD:
    """Logging access attempts to database."""

    def __init__(self):
        self

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def log_access(
        self,
        access_log: AccessLogCreate,
    ) -> AccessLog:
        """Logs an access attempt to the database."""
        logger.info("Writing an access log to the database.")
        access_log = AccessLog.model_validate(access_log)
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write here
        try:
            session = self.session
            session.add(access_log)
            await session.commit()
            await session.refresh(access_log)
            return access_log
        except Exception as e:
            logger.error(f"Error in logging: {e}")
            raise HTTPException(status_code=400, detail="Bad request: logging failed")
        # finally:
        #     await self.session.close()

    # Do we need current_user here?
    # TBD: create a generic read method and use it here.
    # TBD implement crud tests for this?
    async def read_log_by_identity_id(self, identity_id: UUID) -> list[AccessLogRead]:
        """Reads access logs by identity id."""
        logger.info("Reading identity access logs from the database.")
        try:
            session = self.session
            query = select(AccessLog).where(
                AccessLog.identity_id == identity_id,
            )
            response = await session.exec(query)
            results = response.all()
            return results
        except Exception as e:
            logger.error(f"Error in reading log: {e}")
            raise HTTPException(status_code=404, detail="Log not found")

    # Do we need current_user here?
    # TBD: create a generic read method and use it here.
    # TBD: implement more crud tests for this?
    async def read_log_by_resource(
        self, resource_id: UUID  # ,   resource_type: ResourceType
    ) -> list[AccessLogRead]:
        """Reads access logs by resource id and type."""
        logger.info("Reading resource access logs from the database.")
        try:
            session = self.session
            query = select(AccessLog).where(
                AccessLog.resource_id == resource_id,
            )
            response = await session.exec(query)
            results = response.all()
            return results
        except Exception as e:
            logger.error(f"Error in reading log: {e}")
            raise HTTPException(status_code=404, detail="Log not found")

    # TBD: create a generic read method and use it here.
    async def read_log_created(self, resource_id: UUID) -> AccessLogRead:
        """Reads first access log with action "Own" for resource id and type - corresponds to create."""
        logger.info("Reading create information from access logs in database.")
        try:
            session = self.session
            query = (
                select(AccessLog)
                .where(
                    AccessLog.resource_id == resource_id,
                )
                .order_by(AccessLog.time)
                .limit(1)
            )
            response = await session.exec(query)
            result = response.one()
            return result
        except Exception as e:
            logger.error(f"Error in reading log: {e}")
            raise HTTPException(status_code=404, detail="Log not found")
