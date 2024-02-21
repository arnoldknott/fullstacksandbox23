from typing import List
import logging
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

    async def read_by_id_with_childs(self, demo_resource_id: int) -> DemoResourceRead:
        """Returns the demo resource with id and includes its childs."""
        session = self.session
        try:

            demo_resource = await session.get(DemoResource, demo_resource_id)
            return demo_resource
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="Demo resource not found")
        # if demo_resource is None:
        #     raise HTTPException(status_code=404, detail="Object not found")
        # return demo_resource

    # TBD: turn into list of tag-Ids, to allow multiple tags
    async def add_tag(
        self, demo_resource_id: int, tag_ids: List[int]
    ) -> DemoResourceRead:
        """Adds a tag to a demo resource."""
        session = self.session
        # TBD: refactor into try-except block and add logging
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
