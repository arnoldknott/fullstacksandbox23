from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# from .demo_resource import DemoResource


class CategoryCreate(SQLModel):
    name: str = Field(max_length=12)
    description: Optional[str] = None


class Category(CategoryCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    demo_resources: List["DemoResource"] = Relationship(  # noqa: F821
        back_populates="category"
    )


class CategoryUpdate(CategoryCreate):
    pass
