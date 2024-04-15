# from fastapi import HTTPException
import logging
from typing import List, Optional
from fastapi import HTTPException

# from models.azure_group_user_link import AzureGroupUserLink
from core.types import Action
from core.types import CurrentUserData
from models.identity import (
    User,
    UserCreate,
    UserRead,
    UserUpdate,
    AzureGroupUserLink,
    AzureGroup,
    AzureGroupCreate,
    AzureGroupRead,
    AzureGroupUpdate,
)
from sqlmodel import select


# from sqlalchemy.orm import selectinload

# from .azure_group import AzureGroupCRUD
from .base import BaseCRUD

logger = logging.getLogger(__name__)


class AzureGroupCRUD(
    BaseCRUD[AzureGroup, AzureGroupCreate, AzureGroupRead, AzureGroupUpdate]
):
    def __init__(self):
        # super().__init__(AzureGroup, IdentityType.azure_group)
        super().__init__(AzureGroup)

    # TBD: refactor into access control and just call self.create() with current_user!
    async def create_if_not_exists(
        self, azure_group_id: str, azure_tenant_id: str
    ) -> AzureGroupRead:
        """Creates a new group if it does not exist."""
        # try:
        #     existing_group = await self.read_by_id(azure_group_id)
        # except HTTPException as err:
        #     if err.status_code == 404:
        existing_group = await self.session.get(AzureGroup, azure_group_id)
        if existing_group is None:
            try:
                # TBD: refactor to use create from base class!
                group_create = AzureGroupCreate(
                    id=azure_group_id,
                    azure_tenant_id=azure_tenant_id,
                )
                # TBD: After refactoring into access control, the create method should cannot be used any more here.
                # group does not exist and there is no access policy for the group to create itself.
                # Do we need the current user here? Make sure not to run into a circular dependency!
                # existing_group = await self.create(group_create)
                session = self.session
                database_group = AzureGroup.model_validate(group_create)
                session.add(database_group)
                await session.commit()
                await session.refresh(database_group)
                existing_group = database_group
            except Exception as err:
                logging.error(err)
                raise HTTPException(status_code=404, detail="Group not found.")
            # else:
            #     raise err
        return existing_group


class UserCRUD(BaseCRUD[User, UserCreate, UserRead, UserUpdate]):
    def __init__(self):
        # super().__init__(User, IdentityType.user)
        super().__init__(User)

    async def read_by_azure_user_id(
        self, azure_user_id: str, current_user: CurrentUserData
    ) -> UserRead:
        """Returns a User with linked Groups from the database."""
        try:
            filters = [User.azure_user_id == azure_user_id]
            user = await self.read(current_user, filters=filters)
            return user[0]
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="User not found")

    # This allows self-sign-up, unless user has been disabled by admin!
    # Any user passed in, get's checked for existence, if not existing, it get's created!
    # no matter if the user existed or not, group membership gets checked and created if needed!
    # Note the difference between user_id and azure_user_id as well as group_id and azure_group_id!
    # TBD: rename into azure_user_self_sign_up()!
    async def create_azure_user_and_groups_if_not_exist(
        self,
        azure_user_id: str,
        azure_tenant_id: str,
        # TBD add the roles to be able to create CurrentUserData here - needed for "access controlled" creation of the groups.
        groups: Optional[List[str]],
    ) -> UserRead:
        """Checks if user and its groups exist, if not create and link them."""
        session = self.session
        current_user_data = None
        try:
            # Note: current_user is not available here during self-sign-up! So no access control here!
            statement = select(User).where(User.azure_user_id == azure_user_id)
            results = await session.exec(statement)
            current_user = results.first()
            if current_user is None:
                raise HTTPException(status_code=404, detail="User not found")
        except HTTPException as err:
            if err.status_code == 404:
                try:
                    user_create = UserCreate(
                        azure_user_id=azure_user_id,
                        azure_tenant_id=azure_tenant_id,
                    )

                    database_user = User.model_validate(user_create)
                    session.add(database_user)
                    await session.commit()
                    await session.refresh(database_user)
                    current_user = database_user
                    current_user_data = CurrentUserData(
                        user_id=current_user.id,
                        roles=[],  # Roles are coming from the token - but this information is not available here!
                        groups=groups,
                    )
                    await self._write_policy(
                        current_user.id, Action.own, current_user_data
                    )
                    await self._write_log(
                        current_user.id, Action.own, current_user_data, 201
                    )
                    logger.info("USER created in database")
                except Exception as err:
                    await self._write_log(
                        current_user.id, Action.own, current_user_data, 404
                    )
                    logger.error(f"Error in BaseCRUD.create: {err}")
                    raise HTTPException(status_code=404, detail="User not found")
            else:
                raise err
        # if used elsewhere consider update if needed! But should also be covered already by the base.update!
        for azure_group_id in groups:
            # print(
            #     "=== user crud - create_azure_user_and_groups_if_not_exist - azure_group_id ==="
            # )
            # print(azure_group_id)
            # call group crud to check if group exists, if not create it!
            # TBD: refactor into using the access controlled protected methods:
            # Now the user actually exists and security can provide the CurrentUserData!
            # use current_user_data for this!
            async with AzureGroupCRUD() as group_crud:
                # TBD: add access control:
                # members of groups need to have read access to the group -
                # even if it exists already!
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
            # TBD: is the link table enough? no need to write a policy for groups?
            session = self.session
            azure_user_group_link = await session.exec(
                select(AzureGroupUserLink).where(
                    AzureGroupUserLink.azure_user_id == azure_user_id,
                    AzureGroupUserLink.azure_group_id == azure_group_id,
                )
            )
            azure_user_group_link = azure_user_group_link.first()
            # print("=== user_group_link - select ===")
            # print(azure_user_group_link)
            if not azure_user_group_link:
                azure_user_group_link = AzureGroupUserLink(
                    azure_user_id=azure_user_id,
                    azure_group_id=azure_group_id,
                )
                session.add(azure_user_group_link)
                # print("=== user_group_link - add ===")
                # print(azure_user_group_link)
                await session.commit()
                await session.refresh(azure_user_group_link)
            # read again after the relationship to the groups is created:
        # TBD: put this one back in - but now with the current_user parameter!
        # current_user = await self.read_by_azure_user_id(
        #     azure_user_id  # , update_last_access
        # )
        return current_user

    # Hose are not even used anywhere yet - so no priority to update them!
    # # TBD: Refactor into access control: just call self.update()
    # async def deactivate_user(self, azure_user_id: str) -> User:
    #     """Deactivates a user."""
    #     session = self.session
    #     # async with session:
    #     existing_user = await session.get(User, azure_user_id)
    #     if not existing_user:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     user_update = UserUpdate(is_active=False)
    #     existing_user = await self.update(existing_user, user_update)
    #     return existing_user

    # # TBD: Refactor into access control: just call self.update()
    # async def activate_user(self, azure_user_id: str) -> User:
    #     """Activates a user."""
    #     session = self.session
    #     # async with session:
    #     existing_user = await session.get(User, azure_user_id)
    #     if not existing_user:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     user_update = UserUpdate(is_active=True)
    #     existing_user = await self.update(existing_user, user_update)
    #     return existing_user

    # # TBD: Refactor into access control: just call self.read() and return the is_active field!
    # async def user_is_active(self, azure_user_id: str) -> bool:
    #     """Checks if a user is active."""
    #     session = self.session
    #     # async with session:
    #     existing_user = await session.get(User, azure_user_id)
    #     if not existing_user:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return existing_user.is_active
