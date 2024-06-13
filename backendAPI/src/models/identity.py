import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Uuid
from sqlmodel import Field, Relationship, SQLModel

from core.config import config
from models.access import IdentityHierarchy

# from .azure_group import AzureGroup, AzureGroupRead

# from .azure_group_user_link import AzureGroupUserLink


# region account linking


# region Azure Account


class AzureGroupUserLink(SQLModel, table=True):
    azure_group_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="azuregroup.id", primary_key=True
    )
    azure_user_id: Optional[uuid.UUID] = Field(
        default=None,
        # foreign_key="user.azure_user_id",
        # primary_key=True,
        # TBD: add ondelete="CASCADE" to avoid orphans - write tests for this!
        sa_column=Column(
            "uuid_data",
            Uuid,
            ForeignKey("user.azure_user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
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
        # link_model=AzureGroupUserLink,
        # sa_relationship_kwargs={"lazy": "selectin"},
        # # sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"},
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "AzureGroup.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
        },
    )

    # create the relationships and back population to users, courses... here!


class AzureGroupUpdate(AzureGroupCreate):
    """Schema for updating a group."""

    is_active: Optional[bool] = None


# endregion AzureGroup

# endregion account linking


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
    is_active: Optional[bool] = Field(default=True)

    ### Foreign account: Azure AD ###
    azure_user_id: Optional[uuid.UUID] = Field(index=True, unique=True)
    azure_groups: Optional[List["AzureGroup"]] = Relationship(
        back_populates="users",
        # link_model=AzureGroupUserLink,
        # # sa_relationship_kwargs={"lazy": "selectin"},
        # sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"},
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "AzureGroup.id == foreign(IdentityHierarchy.parent_id)",
            "cascade": "all, delete",
        },
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


# endregion User

# TBD: check if it makes sense to use relationships between groups and group-users;
# but consider the access filters_allowed!
# region UeberGroup


class UeberGroupCreate(SQLModel):
    """Schema for creating a user."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class UeberGroup(UeberGroupCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class UeberGroupRead(UeberGroupCreate):
    """Schema for reading a user."""

    id: uuid.UUID  # no longer optional - needs to exist now


# endregion SubGroup


# region Group


class GroupCreate(SQLModel):
    """Schema for creating a user."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class Group(GroupCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class GroupRead(GroupCreate):
    """Schema for reading a user."""

    id: uuid.UUID  # no longer optional - needs to exist now


# endregion Group


# region SubGroup


class SubGroupCreate(SQLModel):
    """Schema for creating a user."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class SubGroup(SubGroupCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class SubGroupRead(SubGroupCreate):
    """Schema for reading a user."""

    id: uuid.UUID  # no longer optional - needs to exist now


# endregion SubGroup


# region SubSubGroup


class SubSubGroupCreate(SQLModel):
    """Schema for creating a user."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class SubSubGroup(SubSubGroupCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class SubSubGroupRead(SubSubGroupCreate):
    """Schema for reading a user."""

    id: uuid.UUID  # no longer optional - needs to exist now


# endregion SubSubGroup
