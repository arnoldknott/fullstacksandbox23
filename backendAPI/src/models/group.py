import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from core.config import config
from sqlmodel import Field, Relationship, SQLModel

from .group_user_link import GroupUserLink

if TYPE_CHECKING:
    from .user import User


class GroupCreate(SQLModel):
    """Schema for creating a group."""

    is_active: bool = True
    azure_group_id: str
    # enables multi-tenancy, if None, then it's the internal tenant:
    azure_tenant_id: Optional[str] = config.AZURE_TENANT_ID


class Group(GroupCreate, table=True):
    """Schema for a group in the database."""

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    # last_updated_at: datetime = Field(default=datetime.now())# does not really make sense here

    users: Optional[List["User"]] = Relationship(
        back_populates="groups",
        link_model=GroupUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # create the relationships and back population to users, courses... here!


class GroupRead(GroupCreate):
    """Schema for reading a group."""

    id: uuid.UUID  # no longer optional - needs to exist now
    users: Optional[List["User"]] = []

    # add everything, that should be shown from the backpopulations here
    # but only what's realistically needed!


class GroupUpdate(GroupCreate):
    """Schema for updating a group."""

    is_active: Optional[bool] = None
