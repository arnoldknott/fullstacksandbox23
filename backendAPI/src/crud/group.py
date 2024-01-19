# from fastapi import HTTPException
from fastapi import HTTPException
from models.group import Group, GroupCreate, GroupRead, GroupUpdate

from .base import BaseCRUD

# from sqlmodel import select


class GroupCRUD(BaseCRUD[Group, GroupCreate, GroupRead, GroupUpdate]):
    def __init__(self):
        super().__init__(Group)

    async def create_if_not_exists(
        self, azure_group_id: str, azure_tenant_id: str
    ) -> GroupRead:
        """Creates a new group if it does not exist."""
        try:
            existing_group = await self.read_by_id(azure_group_id)
        except HTTPException as err:
            if err.status_code == 404:
                group_create = GroupCreate(
                    azure_group_id=azure_group_id,
                    azure_tenant_id=azure_tenant_id,
                )
                existing_group = await self.create(group_create)
            else:
                raise err
        return existing_group
