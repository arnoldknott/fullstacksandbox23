from fastapi import HTTPException
from models.category import Category, CategoryCreate, CategoryUpdate
from models.demo_resource import DemoResource
from sqlmodel import select

from .base import BaseCRUD


class CategoryCRUD(BaseCRUD[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)

    async def read_all_demo_resources(self, category_id) -> list[DemoResource]:
        """Returns all demo resources within category."""
        session = self.session
        print("=== CRUD with session and model is called ===")
        # response = await session.get(model, category_id)
        statement = select(Category).where(Category.id == category_id)
        # .options(selectinload(model.demo_resources)))
        response = await session.exec(statement)
        category = response.one()
        print("=== response ===")
        print(response)
        print("=== category ===")
        print(category)
        print("=== category.demo_resources ===")
        print(category.demo_resources)
        # print("=== category.model_dump() ===")
        # print(category.model_dump())
        # print("=== category.model_dump_json() ===")
        print(category.model_dump_json())
        demo_resources = category.demo_resources
        if not demo_resources:
            raise HTTPException(status_code=404, detail="No demo resources found")
        return demo_resources
