import logging
from uuid import UUID

from core.databases import get_async_session
from core.types import Action, ResourceType

from fastapi import HTTPException
from models.access import AccessPolicy, AccessLog

logger = logging.getLogger(__name__)


class AccessPolicyCRUD:
    """CRUD for access control policies"""

    def __init__(self):
        """Initializes the CRUD for access control policies."""
        self

    async def create(self, policy: AccessPolicy) -> AccessPolicy:
        """Creates a new access control policy."""
        pass

    async def read(
        self, identity_id: UUID, resource_id: int, action: Action
    ) -> AccessPolicy:
        """Reads an access control policy."""
        # TBD:
        # - query by request parameters
        # - add inheritance (and override checks) here:
        #   - Self-join on the resource hierarchy table and
        #   - Self join teh identity hierarchy table
        pass

    async def update(self) -> AccessPolicy:
        """Updates an access control policy."""
        pass

    async def delete(self) -> AccessPolicy:
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
