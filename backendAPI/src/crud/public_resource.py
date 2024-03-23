import logging

from fastapi import HTTPException
from models.public_resource import (
    PublicResource,
    PublicResourceCreate,
    PublicResourceRead,
    PublicResourceUpdate,
)
from core.databases import get_async_session
import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)


class PublicResourceCRUD:
    """CRUD for PublicResource - absolutely no protection"""

    # Can be used to derive a public_base_CRUD

    def __init__(self):
        """Initializes the CRUD for PublicResource."""
        pass

    async def __aenter__(self) -> AsyncSession:
        """Returns a database session."""
        self.session = await get_async_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the database session."""
        await self.session.close()

    async def create(
        self,
        public_resource: PublicResourceCreate,
    ) -> PublicResource:
        """Creates a new public resource."""
        logger.info("PublicResourceCRUD.create")

        try:
            session = self.session
            database_public_resource = PublicResource.model_validate(public_resource)

            session.add(database_public_resource)
            await session.commit()
            await session.refresh(database_public_resource)
            # TBD: add access log here!
            return database_public_resource
        except Exception as e:
            # TBD: add access logging here!
            logger.error(f"Error in PublicResourceCRUD.create: {e}")
            raise HTTPException(status_code=404, detail="Object not found")

    # TBD: implement a create_if_not_exists method

    # TBD: add skip and limit
    # async def read_all(self, skip: int = 0, limit: int = 100)  -> list[BaseModelType]:
    async def read_all(self) -> list[PublicResourceRead]:
        """Returns all public resources."""
        session = self.session
        # statement = select(self.model).offset(skip).limit(limit)
        response = await session.exec(select(PublicResource))
        if response is None:
            # TBD: add access logging here!
            raise HTTPException(status_code=404, detail="No objects found")
        # TBD: add access logging here!
        return response.all()

    async def read_by_id(
        self,
        public_resource_id: uuid.UUID,
    ) -> PublicResourceRead:
        """Returns a public resource by id."""
        session = self.session
        public_resource = await session.get(PublicResource, public_resource_id)
        if public_resource is None:
            # TBD: add access logging here!
            raise HTTPException(status_code=404, detail="Object not found")
        return public_resource

    async def update(
        self,
        old: PublicResource,
        new: PublicResourceUpdate,
    ) -> PublicResource:
        """Updates an public resource."""
        session = self.session
        updated = new.model_dump(exclude_unset=True)
        for key, value in updated.items():
            # if (
            #     key == "created_at"
            #     or key == "last_updated_at"
            #     # or key == "last_accessed_at"
            # ):
            #     continue
            setattr(old, key, value)
        public_resource = old
        session.add(public_resource)
        await session.commit()
        await session.refresh(public_resource)
        # TBD: add exception handling here!
        # TBD: add access logging here!
        return public_resource

    async def delete(self, public_resource_id: uuid.UUID) -> PublicResource:
        """Deletes a public resource."""
        session = self.session
        # TBD: refactor into try-except block and add logging
        public_resource = await session.get(PublicResource, public_resource_id)
        if public_resource is None:
            raise HTTPException(status_code=404, detail="Object not found")
        await session.delete(public_resource)
        await session.commit()
        return public_resource
