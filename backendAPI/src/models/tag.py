import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .demo_resource import DemoResource
# from .demo_resource import DemoResource
# from .demo_resource_tag_link import DemoResourceTagLink
from .access import ResourceHierarchy


class TagCreate(SQLModel):
    name: str = Field(max_length=10)


class Tag(TagCreate, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )

    demo_resources: Optional[List["DemoResource"]] = Relationship(
        back_populates="tags",
        # link_model=DemoResourceTagLink,
        # sa_relationship_kwargs={"lazy": "selectin"},
        link_model=ResourceHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "Tag.id == foreign(ResourceHierarchy.child_id)",
            "secondaryjoin": "DemoResource.id == foreign(ResourceHierarchy.parent_id)",
        },
    )


class TagUpdate(TagCreate):
    pass


class TagRead(TagCreate):
    id: uuid.UUID


# class TagReadWithDemoResources(Tag):
#     demo_resources: List["DemoResource"] = []
