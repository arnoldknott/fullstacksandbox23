import logging
from uuid import UUID

from typing import List, Union, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import CurrentUserData, ResourceType, Action
from core.access import AccessControl

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

# access_control = AccessControl()
read = Action.read
write = Action.write
own = Action.own


class AccessPolicyCRUD:
    """CRUD for access control policies"""

    def __init__(self):
        """Initializes the CRUD for access control policies."""
        self.session = None
        self.access_control = AccessControl(self)

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def create(
        self, policy: AccessPolicyCreate, current_user: CurrentUserData
    ) -> AccessPolicyRead:
        """Creates a new access control policy."""
        try:
            session = self.session
            policy = AccessPolicy.model_validate(policy)
            # TBD: add access control checks here:
            # only owners and Admins can create policies
            # current_user = CurrentUserData(
            #     user_id=policy.identity_id,
            #     # how do i get the roles and groups here?
            # )

            # Every user can create a policy for themselves:
            if policy.identity_id != current_user.user_id:
                # Current user creates a policy for another identity.
                # Current user needs to own the resource to grant others access (share) it.
                if not await self.access_control.allows(
                    user=current_user,
                    resource_id=policy.resource_id,
                    resource_type=policy.resource_type,
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
        parent_resource_type: ResourceType,
        current_user: CurrentUserData,
    ):
        """Adds a child policy to a parent policy."""
        # TBD: make sure, that current_user has owner rights in parent_resource or is Admin
        # put that into the access_control in core.access AccessControl.allows or so?
        # TBD should this be a method of AccessPolicyCRUD or AccessControl?
        pass

    async def read(
        self,
        policy_id: Optional[int] = None,
        identity_id: Optional[UUID] = None,
        resource_id: Optional[int] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[Action] = None,
    ) -> List[AccessPolicyRead]:
        """Reads access control policies based on the provided parameters."""
        try:
            session = self.session
            query = select(AccessPolicy)

            if policy_id is not None:
                if (
                    identity_id is not None
                    or resource_id is not None
                    or resource_type is not None
                    or action is not None
                ):
                    raise ValueError(
                        "Policy ID cannot be provided with other parameters."
                    )
                results = await session.get(AccessPolicy, policy_id)
            else:
                conditions = []
                if identity_id is not None:
                    conditions.append(AccessPolicy.identity_id == identity_id)
                if resource_id is not None:
                    if resource_type is None:
                        raise ValueError(
                            "'resource_type' is required in conjunction with 'resource_id'."
                        )
                    conditions.append(AccessPolicy.resource_id == resource_id)
                    conditions.append(AccessPolicy.resource_type == resource_type)
                elif resource_type is not None:
                    conditions.append(AccessPolicy.resource_type == resource_type)
                if action is not None:
                    conditions.append(AccessPolicy.action == action)

                if conditions:
                    query = query.where(*conditions)

                # print("=== AccessPolicyCRUD.read - query ===")
                # print(query)
                # print("=== AccessPolicyCRUD.read - query.compile().params ===")
                # print(query.compile().params)

                # query = select(AccessPolicy)

                response = await session.exec(query)
                results = response.all()
                # print("=== AccessPolicyCRUD.read - results ===")
                # print(results)

            if not results:
                raise HTTPException(status_code=404, detail="Access policy not found")

            return results
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=404, detail="Access policy not found")

    async def delete(
        self,
        policy_id: Optional[int] = None,
        identity_id: Optional[UUID] = None,
        resource_id: Optional[int] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[Action] = None,
    ) -> None:
        """Deletes an access control policy."""
        try:
            session = self.session

            if policy_id is not None:
                if (
                    identity_id is not None
                    or resource_id is not None
                    or resource_type is not None
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
                    resource_type=resource_type,
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

    # TBD: is that
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
    # TBD: delete and use base class with method read_with_query_options instead?
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
    # TBD: type might not be necessary any more as input since we've switched to UUID.
    # TBD: delete and use base class with method read_with_query_options instead?
    async def read_log_by_resource(
        self, resource_id: UUID, resource_type: ResourceType
    ) -> list[AccessLogRead]:
        """Reads access logs by resource id and type."""
        logger.info("Reading resource access logs from the database.")
        try:
            session = self.session
            query = select(AccessLog).where(
                AccessLog.resource_id == resource_id,
                AccessLog.resource_type == resource_type,
            )
            response = await session.exec(query)
            results = response.all()
            return results
        except Exception as e:
            logger.error(f"Error in reading log: {e}")
            raise HTTPException(status_code=404, detail="Log not found")

    # TBD: delete and use base class with method read_with_query_options instead?
    async def read_log_created(
        self, resource_id: UUID, resource_type: ResourceType
    ) -> AccessLogRead:
        """Reads first access log with action "Own" for resource id and type - corresponds to create."""
        logger.info("Reading create information from access logs in database.")
        try:
            session = self.session
            query = (
                select(AccessLog)
                .where(
                    AccessLog.resource_id == resource_id,
                    AccessLog.resource_type == resource_type,
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
