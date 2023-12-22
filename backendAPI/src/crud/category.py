from typing import List

from fastapi import HTTPException
from models.category import Category, CategoryCreate, CategoryUpdate
from models.demo_resource import DemoResource
from sqlmodel import select

from .base import BaseCRUD


class CategoryCRUD(BaseCRUD[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)

    # async def read_tag_with_all_demo_resources(
    #     self, category_id
    # ) -> CategoryReadWithDemoResources:
    #     """Returns all demo resources within category."""
    #     session = self.session
    #     statement = select(Category).where(Category.id == category_id)
    #     response = await session.exec(statement)
    #     category = response.one()
    #     return category

    # demo_resources = category.demo_resources
    # if not demo_resources:
    #     raise HTTPException(status_code=404, detail="No demo resources found")
    # return CategoryReadWithDemoResources.from_orm(category)

    async def read_all_demo_resources(self, category_id) -> List[DemoResource]:
        """Returns all demo resources within category."""
        session = self.session
        statement = select(Category).where(Category.id == category_id)
        response = await session.exec(statement)
        category = response.one()
        demo_resources = category.demo_resources
        if not demo_resources:
            raise HTTPException(status_code=404, detail="No demo resources found")
        return demo_resources
