import logging
from uuid import UUID

from typing import List, Union, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import ResourceType, Action

from fastapi import HTTPException
from models.access import AccessPolicyCreate, AccessPolicy, AccessPolicyRead, AccessLog

logger = logging.getLogger(__name__)


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

    async def create(self, policy: AccessPolicyCreate) -> AccessPolicyRead:
        """Creates a new access control policy."""
        try:
            session = self.session
            policy = AccessPolicy.model_validate(policy)
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
