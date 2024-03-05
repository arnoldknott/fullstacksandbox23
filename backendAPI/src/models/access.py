import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel
from core.types import IdentityType, ResourceType, Action


class AccessPolicy(SQLModel, table=True):
    """Table for access control"""

    identity_id: uuid.UUID = Field(primary_key=True)
    identity_type: "IdentityType" = Field(index=True)
    resource_id: uuid.UUID = Field(primary_key=True)
    resource_type: "ResourceType" = Field(index=True)
    action: "Action" = Field()
    # TBD: not sure if this is needed:
    # override: bool = Field(default=False)


class AccessLogging(SQLModel, table=True):
    """Table for logging actual access attempts"""

    identity_id: uuid.UUID = Field(primary_key=True)
    identity_type: "IdentityType" = Field(index=True)
    resource_id: uuid.UUID = Field(primary_key=True)
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
