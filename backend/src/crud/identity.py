import logging
from hashlib import sha256
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import config
from core.types import Action, CurrentUserData, IdentityType
from models.access import AccessLogCreate, AccessPolicyCreate, IdentifierTypeLink
from models.identity import (  # AzureGroupUserLink,
    AzureGroup,
    AzureGroupCreate,
    AzureGroupRead,
    AzureGroupUpdate,
    Group,
    GroupCreate,
    GroupRead,
    GroupUpdate,
    Me,
    MeUpdate,
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
    UserAccount,
    UserCreate,
    UserProfile,
    UserRead,
    UserUpdate,
)

# from .azure_group import AzureGroupCRUD
from .access import IdentityHierarchyCRUD
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
        session = self.session
        try:
            existing_group = await self.session.get(AzureGroup, azure_group_id)
            if existing_group is None:

                # TBD: refactor to use create from base class!
                group_create = AzureGroupCreate(
                    id=azure_group_id,
                    azure_tenant_id=azure_tenant_id,
                )
                # TBD: After refactoring into access control, the create method should cannot be used any more here.
                # group does not exist and there is no access policy for the group to create itself.
                # Do we need the current user here? Make sure not to run into a circular dependency!
                database_group = AzureGroup.model_validate(group_create)
                assert database_group.id is not None
                await self._write_identifier_type_link(database_group.id)
                session.add(database_group)
                await session.commit()
                await session.refresh(database_group)
                existing_group = database_group
            return AzureGroupRead.model_validate(existing_group)
        except Exception as err:
            await session.rollback()
            logging.error(err)
            raise HTTPException(status_code=404, detail="Group not found.")


