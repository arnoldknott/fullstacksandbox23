import logging
from uuid import UUID

from pprint import pprint

from typing import List, Optional
from sqlmodel import select, or_, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import CurrentUserData, Action

# from core.access import AccessControl

from fastapi import HTTPException
from models.access import (
    AccessPolicyCreate,
    AccessPolicy,
    AccessPolicyRead,
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

        # Permission overrides:
        # own includes write and read
        # write includes read
        if action == Action.read:
            action = ["own", "write", "read"]
        elif action == Action.write:
            action = ["own", "write"]
        elif action == Action.own:
            action = ["own"]

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
        resource_id: UUID,
        action: "Action",
        current_user: Optional["CurrentUserData"] = None,
    ) -> bool:
        """Checks if the user has permission including inheritance to perform the action on the resource"""
        # TBD: move the logging to the BaseCrud? Or keep it here together with the Access Control?
        # loggingCRUD = AccessLoggingCRUD()
        # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
        # Don't include the identity in the query, as public resources are not assigned to any identity!
        # TBD: implement "public" override: check if the resource is public for requested action and return True if it is!

        # # TBD: call the filters_allowed method and execute the statement here.
        # # check for public override:
        # if not current_user:
        #     # async with self.policy_crud as policy_crud:
        #     policy_crud = self.policy_crud
        #     # add join with inheritance table
        #     # policies = await policy_crud.read(
        #     #     resource_id=resource_id, resource_type=resource_type, action=action
        #     # )
        #     policies = await policy_crud.read(resource_id=resource_id, action=action)
        #     for policy in policies:
        #         if policy.public:
        #             return True
        #         else:
        #             logger.error("Error accessing resource without user information.")
        #             raise HTTPException(status_code=403, detail="Access denied")
        # # check for admin override:
        # elif current_user.roles and "Admin" in current_user.roles:
        #     return True
        # # TBD: implement the comparison of policies and request.
        # else:
        #     policy_crud = self.policy_crud
        #     # async with self.policy_crud as policy_crud:
        #     # add join with inheritance table for both resource and identity
        #     policies = await policy_crud.read(
        #         resource_id=resource_id,
        #         action=action,
        #         identity_id=current_user.user_id,
        #     )
        #     if policies is not None:
        #         return True
        #     else:
        #         logger.error("Error accessing resource.")
        #         raise HTTPException(status_code=403, detail="Access denied")

        # Necessary as otherwise an empty database could never get data into it.
        if current_user and current_user.roles and "Admin" in current_user.roles:
            return True

        try:
            query = select(AccessPolicy).where(
                AccessPolicy.resource_id == resource_id,
            )

            query = self.filters_allowed(query, action, current_user=current_user)
            # print("=== AccessPolicyCRUD.allows - query ===")
            # print(query.compile())
            # print(query.compile().params)

            # Only one policy per resource - action - identity combination is allowed!
            response = await self.session.exec(query)
            results = response.one()

            if results.resource_id == resource_id and results.action == action:
                return True
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found")

        return False

    async def create(
        self, policy: AccessPolicyCreate, current_user: CurrentUserData
    ) -> AccessPolicyRead:
        """Creates a new access control policy."""
        try:
            session = self.session
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
            if policy.identity_id != current_user.user_id:
                # Current user creates a policy for another identity.
                # Current user needs to own the resource to grant others access (share) it.
                if not await self.allows(
                    current_user=current_user,
                    resource_id=policy.resource_id,
                    # resource_type=policy.resource_type,
                    action=own,
                ):
                    raise HTTPException(status_code=403, detail="Forbidden.")
            session.add(policy)
            await session.commit()
            await session.refresh(policy)
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

    async def read(
        self,
        current_user: Optional["CurrentUserData"] = None,
        policy_id: Optional[int] = None,
        identity_id: Optional[UUID] = None,
        resource_id: Optional[int] = None,
        action: Optional[Action] = None,
    ) -> List[AccessPolicyRead]:
        """Reads access control policies based on the provided parameters."""

        # TBD: add some access checks here:
        # if current_user is Admin: allow all.
        # otherwise: identity_id must be either current_user.id or a group the current_user is member of.
        # if no identity id, the resource needs to be public

        try:
            # session = self.session
            query = select(AccessPolicy)

            print("=== AccessPolicyCRUD.read - current_user ===")
            pprint(current_user)
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

            await self.allows(resource_id, own, current_user)

            if policy_id is not None:
                if (
                    identity_id is not None
                    or resource_id is not None
                    or action is not None
                ):
                    raise ValueError(
                        "Policy ID cannot be provided with other parameters."
                    )
                query = query.where(AccessPolicy.id == policy_id)
            else:
                if identity_id is not None:
                    query = query.where(AccessPolicy.identity_id == identity_id)
                if resource_id is not None:
                    query = query.where(AccessPolicy.resource_id == resource_id)
                if action is not None:
                    query = query.where(AccessPolicy.action == action)

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
        current_user: Optional["CurrentUserData"] = None,
        policy_id: Optional[int] = None,
        identity_id: Optional[UUID] = None,
        resource_id: Optional[int] = None,
        action: Optional[Action] = None,
    ) -> None:
        """Deletes an access control policy."""

        # TBD: add some access checks here:
        # if current_user is Admin: allow all.
        # otherwise: identity_id must be either current_user.id or a group the current_user is member of.
        # if no identity id, the resource needs to be public
        # current_user must have own rights on the resource to delete a policy

        try:
            session = self.session

            if policy_id is not None:
                if (
                    identity_id is not None
                    or resource_id is not None
                    or action is not None
                ):
                    raise ValueError(
                        "Policy ID cannot be provided with other parameters."
                    )
                policy = await session.get(AccessPolicy, policy_id)
                if policy is None:
                    logger.error(
                        f"Error in deleting policy: policy {policy_id} not found"
                    )
                    raise HTTPException(
                        status_code=404, detail="Access policy not found"
                    )
                await session.delete(policy)
            else:
                policies = await self.read(
                    identity_id=identity_id,
                    resource_id=resource_id,
                    action=action,
                )
                for policy in policies:
                    policy = await session.get(AccessPolicy, policy_id)
                    if policy is None:
                        logger.error(
                            f"Error in deleting policy: policy {policy_id} not found"
                        )
                        raise HTTPException(
                            status_code=404, detail="Access policy not found"
                        )
                    await session.delete(policy)
            await session.commit()
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
