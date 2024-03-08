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

    # async def read_by_policy_id(self, policy_id: int) -> AccessPolicyRead:
    #     # TBD: maybe this should just return the highest?
    #     """Reads all access control policy for a given resource."""
    #     try:
    #         session = self.session
    #         results = await session.get(AccessPolicy, policy_id)
    #         if results is None:
    #             raise HTTPException(status_code=404, detail="Access policy not found")
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading policy: {e}")
    #         raise HTTPException(status_code=404, detail="Access policy not found")

    # async def read_by_identity(self, identity_id: UUID) -> List[AccessPolicyRead]:
    #     """Reads access control policies for a given identity."""
    #     try:
    #         session = self.session
    #         statement = select(AccessPolicy).where(
    #             AccessPolicy.identity_id == identity_id,
    #         )
    #         response = await session.exec(statement)
    #         results = response.all()
    #         if len(results) == 0:
    #             raise HTTPException(status_code=404, detail="Access policy not found")
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading policy: {e}")
    #         raise HTTPException(status_code=404, detail="Access policy not found")
    #     # except Exception as e:
    #     #     logger.error(f"Error in reading policy: {e}")
    #     #     raise HTTPException(status_code=404, detail="Access policy not found")
    #     # TBD:
    #     # - query by request parameters
    #     # - add inheritance (and override checks) here:
    #     #   - Self-join on the resource hierarchy table and
    #     #   - Self join the identity hierarchy table

    # async def read_by_resource(
    #     self, resource_id: int, resource_type: ResourceType
    # ) -> List[AccessPolicyRead]:
    #     # TBD: maybe this should just return the highest?
    #     """Reads all access control policy for a given resource."""
    #     try:
    #         session = self.session
    #         statement = select(AccessPolicy).where(
    #             AccessPolicy.resource_id == resource_id,
    #             AccessPolicy.resource_type == resource_type,
    #         )
    #         response = await session.exec(statement)
    #         results = response.all()
    #         if len(results) == 0:
    #             raise HTTPException(status_code=404, detail="Access policy not found")
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading policy: {e}")
    #         raise HTTPException(status_code=404, detail="Access policy not found")

    # async def read_by_identity_and_resource(
    #     self, identity_id: UUID, resource_id: int, resource_type: ResourceType
    # ) -> List[AccessPolicyRead]:
    #     """Reads all access control policy for a given resource."""
    #     try:
    #         session = self.session
    #         statement = select(AccessPolicy).where(
    #             AccessPolicy.identity_id == identity_id,
    #             AccessPolicy.resource_id == resource_id,
    #             AccessPolicy.resource_type == resource_type,
    #         )
    #         response = await session.exec(statement)
    #         results = response.all()
    #         if len(results) == 0:
    #             raise HTTPException(status_code=404, detail="Access policy not found")
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading policy: {e}")
    #         raise HTTPException(status_code=404, detail="Access policy not found")

    # async def read_by_identity_and_resource_and_action(
    #     self,
    #     identity_id: UUID,
    #     resource_id: int,
    #     resource_type: ResourceType,
    #     action: Action,
    # ) -> List[AccessPolicyRead]:
    #     """Reads all access control policy for a given resource."""
    #     try:
    #         session = self.session
    #         statement = select(AccessPolicy).where(
    #             AccessPolicy.identity_id == identity_id,
    #             AccessPolicy.resource_id == resource_id,
    #             AccessPolicy.resource_type == resource_type,
    #             AccessPolicy.action == action,
    #         )
    #         response = await session.exec(statement)
    #         results = response.all()
    #         if len(results) == 0:
    #             raise HTTPException(status_code=404, detail="Access policy not found")
    #         return results
    #     except Exception as e:
    #         logger.error(f"Error in reading policy: {e}")
    #         raise HTTPException(status_code=404, detail="Access policy not found")

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
