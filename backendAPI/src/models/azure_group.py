import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from core.config import config
from sqlmodel import Field, Relationship, SQLModel

from .azure_group_user_link import AzureGroupUserLink

if TYPE_CHECKING:
    from .user import User


class AzureGroupCreate(SQLModel):
    """Schema for creating a group."""

    azure_group_id: uuid.UUID
    # enables multi-tenancy, if None, then it's the internal tenant:
    azure_tenant_id: Optional[uuid.UUID] = config.AZURE_TENANT_ID
    is_active: bool = True


class AzureGroup(AzureGroupCreate, table=True):
    """Schema for a group in the database."""

    # dropping id for now - this is just too confusing during early stages and not needed
    # if other sources than Azure AD are used, then this potentially needs to be re-added
    # careful when doing that - take production database offline first!
    #  id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    azure_group_id: uuid.UUID = Field(index=True, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    is_active: Optional[bool] = Field(default=True)
    # last_updated_at: datetime = Field(default=datetime.now())# does not really make sense here

    users: Optional[List["User"]] = Relationship(
        back_populates="azure_groups",
        link_model=AzureGroupUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # create the relationships and back population to users, courses... here!


class AzureGroupRead(AzureGroupCreate):
    """Schema for reading a group."""

    azure_group_id: uuid.UUID
    # id: uuid.UUID  # no longer optional - needs to exist now
    azure_users: Optional[List["User"]] = []

    # add everything, that should be shown from the backpopulations here
    # but only what's realistically needed!


class AzureGroupUpdate(AzureGroupCreate):
    """Schema for updating a group."""

    is_active: Optional[bool] = None
