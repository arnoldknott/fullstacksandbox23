import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select

from core.types import Action, CurrentUserData, IdentityType
from models.access import AccessLogCreate, AccessPolicyCreate
from models.identity import (
    AzureGroup,
    AzureGroupCreate,
    AzureGroupRead,
    AzureGroupUpdate,
    AzureGroupUserLink,
    Group,
    GroupCreate,
    GroupRead,
    GroupUpdate,
    SubGroup,
    SubGroupCreate,
    SubGroupRead,
    SubGroupUpdate,
    SubSubGroup,
    SubSubGroupCreate,
    SubSubGroupRead,
    SubSubGroupUpdate,
    UeberGroup,
    UeberGroupCreate,
    UeberGroupRead,
    UeberGroupUpdate,
    User,
    Me,
    UserCreate,
    UserAccount,
    UserProfile,
    UserRead,
    UserUpdate,
)

# from .azure_group import AzureGroupCRUD
from .base import BaseCRUD


logger = logging.getLogger(__name__)


class AzureGroupCRUD(
    BaseCRUD[AzureGroup, AzureGroupCreate, AzureGroupRead, AzureGroupUpdate]
):
    def __init__(self):
        super().__init__(AzureGroup)

    # TBD: refactor into access control and just call self.create() with current_user!
    async def create_if_not_exists(
        self, azure_group_id: UUID, azure_tenant_id: UUID
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
                await self._write_identifier_type_link(database_group.id)
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
        super().__init__(User, allow_standalone=True)

    # def _add_identity_type_link_to_session(self, user_id: UUID):
    #     session = self.session
    #     identity_type_link = IdentityTypeLink(id=user_id, type=IdentityType.user)
    #     session.add(identity_type_link)
    #     # session.add(IdentityTypeLink(user_id, IdentityType.user))

    async def read_by_azure_user_id(
        self, azure_user_id: UUID, current_user: CurrentUserData
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
        azure_user_id: UUID,
        azure_tenant_id: UUID,
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
            else:
                access_log = AccessLogCreate(
                    resource_id=current_user.id,
                    action=Action.read,
                    identity_id=current_user.id,
                    status_code=200,
                )
                async with self.logging_CRUD as log_CRUD:
                    await log_CRUD.create(access_log)
                current_user_data = CurrentUserData(
                    user_id=current_user.id,
                    azure_token_roles=[],  # Roles are coming from the token - but this information is not available here!
                    azure_token_groups=groups,
                )
        except HTTPException as err:
            if err.status_code == 404 and err.detail == "User not found":
                # create user and groups:
                try:
                    user_create = UserCreate(
                        azure_user_id=azure_user_id,
                        azure_tenant_id=azure_tenant_id,
                    )
                    # print(
                    #     "=== user crud - create_azure_user_and_groups_if_not_exist - user_create ==="
                    # )
                    # print(user_create)
                    # The model-validation adds the default values (id) to the user_create object!
                    # Can be used for linked tables: avoids multiple round trips to database
                    database_user = User.model_validate(user_create)
                    await self._write_identifier_type_link(database_user.id)

                    # session.add(IdentityTypeLink(database_user.id, IdentityType.user))
                    session.add(database_user)
                    await session.commit()
                    await session.refresh(database_user)

                    # The settings in user account and user profile cannot be changed, before the user is created.
                    user_account = UserAccount(user_id=database_user.id)
                    user_profile = UserProfile(user_id=database_user.id)
                    # TBD: is the model_validate needed here right after creating the model?
                    # user_account = UserAccount.model_validate(user_account)
                    # user_profile = UserProfile.model_validate(user_profile)
                    await self._write_identifier_type_link(
                        user_account.id, IdentityType.user_account
                    )
                    await self._write_identifier_type_link(
                        user_profile.id, IdentityType.user_profile
                    )
                    # Commit again to save the user_account and user_profile:

                    session.add(user_account)
                    session.add(user_profile)
                    # session.add(database_user)
                    await session.commit()
                    await session.refresh(user_account)
                    await session.refresh(user_profile)

                    database_user.user_account_id = user_account.id
                    database_user.user_profile_id = user_profile.id
                    session.add(database_user)
                    await session.commit()
                    await session.refresh(database_user)

                    current_user = database_user
                    current_user_data = CurrentUserData(
                        user_id=current_user.id,
                        azure_token_roles=[],  # Roles are coming from the token - but this information is not available here!
                        azure_token_groups=groups,
                    )
                    # User is owner of itself:
                    access_policy = AccessPolicyCreate(
                        resource_id=database_user.id,
                        action=Action.own,
                        identity_id=current_user_data.user_id,
                    )
                    async with self.policy_CRUD as policy_CRUD:
                        await policy_CRUD.create(access_policy, current_user_data)

                    # await self._write_policy(
                    #     current_user.id, Action.own, current_user_data
                    # )
                    access_log = AccessLogCreate(
                        resource_id=current_user.id,
                        action=Action.own,
                        identity_id=current_user_data.user_id,
                        status_code=201,
                    )
                    async with self.logging_CRUD as log_CRUD:
                        await log_CRUD.create(access_log)
                    # await self._write_log(
                    #     current_user.id, Action.own, current_user_data, 201
                    # )
                    logger.info("USER created in database")
                except Exception as err:
                    access_log = AccessLogCreate(
                        resource_id=current_user.id,
                        action=Action.own,
                        identity_id=current_user_data.user_id,
                        status_code=404,
                    )
                    async with self.logging_CRUD as log_CRUD:
                        await log_CRUD.create(access_log)
                    # await self._write_log(
                    #     current_user.id, Action.own, current_user_data, 404
                    # )
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
            # TBD: remove after switching to the IdentityHierarchy table!
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
            # TBD: check if the group is already linked to the user!
            # User needs write access to the group to be able to add itself to the group:
            # print(
            #     "===  user crud - create_azure_user_and_groups_if_not_exist - current_user_data ==="
            # )
            # print(current_user_data)
            try:
                async with self.hierarchy_CRUD as hierarchy_CRUD:
                    await hierarchy_CRUD.read(
                        parent_id=azure_group_id,
                        child_id=current_user_data.user_id,
                        current_user=current_user_data,
                    )
            except Exception as err:
                async with self.policy_CRUD as policy_CRUD:
                    access_policy = AccessPolicyCreate(
                        resource_id=azure_group_id,
                        action=Action.write,  # needs write access to parent to add itself to the group -> BaseHierarchyCRUD.create()!
                        identity_id=current_user_data.user_id,
                    )
                    # TBD: fix this: what rights should a user have to a newly created group_group?
                    await policy_CRUD.create(access_policy, current_user_data)
                await self.add_child_to_parent(
                    parent_id=azure_group_id,
                    child_id=current_user_data.user_id,
                    current_user=current_user_data,
                    inherit=True,
                )
                logger.info(
                    f"USERCrud failed with {err}, so user got linked to group in database."
                )

        # print(
        #     "=== user crud - create_azure_user_and_groups_if_not_exist - current_user ==="
        # )
        # pprint(current_user)
        # print(
        #     "=== user crud - create_azure_user_and_groups_if_not_exist - current_user.azure_groups ==="
        # )
        # pprint(current_user.azure_groups)
        # # print(
        # #     "=== user crud - create_azure_user_and_groups_if_not_exist - current_user_data ==="
        # # )
        # # pprint(current_user_data)
        # print("=== user crud - create_azure_user_and_groups_if_not_exist - groups ===")
        # pprint(groups)
        # print("\n")

        # # remove hierarchy links for groups, that are no longer in the token:
        for linked_group in current_user.azure_groups:
            # print(
            #     "=== user crud - create_azure_user_and_groups_if_not_exist - linked_group.id ==="
            # )
            # pprint(linked_group.id)
            if str(linked_group.id) not in groups:
                async with self.hierarchy_CRUD as hierarchy_CRUD:
                    await hierarchy_CRUD.delete(
                        parent_id=linked_group.id,
                        child_id=current_user_data.user_id,
                        current_user=current_user_data,
                    )

        # read again after the relationship to the groups is created:
        # TBD: put this one back in - but now with the current_user parameter!
        # current_user = await self.read_by_azure_user_id(
        #     azure_user_id  # , update_last_access
        # )
        return current_user

    async def read_me(self, current_user: CurrentUserData) -> Me:
        """Returns the current user."""
        try:

            # This is for checking the access rights of the user to itself:
            # Version 1:
            # TBD fix cartesian product in the query when admin calls this!
            # problem started since the user_account was added to the user!
            # Challenge is in the model, not in the query!
            user = await self.read_by_id(current_user.user_id, current_user)

            # Version 2: check access first and then read directly from the database:
            # access_request = AccessRequest(
            #     current_user=current_user,
            #     resource_id=current_user.user_id,
            #     action=Action.own,
            # )
            # await self.policy_CRUD.allows(access_request)
            # user_query = (
            #     select(User).where(User.id == current_user.user_id)
            #     # .join(UserAccount, UserAccount.user_id == User.id)
            #     # .options(selectinload(User.user_account))
            # )
            # user_response = await self.session.exec(user_query)
            # user = user_response.unique().one()

            # me = Me.model_validate(user)
            # print("=== user crud - read_me - me ===")
            # print(me)
            query = (
                select(UserAccount, UserProfile).where(
                    UserAccount.user_id == current_user.user_id,
                    UserProfile.user_id == current_user.user_id,
                )
                # .options(selectinload(UserAccount))
            )
            response = await self.session.exec(query)
            account, profile = response.unique().one()
            user.user_account = account
            user.user_profile = profile

            # Add detailed logging before model_validate
            me = Me.model_validate(user)
            return me
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="User not found")

    async def update_me(self, current_user: CurrentUserData, new_me: Me) -> Me:
        """Updates the current user including user account and user profile."""
        try:
            # using self.update() also verifies the access rights of the user to itself:

            user_update = UserUpdate(
                **new_me.model_dump(
                    exclude={"user_account", "user_profile"}, exclude_unset=True
                )
            )

            user = await self.update(
                current_user,
                current_user.user_id,
                user_update,
            )
            statement = select(UserAccount).where(
                UserAccount.user_id == current_user.user_id
            )
            response = await self.session.exec(statement)
            current_account = response.unique().one()
            if current_account is None:
                logger.info(
                    f"User account for user_id {current_user.user_id} not found."
                )
                raise HTTPException(status_code=404, detail="User account not found")
            if new_me.user_account is not None:
                UserAccount.model_validate(new_me.user_account)
                updated_account = new_me.user_account.model_dump(exclude_unset=True)
                for key, value in updated_account.items():
                    setattr(current_account, key, value)
                self.session.add(current_account)

            statement = select(UserProfile).where(
                UserProfile.user_id == current_user.user_id
            )
            response = await self.session.exec(statement)
            current_profile = response.unique().one()
            if current_profile is None:
                logger.info(
                    f"User profile for user_id {current_user.user_id} not found."
                )
                raise HTTPException(status_code=404, detail="User profile not found")
            if new_me.user_profile is not None:
                UserProfile.model_validate(new_me.user_profile)
                updated_profile = new_me.user_profile.model_dump(exclude_unset=True)
                for key, value in updated_profile.items():
                    setattr(current_profile, key, value)
                self.session.add(current_profile)

            await self.session.commit()
            await self.session.refresh(current_account)
            await self.session.refresh(current_profile)
            user.user_account = current_account
            user.user_profile = current_profile
            me = Me.model_validate(user)
            access_log = AccessLogCreate(
                resource_id=current_user.user_id,
                action=Action.write,
                identity_id=current_user.user_id,
                status_code=200,
            )
            async with self.logging_CRUD as log_CRUD:
                await log_CRUD.create(access_log)
            return me
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="User not updated.")

    # Hose are not even used anywhere yet - so no priority to update them!
    # # TBD: Refactor into access control: just call self.update()
    # async def deactivate_user(self, azure_user_id: UUID) -> User:
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
    # async def activate_user(self, azure_user_id: UUID) -> User:
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
    # async def user_is_active(self, azure_user_id: UUID) -> bool:
    #     """Checks if a user is active."""
    #     session = self.session
    #     # async with session:
    #     existing_user = await session.get(User, azure_user_id)
    #     if not existing_user:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return existing_user.is_active


class UeberGroupCRUD(
    BaseCRUD[UeberGroup, UeberGroupCreate, UeberGroupRead, UeberGroupUpdate]
):
    def __init__(self):
        super().__init__(UeberGroup, allow_standalone=True)


class GroupCRUD(BaseCRUD[Group, GroupCreate, GroupRead, GroupUpdate]):
    def __init__(self):
        super().__init__(Group, allow_standalone=True)


class SubGroupCRUD(BaseCRUD[SubGroup, SubGroupCreate, SubGroupRead, SubGroupUpdate]):
    def __init__(self):
        super().__init__(SubGroup)


class SubSubGroupCRUD(
    BaseCRUD[SubSubGroup, SubSubGroupCreate, SubSubGroupRead, SubSubGroupUpdate]
):
    def __init__(self):
        super().__init__(SubSubGroup)
