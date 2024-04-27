import logging
from uuid import UUID

from pprint import pprint

from typing import List, Optional
from sqlmodel import select, delete, or_, and_, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import CurrentUserData, Action, ResourceType, IdentityType

# from core.access import AccessControl

from fastapi import HTTPException
from models.access import (
    AccessPolicyCreate,
    AccessPolicy,
    AccessPolicyRead,
    AccessPolicyUpdate,
    AccessRequest,
    IdentifierTypeLink,
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
        if action == read:
            action = ["own", "write", "read"]
        elif action == write:
            action = ["own", "write"]
        elif action == own:
            action = ["own"]
        else:
            # TBD: write test for this: if pydantic works on verifying action types,
            # a 422 or type error should be raised before this line!
            logger.error("Invalid action provided.")
            raise HTTPException(status_code=400, detail="Bad request: invalid action.")

        if not current_user:
            if model != AccessPolicy:
                statement = statement.join(
                    AccessPolicy, model.id == AccessPolicy.resource_id
                )
                statement = statement.where(AccessPolicy.resource_id == model.id)
            statement = statement.where(AccessPolicy.action.in_(action))
            statement = statement.where(AccessPolicy.public)
        elif current_user.roles and "Admin" in current_user.roles:
            pass
        else:
            # this is becoming two different functions - one for resources and one for policies
            # consider splitting this into two functions
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
            else:
                subquery = select(AccessPolicy.resource_id).where(
                    and_(
                        AccessPolicy.identity_id == current_user.user_id,
                        AccessPolicy.action == own,
                    )
                )
                statement = statement.filter(AccessPolicy.resource_id.in_(subquery))

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
        if current_user and current_user.roles and "Admin" in current_user.roles:
            return True

        try:
            query = select(AccessPolicy)  # .where(
            # AccessPolicy.resource_id == resource_id,
            # )
            if resource_id:
                print("=== AccessPolicyCRUD.allows - add resource_id ===")
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
        try:
            # TBD: remove this, as it's already done through typing the arguments of the method?
            policy = AccessPolicy.model_validate(policy)

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
            # Yes - should definitely check if user has write access on the parent resource!
            # All endpoints that utilize the inheritance should then call the
            # create_as_child(object, parent) -> where the parent access gets checked.
            # Furthermore the instantiation of BaseCRUD needs
            # to get all possible parent models as List[SQLModel]
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

            self.session.add(policy)
            await self.session.commit()
            await self.session.refresh(policy)
            return policy
        except Exception as err:
            logger.error(f"Error in creating policy: {err}")
            print(err)
            raise HTTPException(status_code=403, detail="Forbidden.")

    # other way around: add to parent - in create_as_child
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

            print("=== AccessPolicyCRUD.read - query ===")
            print(query.compile())
            print(query.compile().params)

            response = await self.session.exec(query)
            results = response.all()

            print("=== AccessPolicyCRUD.read - results ===")
            pprint(results)

            if not results:
                raise HTTPException(status_code=404, detail="Access policy not found.")

            return results
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found.")

    async def read_access_policies_by_resource_id(
        self,
        resource_id: UUID,
        current_user: CurrentUserData,
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
        resource_type: ResourceType,
        current_user: CurrentUserData,
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
        identity_id: UUID,
        current_user: CurrentUserData,
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
        identity_type: IdentityType,
        current_user: CurrentUserData,
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
        access_policy: AccessPolicyUpdate,
        current_user: Optional["CurrentUserData"],
    ) -> AccessPolicyRead:
        """Updates an access control policy."""
        # reuses delete and create methods

        try:
            # TBD: should public be a part of the update?
            # => yes, needs to, because it's a mandatory part of the AccessPolicyCreate,
            # which AccessPolicyUpdate inherits from!
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
            return await self.create(new_policy, current_user)

        except Exception as e:
            logger.error(f"Error in updating policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found")

    async def delete(
        self,
        current_user: Optional["CurrentUserData"],
        access_policy: AccessPolicy,
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
    async def read_log_by_resource_id(
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
