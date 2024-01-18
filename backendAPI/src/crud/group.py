# from fastapi import HTTPException
from fastapi import HTTPException
from models.group import Group, GroupCreate, GroupUpdate

from .base import BaseCRUD

# from sqlmodel import select


class GroupCRUD(BaseCRUD[Group, GroupCreate, GroupUpdate]):
    def __init__(self):
        super().__init__(Group)

    async def user_is_active(self, group_id: str) -> bool:
        """Checks if a user is active."""
        session = self.session
        async with session:
            existing_user = await session.get(Group, group_id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            return existing_user.is_active
