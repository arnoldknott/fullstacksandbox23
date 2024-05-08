import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from core.config import config
from core.types import IdentityType

# from .azure_group import AzureGroup, AzureGroupRead

# from .azure_group_user_link import AzureGroupUserLink


# region account linking


# region Azure Account


class AzureGroupUserLink(SQLModel, table=True):
    azure_group_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="azuregroup.id", primary_key=True
    )
    azure_user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.azure_user_id", primary_key=True
    )


class AzureGroupCreate(SQLModel):
    """Schema for creating a group."""

    id: uuid.UUID
    # enables multi-tenancy, if None, then it's the internal tenant:
    azure_tenant_id: Optional[uuid.UUID] = config.AZURE_TENANT_ID
    is_active: bool = True


class AzureGroupRead(AzureGroupCreate):
    """Schema for reading a group."""

    id: uuid.UUID
    # id: uuid.UUID  # no longer optional - needs to exist now
    azure_users: Optional[List["User"]] = []

    # add everything, that should be shown from the backpopulations here
    # but only what's realistically needed!


class AzureGroup(AzureGroupCreate, table=True):
    """Schema for a group in the database."""

    # dropping id for now - this is just too confusing during early stages and not needed
    # if other sources than Azure AD are used, then this potentially needs to be re-added
    # careful when doing that - take production database offline first!
    #  id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    id: uuid.UUID = Field(
        index=True,
        primary_key=True,
        foreign_key="identifiertypelink.id",
        description="Identical to the uuid for this group from Azure.",
    )
    created_at: datetime = Field(default=datetime.now())
    is_active: Optional[bool] = Field(default=True)
    # last_updated_at: datetime = Field(default=datetime.now())# does not really make sense here

    users: Optional[List["User"]] = Relationship(
        back_populates="azure_groups",
        link_model=AzureGroupUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # create the relationships and back population to users, courses... here!


class AzureGroupUpdate(AzureGroupCreate):
    """Schema for updating a group."""

    is_active: Optional[bool] = None


# endregion


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


# region Identity Hierarchy


class IdentityHierarchy(SQLModel, table=True):
    """Schema for the identity hierarchy in the database."""

    child_id: uuid.UUID = Field(primary_key=True)
    child_type: IdentityType = Field(index=True)
    parent_id: uuid.UUID = Field(primary_key=True)
    parent_type: IdentityType = Field(index=True)


# endregion


# region User


class UserCreate(SQLModel):
    """Schema for creating a user."""

    azure_user_id: Optional[uuid.UUID] = None
    # # enables multi-tenancy, if None, then it's the internal tenant:
    azure_tenant_id: Optional[uuid.UUID] = config.AZURE_TENANT_ID
    # last_accessed_at: Optional[datetime] = datetime.now()
    is_active: bool = True


class User(UserCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    # created_at: datetime = Field(default=datetime.now())
    # TBD: change last_accessed_at to non-optional after migration.
    # last_accessed_at: Optional[datetime] = Field(default=datetime.now())
    # TBD: moce the last_updated_at and last_accessed_at to a resource access log table
    # last_accessed_at: datetime = Field(default=datetime.now())
    is_active: Optional[bool] = Field(default=True)

    ### Foreign account: Azure AD ###
    azure_user_id: Optional[uuid.UUID] = Field(index=True, unique=True)
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

    id: uuid.UUID  # no longer optional - needs to exist now

    # created_at: datetime
    # last_accessed_at: datetime
    azure_groups: Optional[List["AzureGroupRead"]] = None
    # brightspace_account: Optional["DiscordAccount"] = None
    # google_account: Optional["GoogleAccount"] = None
    # discord_account: Optional["DiscordAccount"] = None


class UserUpdate(UserCreate):
    """Schema for updating a user."""

    is_active: Optional[bool] = None

    # TBD: this is one-to-one relationship, so it's not an extra table. Add to user instead for reduced complexity.
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


# endregion
