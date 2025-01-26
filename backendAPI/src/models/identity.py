import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Uuid
from sqlmodel import Field, Relationship, SQLModel

# from core.types import AppRoles
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
    # Could be an option in future to implement roles for the app:
    # app_roles: Optional[List[AppRoles]] = None
    is_active: bool = True


class User(UserCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    is_active: Optional[bool] = Field(default=True)

    # ### User Account ###
    user_account_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="useraccount.id"
    )
    user_account: Optional["UserAccount"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    # user_account_id: Optional[uuid.UUID] = Field(
    #     foreign_key="useraccount.id",
    # )
    # user_account: Optional["UserAccount"] = Relationship(
    #     back_populates="user",
    #     # sa_relationship_kwargs={"single_parent": True},
    #     # cascade_delete=True,
    #     sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    # )

    # ### User Profile ###
    # user_profile: Optional["UserProfile"] = Relationship(
    #     back_populates="user",
    #     # cascade_delete=True,
    #     sa_relationship_kwargs={"single_parent": True},
    # )

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
            # "lazy": "noload",
            "viewonly": True,
            "primaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "AzureGroup.id == foreign(IdentityHierarchy.parent_id)",
            "cascade": "all, delete",
        },
    )
    ueber_groups: Optional[List["UeberGroup"]] = Relationship(
        back_populates="users",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            # "lazy": "joined",
            "lazy": "noload",
            "viewonly": True,
            "primaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "UeberGroup.id == foreign(IdentityHierarchy.parent_id)",
        },
    )
    groups: Optional[List["Group"]] = Relationship(
        back_populates="users",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            # "lazy": "joined",
            "lazy": "noload",
            "viewonly": True,
            "primaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "Group.id == foreign(IdentityHierarchy.parent_id)",
        },
    )
    sub_groups: Optional[List["SubGroup"]] = Relationship(
        back_populates="users",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            # "lazy": "joined",
            "lazy": "noload",
            "viewonly": True,
            "primaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "SubGroup.id == foreign(IdentityHierarchy.parent_id)",
        },
    )
    sub_sub_groups: Optional[List["SubSubGroup"]] = Relationship(
        back_populates="users",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            # "lazy": "joined",
            "lazy": "noload",
            "viewonly": True,
            "primaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "SubSubGroup.id == foreign(IdentityHierarchy.parent_id)",
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


class UserAccount(SQLModel, table=True):
    # id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # id: Optional[uuid.UUID] = Field(
    #     default=None, foreign_key="identifiertypelink.id", primary_key=True
    # )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None, index=True
    )  # This is manually set from identity crud at self-sign-up!
    user: User = Relationship(
        back_populates="user_account",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    is_publicAIuser: bool = False


# class UserAccount(SQLModel, table=True):
#     """Schema for a user account in the database."""

#     id: Optional[uuid.UUID] = Field(
#         default_factory=uuid.uuid4,
#         foreign_key="identifiertypelink.id",
#         primary_key=True,
#     )
#     user_id: Optional[uuid.UUID] = Field(foreign_key="user.id", index=True)
#     user: List["User"] = Relationship(
#         back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
#     )

#     # id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
#     # user_id: Optional[uuid.UUID] = Field(
#     #     Column(
#     #         sa_relationship_kwargs={
#     #             "foreign_keys": "[user.id], [identifiertypelink.id]"
#     #         },
#     #         index=True,
#     #     )
#     # )
#     # user: Optional["User"] = Relationship(
#     #     back_populates="user_account",
#     #     # cascade_delete=True,
#     #     sa_relationship_kwargs={"single_parent": True},
#     # )

#     # Controls user enabled features, account linking and so on in the app.
#     is_publicAIuser: bool = False


# class ThemeVariants(str, Enum):
#     """Material Design 3 theme variants."""

#     # monochrome = "Monochrome"
#     neutral = "Neutral"
#     tonal_spot = "Tonal Spot"
#     vibrant = "Vibrant"
#     # expressive = "Expressive"
#     fidelity = "Fidelity"
#     content = "Content"
#     rainbow = "Rainbow"
#     # fruit_salad = "Fruit Salad"


# class UserProfile(SQLModel, table=True):
#     """Schema for a user profile in the database."""

#     # Theme settings, language settings, notification settings,
#     # potentially: view history, saved resources, personalized quick links, ...

#     id: Optional[uuid.UUID] = Field(
#         foreign_key="user.id",
#         primary_key=True,
#     )
#     user: Optional["User"] = Relationship(
#         back_populates="user_profile",
#         cascade_delete=True,
#     )

#     theme_color: str = "#353c6e"
#     theme_variant: ThemeVariants = ThemeVariants.tonal_spot
#     contrast: float = 0.0

#     @model_validator(mode="after")
#     def validate_theme_color(self):
#         if not self.theme_color.startswith("#"):
#             raise ValueError("Theme color must start with '#'.")
#         if len(self.theme_color) != 7:
#             raise ValueError("Theme color must be 7 characters long.")
#         if not all(c in "0123456789abcdef" for c in self.theme_color[1:]):
#             raise ValueError("Theme color must be a valid hex color.")

#     @model_validator(mode="after")
#     def validate_contrast(self):
#         if self.contrast <= -1.0 or self.contrast >= 1.0:
#             raise ValueError("Contrast must be between -1.0 and 1.0.")


# Note: this is one of the models, that other users can see about a user.
class UserReadNoGroups(UserCreate):
    """Schema for reading a user without linked accounts and groups."""

    # This is what other users can see about a user - without groups.

    id: uuid.UUID
    azure_user_id: Optional[uuid.UUID] = None
    azure_groups: Optional[List["AzureGroupRead"]] = None


# Note: this the other model, that other users can see about a user.
class UserRead(UserCreate):
    """Schema for reading a user."""

    # This is what other users can see about a user - including groups.

    id: uuid.UUID  # no longer optional - needs to exist now

    # created_at: datetime
    # last_accessed_at: datetime
    azure_groups: Optional[List["AzureGroupRead"]] = None
    # brightspace_account: Optional["DiscordAccount"] = None
    # google_account: Optional["GoogleAccount"] = None
    # discord_account: Optional["DiscordAccount"] = None
    ueber_groups: Optional[List["UeberGroupRead"]] = None
    groups: Optional[List["GroupRead"]] = None
    sub_groups: Optional[List["SubGroupRead"]] = None
    sub_sub_groups: Optional[List["SubSubGroupRead"]] = None


# This is the model, a users can see about themselves.
class Me(UserRead):
    azure_token_roles: Optional[list[str]] = None
    azure_token_groups: Optional[list[uuid.UUID]] = None
    # user_account_id: Optional[uuid.UUID] = None
    user_account: Optional["UserAccount"] = None
    # user_profile: Optional["UserProfile"] = None


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
    """Schema for creating an ueber-group."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class UeberGroup(UeberGroupCreate, table=True):
    """Schema for an ueber-group in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    users: Optional[List["User"]] = Relationship(
        back_populates="ueber_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "UeberGroup.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
        },
    )
    groups: Optional[List["Group"]] = Relationship(
        back_populates="ueber_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "UeberGroup.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "Group.id == foreign(IdentityHierarchy.child_id)",
        },
    )