class UserCRUD(BaseCRUD[User, UserCreate, UserRead, UserUpdate]):
    def __init__(self):
        super().__init__(User, allow_standalone=True)

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

    async def azure_user_self_sign_up(
        self, azure_user_id: UUID, azure_tenant_id: UUID, groups: Optional[List[str]]
    ) -> tuple[UserRead, int]:
        """Resolve a verified Microsoft identity and synchronize its Azure groups."""
        return await self._provider_sign_up(
            azure_user_id=UUID(str(azure_user_id)),
            azure_tenant_id=UUID(str(azure_tenant_id)),
            groups=[UUID(group) for group in (groups or [])],
        )

    async def linkedin_user_self_sign_up(
        self, linkedin_user_id: str
    ) -> tuple[UserRead, int]:
        """Resolve a verified LinkedIn subject without synchronizing Azure groups."""
        if not isinstance(linkedin_user_id, str) or not linkedin_user_id:
            raise HTTPException(status_code=401, detail="Invalid LinkedIn subject.")
        return await self._provider_sign_up(linkedin_user_id=linkedin_user_id)

    async def _provider_sign_up(
        self,
        *,
        azure_user_id: UUID | None = None,
        azure_tenant_id: UUID | None = None,
        linkedin_user_id: str | None = None,
        groups: list[UUID] | None = None,
    ) -> tuple[UserRead, int]:
        """Keep all signup writes atomic, including helpers that commit internally."""
        identity_key = (
            f"microsoft:{azure_user_id}"
            if azure_user_id
            else f"linkedin:{linkedin_user_id}"
        )
        lock_key = int.from_bytes(
            sha256(identity_key.encode()).digest()[:8], "big", signed=True
        )
        try:
            connection = await self.session.connection()
            await connection.execute(select(func.pg_advisory_xact_lock(lock_key)))
            # Helper commits release savepoints, never the owning transaction.
            async with AsyncSession(
                bind=connection,
                join_transaction_mode="create_savepoint",
                expire_on_commit=False,
            ) as session:
                worker = UserCRUD()
                worker.bind_session(session)
                user, status = await worker._initialize_provider_user(
                    azure_user_id, azure_tenant_id, linkedin_user_id
                )
                assert user.id is not None
                current_user_data = CurrentUserData(
                    user_id=user.id,
                    azure_token_roles=[],
                    azure_token_groups=groups or [],
                )
                if azure_user_id is not None:
                    assert azure_tenant_id is not None
                    await worker._sync_azure_groups(
                        user, current_user_data, azure_tenant_id, groups or []
                    )
                await session.refresh(user)
                result = UserRead.model_validate(user)
                await session.commit()
            await self.session.commit()
            return result, status
        except IntegrityError as err:
            await self.session.rollback()
            raise HTTPException(
                status_code=409, detail="Provider identity already exists."
            ) from err
        except BaseException:
            await self.session.rollback()
            raise

    async def _initialize_provider_user(
        self,
        azure_user_id: UUID | None,
        azure_tenant_id: UUID | None,
        linkedin_user_id: str | None,
    ) -> tuple[User, int]:
        session = self.session
        condition = (
            User.azure_user_id == azure_user_id
            if azure_user_id is not None
            else User.linkedin_user_id == linkedin_user_id
        )
        user = (await session.exec(select(User).where(condition))).unique().first()
        is_new = user is None
        pending_invitation = (
            user is not None
            and user.is_active is False
            and user.user_account_id is None
            and user.user_profile_id is None
        )
        if user is not None:
            if azure_user_id is not None and user.azure_tenant_id != azure_tenant_id:
                if not (pending_invitation and user.azure_tenant_id is None):
                    raise HTTPException(
                        status_code=401, detail="Microsoft tenant mismatch."
                    )
                user.azure_tenant_id = azure_tenant_id
            if not user.is_active and not pending_invitation:
                raise HTTPException(status_code=403, detail="User is disabled.")
        else:
            user = User(
                azure_user_id=azure_user_id,
                azure_tenant_id=azure_tenant_id,
                linkedin_user_id=linkedin_user_id,
                is_active=True,
            )
            assert user.id is not None
            session.add(IdentifierTypeLink(id=user.id, type=IdentityType.user))
            await session.flush()
        assert user.id is not None
        status = 201 if is_new or pending_invitation else 200
        if status == 201:
            user.is_active = True
            account = UserAccount(user_id=user.id)
            profile = UserProfile(user_id=user.id)
            assert account.id is not None
            assert profile.id is not None
            session.add(
                IdentifierTypeLink(id=account.id, type=IdentityType.user_account)
            )
            session.add(
                IdentifierTypeLink(id=profile.id, type=IdentityType.user_profile)
            )
            await session.flush()
            session.add(account)
            session.add(profile)
            await session.flush()
            user.user_account_id = account.id
            user.user_profile_id = profile.id
            session.add(user)
            await session.flush()
            if is_new:
                await self.policy_crud.create(
                    AccessPolicyCreate(
                        resource_id=user.id, identity_id=user.id, action=Action.own
                    ),
                    CurrentUserData(
                        user_id=user.id, azure_token_roles=[], azure_token_groups=[]
                    ),
                )
        await self.logging_crud.create(
            AccessLogCreate(
                resource_id=user.id,
                identity_id=user.id,
                action=Action.own if status == 201 else Action.read,
                status_code=status,
            )
        )
        return user, status

    async def _sync_azure_groups(
        self,
        current_user: User,
        current_user_data: CurrentUserData,
        azure_tenant_id: UUID,
        group_uuids: list[UUID],
    ) -> None:
        """Preserve existing Microsoft-only membership synchronization."""
        session = self.session
        await session.refresh(current_user, ["azure_groups"])
        for azure_group_id in group_uuids:
            # call group crud to check if group exists, if not create it!
            # TBD: refactor into using the access controlled protected methods:
            # Now the user actually exists and security can provide the CurrentUserData!
            # use current_user_data for this!
            # async with AzureGroupCRUD() as group_crud:
            group_crud = AzureGroupCRUD()
            group_crud.session = session
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
            # session = self.session

            # azure_user_group_link = await session.exec(
            #     select(AzureGroupUserLink).where(
            #         AzureGroupUserLink.azure_user_id == azure_user_id,
            #         AzureGroupUserLink.azure_group_id == azure_group_id,
            #     )
            # )
            # azure_user_group_link = azure_user_group_link.first()
            # # TBD: remove after switching to the IdentityHierarchy table!
            # if not azure_user_group_link:
            #     azure_user_group_link = AzureGroupUserLink(
            #         azure_user_id=azure_user_id,
            #         azure_group_id=azure_group_id,
            #     )
            #     session.add(azure_user_group_link)
            #     await session.commit()
            #     await session.refresh(azure_user_group_link)

            # TBD: check if the group is already linked to the user!
            # User needs write access to the group to be able to add itself to the group:
            user_group_link = []
            # async with self.hierarchy_CRUD as hierarchy_CRUD:
            hierarchy_CRUD = IdentityHierarchyCRUD(session=session)
            user_group_link = await hierarchy_CRUD.read_for_self_sync(
                parent_id=azure_group_id,
                child_id=current_user_data.user_id,
                current_user=current_user_data,
            )
            if not user_group_link:
                access_policy = AccessPolicyCreate(
                    resource_id=azure_group_id,
                    action=Action.write,  # needs write access to parent to add itself to the group -> BaseHierarchyCRUD.create()!
                    identity_id=current_user_data.user_id,
                )
                # TBD: fix this: what rights should a user have to a newly created group_group?
                await self.policy_crud.create(access_policy, current_user_data)
                await hierarchy_CRUD.create(
                    parent_id=azure_group_id,
                    child_id=current_user_data.user_id,
                    current_user=current_user_data,
                    inherit=True,
                )
                logger.info("User got linked to group in database.")

        # # remove hierarchy links for groups, that are no longer in the token:
        for linked_group in current_user.azure_groups or []:
            if linked_group.id is not None and linked_group.id not in group_uuids:
                hierarchy_CRUD = self.hierarchy_CRUD(session=session)
                await hierarchy_CRUD.delete(
                    parent_id=linked_group.id,
                    child_id=current_user_data.user_id,
                    current_user=current_user_data,
                )

    async def create_invited_azure_user(
        self,
        current_user: CurrentUserData,
        azure_user_id: UUID,
        azure_tenant_id: Optional[UUID] = None,
    ) -> UserRead:
        """Creates a new user with azure_user_id and azure_tenant_id - if it does not exist - and keeps that user disabled until that user signs in the first time."""

        try:
            user_create = User(
                azure_user_id=azure_user_id,
                azure_tenant_id=(
                    azure_tenant_id if azure_tenant_id else UUID(config.AZURE_TENANT_ID)
                ),
                is_active=False,
            )
            # The model-validation adds the default values (id) to the user_create object!
            # Can be used for linked tables: avoids multiple round trips to database
            database_user = User.model_validate(user_create)
            assert database_user.id is not None
            await self._write_identifier_type_link(database_user.id)

            self.session.add(database_user)
            await self.session.commit()
            await self.session.refresh(database_user)

            # The new user owns itself - not the user, that invites!
            access_policy = AccessPolicyCreate(
                resource_id=database_user.id,
                action=Action.own,
                identity_id=database_user.id,
            )
            await self.policy_crud.create(
                access_policy, current_user, allow_override=True
            )

            access_log = AccessLogCreate(
                resource_id=database_user.id,
                action=Action.write,  # Using a write and not a own, as the inviting user is not owning the invited user!
                identity_id=current_user.user_id,
                status_code=201,
            )
            await self.logging_crud.create(access_log)
        except Exception as err:
            await self.session.rollback()
            logging.error(err)
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead.model_validate(database_user)

    async def read_me(self, current_user: CurrentUserData) -> Me:
        """Returns the current user."""
        try:

            # This is for checking the access rights of the user to itself.
            # Returns model Me, which includes user_profile and user_account.
            # Always filters by current_user.user_id, so even Admin only ever gets
            # their own profile/account through this method.
            user = await self.read_by_id(current_user.user_id, current_user)

            me = Me.model_validate(user)
            me.azure_token_roles = current_user.azure_token_roles
            me.azure_token_groups = current_user.azure_token_groups
            return me
        except Exception as err:
            logging.error(err)
            raise HTTPException(status_code=404, detail="User not found")

    async def update_me(self, current_user: CurrentUserData, new_me: MeUpdate) -> Me:
        """Updates the current user including user account and user profile."""
        try:
            # using self.update() also verifies the access rights of the user to itself:

            if new_me.id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Forbidden.")
            user_update = UserUpdate(
                **new_me.model_dump(include={"is_active"}, exclude_unset=True)
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
                updated_account = new_me.user_account.model_dump(
                    exclude_unset=True, exclude_none=True
                )
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
                updated_profile = new_me.user_profile.model_dump(
                    exclude_unset=True, exclude_none=True
                )
                for key, value in updated_profile.items():
                    setattr(current_profile, key, value)
                self.session.add(current_profile)

            await self.session.commit()
            await self.session.refresh(current_account)
            await self.session.refresh(current_profile)
            user.user_account = current_account
            user.user_profile = current_profile
            me = Me.model_validate(user)
            me.azure_token_roles = current_user.azure_token_roles
            me.azure_token_groups = current_user.azure_token_groups
            access_log = AccessLogCreate(
                resource_id=current_user.user_id,
                action=Action.write,
                identity_id=current_user.user_id,
                status_code=200,
            )
            await self.logging_crud.create(access_log)
            return me
        except Exception as err:
            await self.session.rollback()
            logging.error(err)
            raise HTTPException(status_code=404, detail="User not updated.")

    async def delete(
        self,
        current_user: "CurrentUserData",
        object_id: UUID,
    ) -> None:
        """Deletes a user, user_account and user_profile."""
        user_id = object_id
        await super().delete(current_user, user_id)
        # Access control is handled in the super().delete() call above!
        delete_user_account = delete(UserAccount).where(
            col(UserAccount.user_id) == user_id,
        )
        await self.session.exec(delete_user_account)
        delete_user_profile = delete(UserProfile).where(
            col(UserProfile.user_id) == user_id,
        )
        await self.session.exec(delete_user_profile)
        await self.session.commit()


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
