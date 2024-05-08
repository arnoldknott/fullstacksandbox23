import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator  # , create_model
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

# if TYPE_CHECKING:
from core.types import Action, CurrentUserData, IdentityType, ResourceType


class IdentifierTypeLink(SQLModel, table=True):
    """Model for resource types"""

    id: uuid.UUID = Field(primary_key=True)
    # type: Union[ResourceType, IdentityType] = Field(index=True)
    # type: BaseType = Field(
    #     sa_column=Column(Union(Enum(IdentityType), Enum(ResourceType)))
    # )
    type: str = Field(index=True)

    # TBD: is there another way to define the type of the column?
    @model_validator(mode="after")
    def validate_type(self):
        if (self.type not in IdentityType.list()) and (
            self.type not in ResourceType.list()
        ):
            raise ValueError("Invalid type")
        return self


# class ResourceTypeLink(SQLModel, table=True):
#     """Model for resource types"""

#     id: uuid.UUID = Field(primary_key=True)
#     # type: Union[ResourceType, IdentityType] = Field(index=True)
#     # type: BaseType = Field(
#     #     sa_column=Column(Union(Enum(IdentityType), Enum(ResourceType)))
#     # )
#     type: ResourceType = Field(index=True)

#     # TBD: is there another way to define the type of the column?
#     # @model_validator(mode="after")
#     # def validate_type(self):
#     #     if self.type not in ResourceType.list():
#     #         raise ValueError("Invalid Resource type")
#     #     return self


# class IdentityTypeLink(SQLModel, table=True):
#     """Model for identity types"""

#     id: uuid.UUID = Field(primary_key=True)
#     type: IdentityType = Field(index=True)


class AccessPolicyCreate(SQLModel):
    """Create model for access policies"""

    identity_id: Optional[uuid.UUID] = None
    resource_id: uuid.UUID
    action: Action
    public: bool = Field(
        default=False,
        description="Set to true, if the resource is public and does not require any access control.",
    )

    @model_validator(mode="after")
    def either_identity_assignment_or_public(self):
        """Validates either identity is assigned or resource is public"""
        if self.public is True:
            if self.identity_id is not None:
                raise ValueError("No identity can be assigned to a public resource.")
        else:
            if self.identity_id is None:
                raise ValueError(
                    "An identity must be assigned to a non-public resource."
                )
        return self


class AccessPolicy(AccessPolicyCreate, table=True):
    """Table for access control"""

    id: Optional[int] = Field(default=None, primary_key=True)
    identity_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="identifiertypelink.id", index=True
    )
    resource_id: uuid.UUID = Field(foreign_key="identifiertypelink.id", index=True)
    action: "Action" = Field()

    __table_args__ = (UniqueConstraint("identity_id", "resource_id", "action"),)


class AccessPolicyUpdate(AccessPolicyCreate):
    """Update model for access policies"""

    new_action: Action


class AccessPolicyRead(AccessPolicyCreate):
    """Read model for access policies"""

    id: int


class AccessPolicyDelete(SQLModel):
    """Delete model for access policies"""

    identity_id: Optional[uuid.UUID] = None
    resource_id: Optional[uuid.UUID] = None
    action: Optional[Action] = None
    public: Optional[bool] = None

    @model_validator(mode="after")
    def if_public_resource_id_required(self):
        """Validates either identity is assigned or resource is public"""
        if self.public is True and self.resource_id is None:
            raise ValueError("Only one public resource can be deleted at a time.")
        return self

    @model_validator(mode="after")
    def either_resource_id_or_identity_id_required(self):
        """Validates either identity is assigned or resource is public"""
        if self.resource_id is None and self.identity_id is None:
            raise ValueError(
                "Either resource_id or identity_id required when deleting policies."
            )
        return self


class AccessRequest(BaseModel):
    """Model for the access request"""

    # for admin access resource_id and action can be None!
    current_user: CurrentUserData
    resource_id: Optional[uuid.UUID]
    action: Optional[Action]


# No update model for access policies: once created, they should not be updated, only deleted to keep loggings consistent.

# Maybe the logs should just be derived from the AccessRequests and add the status code?


class AccessLogCreate(SQLModel):
    """Create model for access attempt logs"""

    identity_id: Optional[uuid.UUID] = None
    resource_id: uuid.UUID
    action: Action
    status_code: int


class AccessLog(AccessLogCreate, table=True):
    """Table for logging actual access attempts"""

    id: Optional[int] = Field(default=None, primary_key=True)
    # id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # identity_id: Optional[uuid.UUID] = Field(default=None, index=True)
    identity_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="identifiertypelink.id", index=True
    )
    resource_id: uuid.UUID = Field(foreign_key="identifiertypelink.id", index=True)
    action: "Action" = Field(index=True)
    time: datetime = Field(default_factory=datetime.now, index=True)
    status_code: int = Field()


class AccessLogRead(AccessLogCreate):
    """Read model access attempt logs"""

    id: int
    time: datetime


class ResourceHierarchyCreate(SQLModel):
    """Create model for resource hierarchy"""

    parent_id: uuid.UUID
    child_id: uuid.UUID
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )

    @model_validator(mode="after")
    def either_inherit_or_not(self):
        """Validates either inherit is set or not"""
        if self.parent_id == self.child_resource_id:
            raise ValueError("A resource cannot be its own child.")
        return self


class ResourceHierarchy(SQLModel, table=True):
    """Table for resource hierarchy"""

    parent_id: uuid.UUID = Field(primary_key=True)
    child_id: uuid.UUID = Field(primary_key=True)
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )

    __table_args__ = (UniqueConstraint("parent_id", "child_id"),)


class ResourceHierarchyRead(ResourceHierarchyCreate):
    """Read model for resource hierarchy"""

    pass
