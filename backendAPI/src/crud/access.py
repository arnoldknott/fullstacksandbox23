import logging
from uuid import UUID

from typing import List, Union, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import CurrentUserData, ResourceType, Action
from core.access import AccessControl

from fastapi import HTTPException
from models.access import AccessPolicyCreate, AccessPolicy, AccessPolicyRead, AccessLog

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
            # print("=== AccessPolicyCRUD.create - current_user ===")
            # print(current_user)
            # print("=== AccessPolicyCRUD.create - type(current_user) ===")
            # print(type(current_user))
            if not await self.access_control.allows(
                user=current_user,
                resource_id=policy.resource_id,
                resource_type=policy.resource_type,
                action=write,
            ):
                raise HTTPException(status_code=403, detail="Forbidden")
            session.add(policy)
            await session.commit()
            await session.refresh(policy)
            # await session.close()
            # async with await get_async_session() as session:
            #     policy = AccessPolicy(**policy)
            #     session.add(policy)
            #     await session.commit()
            #     await session.refresh(policy)
            return policy
        except Exception as e:
            logger.error(f"Error in creating policy: {e}")
            raise HTTPException(status_code=403, detail="Forbidden")

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
        pass

    async def read(
        self,
        policy_id: Optional[int] = None,
        identity_id: Optional[UUID] = None,
        resource_id: Optional[int] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[Action] = None,
    ) -> Union[AccessPolicyRead, List[AccessPolicyRead]]:
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
                if resource_id is not None or resource_type is not None:
                    if resource_id is None or resource_type is None:
                        raise ValueError(
                            "Both resource_id and resource_type must be provided together."
                        )
                    conditions.append(AccessPolicy.resource_id == resource_id)
                    conditions.append(AccessPolicy.resource_type == resource_type)
                if action is not None:
                    conditions.append(AccessPolicy.action == action)

                if conditions:
                    query = query.where(*conditions)

                print("=== AccessPolicyCRUD.read - session ===")
                print(session)
                print("=== AccessPolicyCRUD.read - query ===")
                print(query)
                response = await session.exec(query)
                results = response.all()

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

    async def log_access(
        self,
        access_log: AccessLog,
    ) -> AccessLog:
        """Logs an access attempt to the database."""
        logger.info("AccessLogging.log_access")
        # TBD: add access control checks here:
        # request is known from self.current_user, object and method is write here
        try:
            with get_async_session() as session:
                session.add(access_log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error in logging: {e}")
            raise HTTPException(status_code=400, detail="Bad request: logging failed")
        finally:
            await self.session.close()
        return access_log

    async def read_log_by_identity_id(self, identity_id: UUID) -> list[AccessLog]:
        """Reads access logs by identity id."""
        pass

    async def read_log_by_resource(
        self, resource_id: int, resource_type: ResourceType
    ) -> list[AccessLog]:
        """Reads access logs by identity id."""
        pass
