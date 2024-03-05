import uuid
from datetime import datetime
from tyuping import Union

from sqlmodel import Field, SQLModel
from core.types import IdentityType, ResourceType, Action


class AccessControl(SQLModel, table=True):
    """Table for access control"""

    identity_id: uuid.UUID = Field(primary_key=True)
    identity_type: "IdentityType" = Field(index=True)
    resource_id: uuid.UUID = Field(primary_key=True)
    resource_type: "ResourceType" = Field(index=True)
    action: "Action" = Field()
    override: bool = Field(default=False)


class AccessLog(AccessControl, table=True):
    """Table for logging actual access attempts"""

    time: datetime = Field(default=datetime.now())
    status_code: Union[int, bool] = Field()


class ResourceHierarchy(SQLModel, table=True):
    """Table for resource hierarchy"""

    parent_id: uuid.UUID = Field(primary_key=True)
    parent_type: "ResourceType" = Field(index=True)
    child_resource_id: uuid.UUID = Field(primary_key=True)
    child_type: "ResourceType" = Field(index=True)
    inherit: bool = Field(default=False)
