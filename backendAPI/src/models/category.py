from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

# from .demo_resource import DemoResource

if TYPE_CHECKING:
    from .demo_resource import DemoResource


class CategoryCreate(SQLModel):
    name: str = Field(max_length=12)
    description: Optional[str] = None


class Category(CategoryCreate, table=True):
    category_id: Optional[int] = Field(default=None, primary_key=True)

    demo_resources: List["DemoResource"] = Relationship(
        back_populates="category", sa_relationship_kwargs={"lazy": "selectin"}
    )


class CategoryUpdate(CategoryCreate):
    name: Optional[str] = None


class CategoryRead(CategoryCreate):
    category_id: int


# class CategoryReadWithDemoResources(Category):
#     demo_resources: List[DemoResource] = []
