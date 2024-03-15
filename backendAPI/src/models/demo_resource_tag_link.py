import uuid

from typing import Optional

from sqlmodel import Field, SQLModel


class DemoResourceTagLink(SQLModel, table=True):
    demo_resource_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="demoresource.id", primary_key=True
    )
    tag_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
