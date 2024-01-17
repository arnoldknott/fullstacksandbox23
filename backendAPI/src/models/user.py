import uuid
from datetime import datetime
from typing import List, Optional

from core.config import config
from sqlmodel import Field, Relationship, SQLModel

from .group import Group, GroupRead
from .group_user_link import GroupUserLink


class UserCreate(SQLModel):
    """Schema for creating a user."""

    # should be unnecessary now, ad this information is the access token via groups and roles:
    # is_active: bool = True
    # is_admin: bool = False
    azure_user_id: str
    # enables multi-tenancy, if None, then it's the internal tenant:
    azure_tenant_id: Optional[str] = config.AZURE_TENANT_ID


class User(UserCreate, table=True):
    """Schema for a user in the database."""

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    # TBD: add "last_access_at" here

    # create the relationships and back population to groups, topics,... here!
    groups: Optional[List["Group"]] = Relationship(
        back_populates="users",
        link_model=GroupUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # Linking DTU Learn and other accounts to user:
    # brightspace_account: Optional["BrightspaceAccount"] = Relationship(
    #     back_populates="user"
    # )
    # google_account: Optional["GoogleAccount"] = Relationship(back_populates="user")
    # discord_account: Optional["DiscordAccount"] = Relationship(back_populates="user")


class UserRead(UserCreate):
    """Schema for reading a user."""

    id: uuid.UUID  # no longer optional - needs to exist now

    # add everything, that should be shown from the backpopulations here
    # but only what's realistically needed!
    groups: Optional[List["GroupRead"]] = []
    # brightspace_account: Optional["DiscordAccount"] = None
    # google_account: Optional["GoogleAccount"] = None
    # discord_account: Optional["DiscordAccount"] = None


class UserUpdate(UserCreate):
    """Schema for updating a user."""

    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

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
    user: Optional["User"] = Relationship(back_populates="brightspace_account")


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
