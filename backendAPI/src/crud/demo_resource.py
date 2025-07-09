from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select

from core.types import CurrentUserData
from models.demo_resource import (
    DemoResource,
    DemoResourceCreate,
    DemoResourceRead,
    DemoResourceUpdate,
)
from models.demo_resource_tag_link import DemoResourceTagLink
from models.tag import Tag

from .base import BaseCRUD

# from sqlalchemy.future import select


class DemoResourceCRUD(
    BaseCRUD[DemoResource, DemoResourceCreate, DemoResourceRead, DemoResourceUpdate]
):
    def __init__(self):
        super().__init__(DemoResource, allow_standalone=True)

    # TBD: turn into list of tag-Ids, to allow multiple tags
    # TBD: refactor into access control - this might include the hierarchy of the resources!
    # TBD: This is a link table,
    # so probably base crud need a new method for linking.
    # This method should then be reusable for all link tables:
    # like sharing, tagging, creating hierarchies etc.
    # TBD: should not be needed any more after refactoring the DemoResource and Tag endpoints!
    # async def add_tag(self, demo_resource_id, tag_ids) -> DemoResourceRead:
    #     """Adds a tag to a demo resource."""
    #     # TBD: refactor to use parent attribute in post method and utilize ResourceHierarchy!
    #     session = self.session
    #     # TBD: refactor into try-except block and add logging
    #     statement = select(DemoResource).where(DemoResource.id == demo_resource_id)
    #     demo_resource = await session.exec(statement)
    #     demo_resource = demo_resource.unique().one()
    #     if not demo_resource:
    #         raise HTTPException(status_code=404, detail="No demo resource found")
    #     statement = select(Tag).where(Tag.id.in_(tag_ids))
    #     tags = await session.exec(statement)
    #     tags = tags.unique().all()
    #     if not tags:
    #         raise HTTPException(status_code=404, detail="No tag found")
    #     for tag in tags:
    #         link = DemoResourceTagLink(demo_resource_id=demo_resource_id, tag_id=tag.id)
    #         session.add(link)
    #     await session.commit()
    #     await session.refresh(demo_resource)
    #     return demo_resource

    # TBD: should the return type be a DemoResourceRead?
    async def read_by_category_id(
        self, current_user: CurrentUserData, category_id: UUID
    ) -> List[DemoResource]:
        """Returns all demo resources within category."""
        return await self.read(
            current_user, filters=[DemoResource.category_id == category_id]
        )

    async def read_by_tag_id(
        self, current_user: CurrentUserData, tag_id: UUID
    ) -> List[DemoResourceRead]:
        """Returns all demo resources with tag."""
        results = await self.read(
            current_user, filters=[DemoResource.tags.any(Tag.id == tag_id)]
        )
        return results
