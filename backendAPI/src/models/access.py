import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from core.types import IdentityType, ResourceType, Action


class AccessPolicyCreate(SQLModel):
    """Create model for access policies"""

    identity_id: uuid.UUID
    identity_type: "IdentityType"
    resource_id: int
    resource_type: "ResourceType"
    action: "Action"
    # TBD: not sure if this is needed:
    # override: bool = Field(default=False)


class AccessPolicy(AccessPolicyCreate, table=True):
    """Table for access control"""

    policy_id: Optional[int] = Field(default=None, primary_key=True)
    identity_id: uuid.UUID = Field(index=True)
    identity_type: "IdentityType" = Field(index=True)
    resource_id: int = Field(index=True)
    resource_type: "ResourceType" = Field(index=True)
    action: "Action" = Field()

    __table_args__ = (
        UniqueConstraint("identity_id", "resource_id", "resource_type", "action"),
    )
    # identity_id: uuid.UUID = Field(primary_key=True)
    # identity_type: "IdentityType" = Field(index=True)
    # resource_id: int = Field(primary_key=True)
    # resource_type: "ResourceType" = Field(index=True)
    # action: "Action" = Field()
    # override: bool = Field(default=False)


class AccessPolicyRead(AccessPolicyCreate):
    """Read model for access policies"""

    policy_id: int


# No update model for access policies: once created, they should not be updated, only deleted to keep loggings consistent.


class AccessLog(SQLModel, table=True):
    """Table for logging actual access attempts"""

    identity_id: uuid.UUID = Field(primary_key=True)
    identity_type: "IdentityType" = Field(index=True)
    resource_id: int = Field(primary_key=True)
    resource_type: "ResourceType" = Field(index=True)
    action: "Action" = Field()
    time: datetime = Field(default=datetime.now())
    status_code: int = Field()


class ResourceHierarchy(SQLModel, table=True):
    """Table for resource hierarchy"""

    parent_id: uuid.UUID = Field(primary_key=True)
    parent_type: "ResourceType" = Field(index=True)
    child_resource_id: uuid.UUID = Field(primary_key=True)
    child_type: "ResourceType" = Field(index=True)
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )
