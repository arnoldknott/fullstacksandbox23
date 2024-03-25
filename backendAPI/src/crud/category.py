from typing import List

from fastapi import HTTPException
from models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate
from models.demo_resource import DemoResource
from sqlmodel import select

from .base import BaseCRUD


class CategoryCRUD(BaseCRUD[Category, CategoryCreate, CategoryRead, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)

    # TBD: add access control and access logging for this!
    # Move to DemoResourceCRUD?
    async def read_all_demo_resources(self, category_id) -> List[DemoResource]:
        """Returns all demo resources within category."""
        session = self.session
        statement = select(DemoResource).where(DemoResource.category_id == category_id)
        print("=== statement ===")
        print(statement)
        response = await session.exec(statement)
        # category = response.one()
        # demo_resources = category.demo_resources
        demo_resources = response.all()
        if not demo_resources:
            raise HTTPException(status_code=404, detail="No demo resources found")
        return demo_resources
