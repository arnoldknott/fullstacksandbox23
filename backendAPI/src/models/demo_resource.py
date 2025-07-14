import uuid
from typing import List, Optional  # , TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# from .demo_resource_tag_link import DemoResourceTagLink
from .access import ResourceHierarchy
from .base import (
    AccessPolicyMixin,
    AccessRightsMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
)
from .category import Category, CategoryRead
from .tag import Tag, TagRead

# if TYPE_CHECKING:
#     # from .category import Category, CategoryRead
#     from .tag import Tag, TagRead


class DemoResourceCreate(SQLModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None

    category_id: Optional[uuid.UUID] = None


class DemoResource(DemoResourceCreate, table=True):
    # id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    # created_at: datetime = Field(default=datetime.now())
    # TBD: move the last_updated_at and last_accessed_at to a resource access log table
    # last_updated_at: datetime = Field(default=datetime.now())
    # Note: so far all times are UTC!

    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(
        back_populates="demo_resources", sa_relationship_kwargs={"lazy": "selectin"}
    )

    tags: Optional[List["Tag"]] = Relationship(
        back_populates="demo_resources",
        # link_model=DemoResourceTagLink,
        # sa_relationship_kwargs={"lazy": "selectin"},
        link_model=ResourceHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "DemoResource.id == foreign(ResourceHierarchy.parent_id)",
            "secondaryjoin": "Tag.id == foreign(ResourceHierarchy.child_id)",
        },
    )


class DemoResourceRead(DemoResourceCreate):
    id: uuid.UUID
    category: Optional["CategoryRead"] = None
    tags: Optional[List["TagRead"]] = None


class DemoResourceExtended(
    DemoResourceRead,
    AccessRightsMixin,
    AccessPolicyMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    pass


class DemoResourceUpdate(DemoResourceCreate):
    name: Optional[str] = None
    # last_updated_at: datetime = Field(default=datetime.now(), exclude=True)


# class DemoResourceWithTags(DemoResourceRead):
#     # tags: Optional[Tag] = []
#     tags: Optional["Tag"] = []
#     category: Optional["Category"] = None


# DemoResourceRead.update_forward_refs()
