from models.category import Category, CategoryCreate, CategoryUpdate

from .base import BaseCRUD


class CategoryCRUD(BaseCRUD[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)
