import uuid
from datetime import datetime
from typing import List, Optional

from core.config import config
from sqlmodel import Field, Relationship, SQLModel

from .azure_group import AzureGroup, AzureGroupRead
from .azure_group_user_link import AzureGroupUserLink


class UserCreate(SQLModel):
    """Schema for creating a user."""

    azure_user_id: Optional[uuid.UUID]
    # # enables multi-tenancy, if None, then it's the internal tenant:
    azure_tenant_id: Optional[uuid.UUID] = config.AZURE_TENANT_ID
    is_active: bool = True


class User(UserCreate, table=True):
    """Schema for a user in the database."""

    # dropping id for now - this is just too confusing during early stages and not needed
    # if other sources than Azure AD are used, then this potentially needs to be re-added
    # careful when doing that - take production database offline first!
    user_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # azure_user_id: uuid.UUID = Field(index=True, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    is_active: Optional[bool] = Field(default=True)
    # TBD: add "last_access_at" here?
    # don't add Roles as they are coming in from the access token:
    # single source of truth and now legacy data floating
    # configure group membership in Azure Portal under Enterprise Applications instead.

    ### Foreign account: Azure AD ###
    azure_user_id: Optional[uuid.UUID] = Field(index=True, unique=True)
    # linking to azure_user - one-to-one relationship:
    # azure_user: Optional["AzureUser"] = Relationship(back_populates="user")

    # create the relationships and back population to groups, topics,... here!
    azure_groups: Optional[List["AzureGroup"]] = Relationship(
        back_populates="users",
        link_model=AzureGroupUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    ### Foreign Account: DTU Learn (Brightspace) ###
    # only add the user-id here - nothing else!
    # Linking DTU Learn and other accounts to user:
    # brightspace_account: Optional["BrightspaceAccount"] = Relationship(
    #     back_populates="user"
    # )

    ### Foreign Account Google ###
    # google_account: Optional["GoogleAccount"] = Relationship(back_populates="user")

    ### Foreign Account Discord ###
    # discord_account: Optional["DiscordAccount"] = Relationship(back_populates="user")


class UserRead(UserCreate):
    """Schema for reading a user."""

    # azure_user_id: uuid.UUID
    user_id: uuid.UUID  # no longer optional - needs to exist now

    # add everything, that should be shown from the backpopulations here
    # but only what's realistically needed!
    # groups: Optional[List["GroupRead"]] = []
    created_at: datetime
    azure_groups: Optional[List["AzureGroupRead"]] = []
    # brightspace_account: Optional["DiscordAccount"] = None
    # google_account: Optional["GoogleAccount"] = None
    # discord_account: Optional["DiscordAccount"] = None


class UserUpdate(UserCreate):
    """Schema for updating a user."""

    is_active: Optional[bool] = None
    # is_admin: Optional[bool] = None

    # class BrightspaceAccount(SQLModel, table=True):
    #     """Schema for a linking a brightspace (DTU Learn) account to the database."""

    #     # calling "d2l/api/lp/{{lp_version}}/users/whoami" returns the user_id as a "Identifier"
    #     user_id: int = Field(primary_key=True)
    #     # calling "d2l/api/lp/{{lp_version}}/users/whoami" returns the profileIdentifier as a "ProfileIdentifier"
    #     profile_identifier: str
    #     # calling "d2l/api/lp/{{lp_version}}/users/{{user_id}}",
    #     # where user_id is the identifier from whoAmI, returns the following
    #     # also the orgId and the orgDefinedId are the user
    #     org_id: int
    #     org_defined_id: int

    # ideally store the tokens in the cache!
    # access_token: str
    # refresh_token: str
    # user: Optional["User"] = Relationship(back_populates="brightspace_account")


# class AzureUserCreate(SQLModel):
#     """Schema for creating a user."""

#     azure_user_id: uuid.UUID
#     # # enables multi-tenancy, if None, then it's the internal tenant:
#     azure_tenant_id: Optional[uuid.UUID] = config.AZURE_TENANT_ID
#     # TBD: do I need the link to the user here?


# class AzureUser(AzureUserCreate, table=True):
#     """Schema for a linking an Azure account to the database."""

#     azure_user_id: uuid.UUID = Field(index=True, primary_key=True)
#     azure_groups: Optional[List["AzureGroup"]] = Relationship(
#         back_populates="users",
#         link_model=AzureGroupUserLink,
#         sa_relationship_kwargs={"lazy": "selectin"},
#     )

#     user_id: uuid.UUID = Field(index=True)
#     user: "User" = Relationship(back_populates="azure_user")


# class AzureUserRead(AzureUser):
#     pass


# class AzureUserUpdate(AzureUserCreate):
#     pass


# class GoogleAccount(SQLModel, table=True):
#     account_id: int = Field(primary_key=True)
#     # ideally store the tokens in the cache!
#     # access_token: str
#     # refresh_token: str
#     user: Optional["User"] = Relationship(back_populates="google_account")


# class DiscordAccount(SQLModel, table=True):
#     account_id: int = Field(primary_key=True)
#     # ideally store the tokens in the cache!
#     # access_token: str
#     # refresh_token: str
#     user: Optional["User"] = Relationship(back_populates="discord_account")
