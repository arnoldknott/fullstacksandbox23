from typing import List

from fastapi import HTTPException
from models.demo_resource import (
    DemoResource,
    DemoResourceCreate,
    DemoResourceRead,
    DemoResourceUpdate,
)
from models.demo_resource_tag_link import DemoResourceTagLink
from models.tag import Tag
from sqlmodel import select

from .base import BaseCRUD

# from sqlalchemy.future import select


class DemoResourceCRUD(
    BaseCRUD[DemoResource, DemoResourceCreate, DemoResourceRead, DemoResourceUpdate]
):
    def __init__(self):
        super().__init__(DemoResource)

    async def read_by_id_with_childs(self, object_id: int) -> DemoResourceRead:
        """Returns an object by id."""
        session = self.session
        object = await session.get(DemoResource, object_id)
        if object is None:
            raise HTTPException(status_code=404, detail="Object not found")
        return object

    # TBD: turn into list of tag-Ids, to allow multiple tags
    async def add_tag(
        self, demo_resource_id: int, tag_ids: List[int]
    ) -> DemoResourceRead:
        """Adds a tag to a demo resource."""
        session = self.session
        statement = select(DemoResource).where(
            DemoResource.demo_resource_id == demo_resource_id
        )
        demo_resource = await session.exec(statement)
        demo_resource = demo_resource.one()
        if not demo_resource:
            raise HTTPException(status_code=404, detail="No demo resource found")
        statement = select(Tag).where(Tag.tag_id.in_(tag_ids))
        tags = await session.exec(statement)
        tags = tags.all()
        if not tags:
            raise HTTPException(status_code=404, detail="No tag found")
        for tag in tags:
            link = DemoResourceTagLink(
                demo_resource_id=demo_resource_id, tag_id=tag.tag_id
            )
            session.add(link)
        # demo_resource.tags.append(tag[0])
        # demo_resource.tags = tag
        await session.commit()
        await session.refresh(demo_resource)
        return demo_resource
