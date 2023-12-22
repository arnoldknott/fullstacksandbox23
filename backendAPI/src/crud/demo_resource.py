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


class DemoResourceCRUD(BaseCRUD[DemoResource, DemoResourceCreate, DemoResourceUpdate]):
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
        statement = select(DemoResource).where(DemoResource.id == demo_resource_id)
        demo_resource = await session.exec(statement)
        demo_resource = demo_resource.one()
        if not demo_resource:
            raise HTTPException(status_code=404, detail="No demo resource found")
        # print("=== demo_resource ===")
        # print(demo_resource)
        statement = select(Tag).where(Tag.id.in_(tag_ids))
        tags = await session.exec(statement)
        tags = tags.all()
        if not tags:
            raise HTTPException(status_code=404, detail="No tag found")
        # print("=== tags ===")
        # print(tags)
        # print("=== tag[0] ===")
        # print(tags[0])
        # print("=== tag[1] ===")
        # print(tags[1])
        for tag in tags:
            link = DemoResourceTagLink(demo_resource_id=demo_resource_id, tag_id=tag.id)
            session.add(link)
        # demo_resource.tags.append(tag[0])
        # demo_resource.tags = tag
        # await session.commit()
        # await session.refresh(demo_resource)
        await session.commit()
        await session.refresh(demo_resource)
        # print("=== demo_resource ===")
        # print(demo_resource)
        return demo_resource


# class DemoResourceCRUD:
#     """Create, Read, Update, Delete operations for demo resources in database."""

#     # pass

#     def __init__(self, session: AsyncSession = Depends(get_async_session)):
#         """Provides a database session for CRUD operations."""
#         self.session = session

#     async def create(self, resource: DemoResourceCreate) -> DemoResource:
#         """Creates a new resource."""
#         print("=== resource ===")
#         print(resource)
#         print("=== resource.model_dump() ===")
#         print(resource.model_dump())
#         # print("=== **resource.model_dump() ===")
#         # print(**resource.model_dump())
#         print("=== DemoResource(**resource.model_dump()) ===")
#         print(DemoResource(**resource.model_dump()))
#         database_resource = DemoResource(**resource.model_dump())
#         # database_resource = resource
#         # database_resource = DemoResource(**resource.dict())
#         self.session.add(database_resource)
#         await self.session.commit()
#         await self.session.refresh(database_resource)
#         return database_resource

#     async def read_all(self) -> list[DemoResource]:
#         """Returns all demo resources."""
#         statement = select(DemoResource)
#         response = await self.session.exec(statement)
#         if response is None:
#             raise HTTPException(status_code=404, detail="No resources found")
#         return response.all()

#     async def read_by_id(self, resource_id: int) -> DemoResource:
#         """Returns a demo resource by id."""
#         resource = await self.session.get(DemoResource, resource_id)
#         if resource is None:
#             raise HTTPException(status_code=404, detail="Resource not found")
#         return resource

#     async def update(self, old: DemoResource, new: DemoResourceUpdate) -> DemoResource:
#         """Updates a demo resource."""
#         # TBD: consider using .model_dump(exclude_unset=True)
#         for key, value in vars(new).items():  # .model_dump().items():
#             if value is not None:
#                 setattr(old, key, value)
#         resource = old
#         self.session.add(resource)
#         await self.session.commit()
#         await self.session.refresh(resource)
#         return resource

#     async def delete(self, resource_id: int) -> DemoResource:
#         """Deletes a demo resource."""
#         resource = await self.session.get(DemoResource, resource_id)
#         if resource is None:
#             raise HTTPException(status_code=404, detail="Resource not found")
#         await self.session.delete(resource)
#         await self.session.commit()
#         return resource
