import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from pydantic import model_validator
from core.types import IdentityType, ResourceType, Action


class AccessPolicyCreate(SQLModel):
    """Create model for access policies"""

    identity_id: Optional[uuid.UUID] = None
    identity_type: Optional["IdentityType"] = None
    resource_id: uuid.UUID
    resource_type: "ResourceType"
    action: "Action"
    public: bool = Field(
        default=False,
        description="Set to true, if the resource is public and does not require any access control.",
    )

    @model_validator(mode="after")
    def either_identity_assignment_or_public(self):
        """Validates either identity is assigned or resource is public"""
        if self.public is True:
            if (self.identity_id is not None) or (self.identity_type is not None):
                raise ValueError("No identity can be assigned to a public resource.")
        else:
            if (self.identity_id is None) or (self.identity_type is None):
                raise ValueError(
                    "An identity must be assigned to a non-public resource."
                )
        return self

    # TBD: not sure if this is needed:
    # override: bool = Field(default=False)


class AccessPolicy(AccessPolicyCreate, table=True):
    """Table for access control"""

    policy_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    identity_id: Optional[uuid.UUID] = Field(
        default=None, index=True
    )  # needs to be a foreign key / relationship for join statements?
    identity_type: Optional["IdentityType"] = Field(default=None, index=True)
    resource_id: uuid.UUID = Field(index=True)
    resource_type: "ResourceType" = Field(index=True)
    action: "Action" = Field()

    __table_args__ = (
        UniqueConstraint("identity_id", "resource_id", "resource_type", "action"),
    )
    # identity_id: uuid.UUID = Field(primary_key=True)
    # identity_type: "IdentityType" = Field(index=True)
    # resource_id: uuid.UUID = Field(primary_key=True)
    # resource_type: "ResourceType" = Field(index=True)
    # action: "Action" = Field()
    # override: bool = Field(default=False)


class AccessPolicyRead(AccessPolicyCreate):
    """Read model for access policies"""

    policy_id: uuid.UUID


# No update model for access policies: once created, they should not be updated, only deleted to keep loggings consistent.


class AccessLogCreate(SQLModel):
    """Create model for access attempt logs"""

    identity_id: uuid.UUID
    identity_type: "IdentityType"
    resource_id: uuid.UUID
    resource_type: "ResourceType"
    action: "Action"
    status_code: int


class AccessLog(AccessLogCreate, table=True):
    """Table for logging actual access attempts"""

    access_attempt_id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    identity_id: uuid.UUID = Field(index=True)
    identity_type: "IdentityType" = Field(index=True)
    resource_id: uuid.UUID = Field(primary_key=True)
    resource_type: "ResourceType" = Field(index=True)
    action: "Action" = Field()
    time: datetime = Field(default=datetime.now())
    status_code: int = Field()


class AccessLogRead(AccessLogCreate):
    """Read model access attempt logs"""

    access_attempt_id: uuid.UUID


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
