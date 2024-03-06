import logging
from uuid import UUID

from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.databases import get_async_session
from core.types import ResourceType

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
            raise HTTPException(status_code=404, detail="Resource not found")

    async def read_by_identity(self, identity_id: UUID) -> List[AccessPolicyRead]:
        """Reads an access control policy."""
        try:
            session = self.session
            statement = select(AccessPolicy).where(
                AccessPolicy.identity_id == identity_id,
            )
            print("=== AccessPolicyCRUD.read_by_identity - statement ===")
            print(statement)
            results = await session.exec(statement)
            return results.all()
        except Exception as e:
            logger.error(f"Error in reading policy: {e}")
            raise HTTPException(status_code=404, detail="Resource not found")
        # TBD:
        # - query by request parameters
        # - add inheritance (and override checks) here:
        #   - Self-join on the resource hierarchy table and
        #   - Self join the identity hierarchy table

    async def read_by_resource(
        self, resource_id: int, resource_type: ResourceType
    ) -> List[AccessPolicy]:
        # TBD: maybe this should just return the highest?
        """Reads all access control policy for a given resource."""
        pass

    async def delete(self) -> None:
        """Deletes an access control policy."""
        pass


class AccessLogging:
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
