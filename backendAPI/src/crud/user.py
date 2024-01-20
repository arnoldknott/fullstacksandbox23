# from fastapi import HTTPException
import logging
from typing import List, Optional

from fastapi import HTTPException
from models.group_user_link import GroupUserLink
from models.user import User, UserCreate, UserRead, UserUpdate
from sqlmodel import select

from .base import BaseCRUD
from .group import GroupCRUD

logger = logging.getLogger(__name__)


class UserCRUD(BaseCRUD[User, UserCreate, UserRead, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    # Not needed any more, since azure_user_id is the primary key!
    # async def read_by_azure_user_id(self, azure_user_id: str) -> UserRead:
    #     """Returns a User with linked Groups from the database."""
    #     async with self.session as session:
    #         user = await session.get(User, azure_user_id)
    #         if user is None:
    #             raise HTTPException(status_code=404, detail="User not found")
    #         return user

    # This allows self-sign-up, unless user has been disabled by admin!
    # Any user passed in, get's checked for existence, if not existing, it get's created!
    # no matter if the user existed or not, group membership gets checked and created if needed!
    # Note the difference between user_id and azure_user_id as well as group_id and azure_group_id!
    async def create_user_and_groups_if_not_exist(
        self, azure_user_id: str, azure_tenant_id: str, groups: Optional[List[str]]
    ) -> UserRead:
        """Checks if user and its groups exist, if not create and link them."""
        # print("=== user_id ===")
        # print(azure_user_id)
        # print("=== tenant_id ===")
        # print(azure_tenant_id)
        # print("=== groups ===")
        # print(groups)
        try:
            current_user = await self.read_by_id(azure_user_id)
        except HTTPException as err:
            if err.status_code == 404:
                user_create = UserCreate(
                    azure_user_id=azure_user_id, azure_tenant_id=azure_tenant_id
                )
                current_user = await self.create(user_create)
                logger.info("USER created in database")
            else:
                raise err
        # if used elsewhere consider update if needed! But should also be covered already by the base.update!
        for azure_group_id in groups:
            print(
                "=== user crud - create_user_and_groups_if_not_exist - azure_group_id ==="
            )
            print(azure_group_id)
            # call group crud to check if group exists, if not create it!
            async with GroupCRUD() as group_crud:
                await group_crud.create_if_not_exists(azure_group_id, azure_tenant_id)
                # try:
                #     group_crud.read_by_id(azure_group_id)
                # except HTTPException as err:
                #     if err.status_code == 404:
                #         group_create = GroupCreate(
                #             azure_group_id=azure_group_id,
                #             azure_tenant_id=azure_tenant_id,
                #         )
                #         group_crud.create(group_create)
                # when using this elsewhere, consider if update is needed in else if statement
                # But should also be covered already by the base.update!
            session = self.session
            user_group_link = await session.exec(
                select(GroupUserLink).where(
                    GroupUserLink.azure_user_id == azure_user_id,
                    GroupUserLink.azure_group_id == azure_group_id,
                )
            )
            user_group_link = user_group_link.first()
            # ("=== user_group_link - select ===")
            # print(user_group_link)
            if not user_group_link:
                user_group_link = GroupUserLink(
                    azure_user_id=azure_user_id,
                    azure_group_id=azure_group_id,
                )
                session.add(user_group_link)
                # print("=== user_group_link - add ===")
                # print(user_group_link)
                await session.commit()
                await session.refresh(user_group_link)
            # read again after the relationship to the groups is created:
        current_user = await self.read_by_id(azure_user_id)
        return current_user

    async def deactivate_user(self, azure_user_id: str) -> User:
        """Deactivates a user."""
        session = self.session
        async with session:
            existing_user = await session.get(User, azure_user_id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            user_update = UserUpdate(is_active=False)
            existing_user = await self.update(existing_user, user_update)
        return existing_user

    async def activate_user(self, azure_user_id: str) -> User:
        """Activates a user."""
        session = self.session
        async with session:
            existing_user = await session.get(User, azure_user_id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            user_update = UserUpdate(is_active=True)
            existing_user = await self.update(existing_user, user_update)
        return existing_user

    async def user_is_active(self, azure_user_id: str) -> bool:
        """Checks if a user is active."""
        session = self.session
        async with session:
            existing_user = await session.get(User, azure_user_id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            return existing_user.is_active
