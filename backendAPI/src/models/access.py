import uuid
from datetime import datetime
from typing import ClassVar, List, Optional

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


# region Access


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


# endregion Access


# region hierarchies


class BaseHierarchy:
    """Class to define the hierarchy of the entities"""

    relations: ClassVar = {}

    @classmethod
    def get_allowed_children_types(cls, entity_type: str) -> List[str]:
        return cls.relations.get(entity_type, [])


class ResourceHierarchyCreate(SQLModel):
    """Create model for resource hierarchy"""

    parent_id: uuid.UUID
    child_id: uuid.UUID
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )

    @model_validator(mode="after")
    def not_child_to_self(self):
        """Validates that the parent is not child to itself"""
        if self.parent_id == self.child_id:
            raise ValueError("A resource cannot be its own child.")
        return self


class ResourceHierarchy(ResourceHierarchyCreate, BaseHierarchy, table=True):
    """Table for resource hierarchy and its types"""

    parent_id: uuid.UUID = Field(
        primary_key=True
    )  # foreign_key="identifiertypelink.id",
    child_id: uuid.UUID = Field(
        primary_key=True
    )  # foreign_key="identifiertypelink.id",

    __table_args__ = (UniqueConstraint("parent_id", "child_id"),)

    relations: ClassVar = {
        ResourceType.demo_resource: [
            ResourceType.tag,
        ],
        ResourceType.category: [
            ResourceType.demo_resource,
            ResourceType.protected_resource,
            ResourceType.public_resource,
        ],
        ResourceType.protected_resource: [
            ResourceType.protected_child,
            ResourceType.protected_grand_child,
        ],
        ResourceType.protected_child: [
            ResourceType.protected_grand_child,
        ],
        ResourceType.module: [
            ResourceType.section,
            ResourceType.topic,
            ResourceType.element,
        ],
        ResourceType.section: [
            ResourceType.subsection,
            ResourceType.topic,
            ResourceType.element,
        ],
        ResourceType.subsection: [ResourceType.topic, ResourceType.element],
        ResourceType.topic: [ResourceType.element],
    }


class ResourceHierarchyRead(ResourceHierarchyCreate):
    """Read model for resource hierarchy"""

    pass


class IdentityHierarchyCreate(SQLModel):
    """Create model for identity hierarchy"""

    parent_id: uuid.UUID
    child_id: uuid.UUID
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )

    @model_validator(mode="after")
    def not_child_to_self(self):
        """Validates that the parent is not child to itself"""
        if self.parent_id == self.child_id:
            raise ValueError("An identity cannot be its own child.")
        return self


class IdentityHierarchy(IdentityHierarchyCreate, BaseHierarchy, table=True):
    """Table for identity hierarchy"""

    parent_id: uuid.UUID = Field(primary_key=True)
    child_id: uuid.UUID = Field(primary_key=True)

    __table_args__ = (UniqueConstraint("parent_id", "child_id"),)

    relations: ClassVar = {
        IdentityType.azure_group: [IdentityType.user],
        IdentityType.ueber_group: [IdentityType.group, IdentityType.user],
        IdentityType.group: [IdentityType.sub_group, IdentityType.user],
        IdentityType.sub_group: [IdentityType.sub_sub_group, IdentityType.user],
        IdentityType.sub_sub_group: [IdentityType.user],
    }


class IdentityHierarchyRead(IdentityHierarchyCreate):
    """Read model for identity hierarchy"""

    pass


# endregion hierarchies
