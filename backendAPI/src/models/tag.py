from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .demo_resource import DemoResource
# from .demo_resource import DemoResource
from .demo_resource_tag_link import DemoResourceTagLink


class TagCreate(SQLModel):
    name: str = Field(max_length=10)


class Tag(TagCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    demo_resources: Optional[List["DemoResource"]] = Relationship(
        back_populates="tags",
        link_model=DemoResourceTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TagUpdate(TagCreate):
    pass


class TagRead(TagCreate):
    id: int


# class TagReadWithDemoResources(Tag):
#     demo_resources: List["DemoResource"] = []
