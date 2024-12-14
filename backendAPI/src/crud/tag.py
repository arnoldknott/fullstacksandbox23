# from fastapi import HTTPException
# from models.demo_resource import DemoResource
from models.tag import Tag, TagCreate, TagRead, TagUpdate

from .base import BaseCRUD

# from sqlmodel import select


class TagCRUD(BaseCRUD[Tag, TagCreate, TagRead, TagUpdate]):
    def __init__(self):
        super().__init__(Tag, allow_standalone=True)

    # # TBD: add access control and access logging for this - use self.read()!
    # # Move to DemoResourceCRUD?
    # async def read_all_demo_resources(self, tag_id) -> list[DemoResource]:
    #     """Returns all demo resources within category."""
    #     session = self.session
    #     statement = select(Tag).where(Tag.id == tag_id)
    #     response = await session.exec(statement)
    #     tag = response.one()
    #     demo_resources = tag.demo_resources
    #     if not demo_resources:
    #         raise HTTPException(status_code=404, detail="No demo resources found")
    #     return demo_resources