class UeberGroupRead(UeberGroupCreate):
    """Schema for reading an ueber-group."""

    id: uuid.UUID  # no longer optional - needs to exist now
    users: Optional[List["User"]] = None
    groups: Optional[List["Group"]] = None


class UeberGroupUpdate(UeberGroupCreate):
    """Schema for updating an ueber-group."""

    name: Optional[str] = None


# endregion SubGroup


# region Group


class GroupCreate(SQLModel):
    """Schema for creating a group."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class Group(GroupCreate, table=True):
    """Schema for a group in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    users: Optional[List["User"]] = Relationship(
        back_populates="groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "Group.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
        },
    )
    ueber_groups: Optional[List["UeberGroup"]] = Relationship(
        back_populates="groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "Group.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "UeberGroup.id == foreign(IdentityHierarchy.parent_id)",
        },
    )
    sub_groups: Optional[List["SubGroup"]] = Relationship(
        back_populates="groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "Group.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "SubGroup.id == foreign(IdentityHierarchy.child_id)",
        },
    )


class GroupRead(GroupCreate):
    """Schema for reading a group."""

    id: uuid.UUID  # no longer optional - needs to exist now
    users: Optional[List["User"]] = None
    sub_groups: Optional[List["SubGroup"]] = None


class GroupUpdate(GroupCreate):
    """Schema for updating a group."""

    name: Optional[str] = None


# endregion Group


# region SubGroup


class SubGroupCreate(SQLModel):
    """Schema for creating a sub-group."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class SubGroup(SubGroupCreate, table=True):
    """Schema for a sub-group in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    users: Optional[List["User"]] = Relationship(
        back_populates="sub_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "SubGroup.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
        },
    )
    groups: Optional[List["Group"]] = Relationship(
        back_populates="sub_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "SubGroup.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "Group.id == foreign(IdentityHierarchy.parent_id)",
        },
    )
    sub_sub_groups: Optional[List["SubSubGroup"]] = Relationship(
        back_populates="sub_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "SubGroup.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "SubSubGroup.id == foreign(IdentityHierarchy.child_id)",
        },
    )


class SubGroupRead(SubGroupCreate):
    """Schema for reading a sub-group."""

    id: uuid.UUID  # no longer optional - needs to exist now
    users: Optional[List["User"]] = None
    sub_sub_groups: Optional[List["SubSubGroup"]] = None


class SubGroupUpdate(SubGroupCreate):
    """Schema for updating a sub-group."""

    name: Optional[str] = None


# endregion SubGroup


# region SubSubGroup


class SubSubGroupCreate(SQLModel):
    """Schema for creating a sub-sub-group."""

    name: str = Field(..., max_length=150, regex="^[a-zA-Z0-9]*$", index=True)
    description: Optional[str] = Field(None, max_length=500)


class SubSubGroup(SubSubGroupCreate, table=True):
    """Schema for a sub-sub-group in the database."""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    users: Optional[List["User"]] = Relationship(
        back_populates="sub_sub_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "SubSubGroup.id == foreign(IdentityHierarchy.parent_id)",
            "secondaryjoin": "User.id == foreign(IdentityHierarchy.child_id)",
        },
    )
    sub_groups: Optional["SubGroup"] = Relationship(
        back_populates="sub_sub_groups",
        link_model=IdentityHierarchy,
        sa_relationship_kwargs={
            "lazy": "joined",
            "viewonly": True,
            "primaryjoin": "SubSubGroup.id == foreign(IdentityHierarchy.child_id)",
            "secondaryjoin": "SubGroup.id == foreign(IdentityHierarchy.parent_id)",
        },
    )


class SubSubGroupRead(SubSubGroupCreate):
    """Schema for reading a sub-sub-group."""

    id: uuid.UUID  # no longer optional - needs to exist now
    users: Optional[List["User"]] = None


class SubSubGroupUpdate(SubSubGroupCreate):
    """Schema for updating a sub-sub-group."""

    name: Optional[str] = None


# endregion SubSubGroup
