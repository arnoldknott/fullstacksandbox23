from typing import Optional

from sqlmodel import Field, SQLModel


class DemoResourceTagLink(SQLModel, table=True):
    demo_resource_id: Optional[int] = Field(
        default=None, foreign_key="demoresource.demo_resource_id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.tag_id", primary_key=True
    )
