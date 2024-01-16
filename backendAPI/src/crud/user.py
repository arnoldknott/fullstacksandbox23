# from fastapi import HTTPException
from models.user import User, UserCreate, UserUpdate

from .base import BaseCRUD

# from sqlmodel import select


class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    # async def
