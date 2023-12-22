from datetime import datetime
from typing import List, Optional  # , TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .category import Category, CategoryRead
from .demo_resource_tag_link import DemoResourceTagLink
from .tag import Tag, TagRead

# if TYPE_CHECKING:
#     # from .category import Category, CategoryRead
#     from .tag import Tag, TagRead


class DemoResourceCreate(SQLModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None

    category_id: Optional[int] = None


class DemoResource(DemoResourceCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    last_updated_at: datetime = Field(default=datetime.now())
    # Note: so far all times are UTC!

    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(
        back_populates="demo_resources", sa_relationship_kwargs={"lazy": "selectin"}
    )

    tags: Optional[List["Tag"]] = Relationship(
        back_populates="demo_resources",
        link_model=DemoResourceTagLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class DemoResourceRead(DemoResourceCreate):
    id: int
    category: Optional["CategoryRead"] = None
    tags: Optional[List["TagRead"]] = []


class DemoResourceUpdate(DemoResourceCreate):
    name: Optional[str] = None
    # last_updated_at: datetime = Field(default=datetime.now(), exclude=True)


# class DemoResourceWithTags(DemoResourceRead):
#     # tags: Optional[Tag] = []
#     tags: Optional["Tag"] = []
#     category: Optional["Category"] = None


# DemoResourceRead.update_forward_refs()

# Lots and lots of inspiration here:
# TBD: url: str
# TBD: add tags
# TBD: add owner
# TBD: add created_at
# TBD: add updated_at
# TBD: add deleted_at
# TBD: add is_deleted
# TBD: add is_active
# TBD: add is_public
# TBD: add is_private
# TBD: add is_protected
# TBD: add is_hidden
# TBD: add is_secret
# TBD: add is_internal
# TBD: add is_external
# TBD: add is_confidential
# TBD: add is_publicly_readable
# TBD: add is_publicly_writable
# TBD: add is_publicly_deletable
# TBD: add is_publicly_modifiable
# TBD: add is_publicly_accessible
# TBD: add is_publicly_visible
# TBD: add is_publicly_hidden
# TBD: add is_publicly_secret
# TBD: add is_publicly_internal
# TBD: add is_publicly_external
# TBD: add is_publicly_confidential
# TBD: add is_publicly_readable_by_owner
# TBD: add is_publicly_writable_by_owner
# TBD: add is_publicly_deletable_by_owner
# TBD: add is_publicly_modifiable_by_owner
# TBD: add is_publicly_accessible_by_owner
# TBD: add is_publicly_visible_by_owner
# TBD: add is_publicly_hidden_by_owner
# TBD: add is_publicly_secret_by_owner
# TBD: add is_publicly_internal_by_owner
# TBD: add is_publicly_external_by_owner
# TBD: add is_publicly_confidential_by_owner
# TBD: add is_publicly_readable_by_group
# TBD: add is_publicly_writable_by_group
# TBD: add is_publicly_deletable_by_group
# TBD: add is_publicly_modifiable_by_group
# TBD: add is_publicly_accessible_by_group
# TBD: add is_publicly_visible_by_group
# TBD: add is_publicly_hidden_by_group
