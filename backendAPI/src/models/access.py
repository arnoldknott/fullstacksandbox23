import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from pydantic import model_validator, BaseModel  # , create_model

# if TYPE_CHECKING:
from core.types import Action, IdentityType, ResourceType, CurrentUserData

# from models import (
#     Category,
#     Tag,
#     DemoResource,
#     ProtectedResource,
#     # Module,
#     # Section,
#     # Subsection,
#     # Topic,
#     # Element,
# )

# ResourceType = create_model(
#     "ResourceType",
#     category=(Category, ...),
#     tag=(Tag, ...),
#     demo_resource=(DemoResource, ...),
#     protected_resource=(ProtectedResource, ...),
#     # module=(Module, ...),
#     # section=(Section, ...),
#     # subsection=(Subsection, ...),
#     # topic=(Topic, ...),
#     # element=(Element, ...),
# )

# TBD: Retrieve resource_types and identity_types from the database from either link or hierarchy tables
# but don't bother the API user with it. All the endpoints need to know is the UUID of the resource or identity.


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
    # identity_type: Optional["IdentityType"] = None
    resource_id: uuid.UUID
    # resource_type: Union["ResourceType", "IdentityType"] = "ResourceType"
    action: "Action"
    public: bool = Field(
        default=False,
        description="Set to true, if the resource is public and does not require any access control.",
    )

    # TBD: should this move to AccessPolicy just below?
    @model_validator(mode="after")
    def either_identity_assignment_or_public(self):
        """Validates either identity is assigned or resource is public"""
        # TBD: refactor: only when Action is read, then public is allowed and no identity is allowed
        # TBD: refactor: when Action is anything else, then public is not allowed and identity is required
        if self.public is True:
            # if (self.identity_id is not None) or (self.identity_type is not None):
            if self.identity_id is not None:
                raise ValueError("No identity can be assigned to a public resource.")
        else:
            # if (self.identity_id is None) or (self.identity_type is None):
            if self.identity_id is None:
                raise ValueError(
                    "An identity must be assigned to a non-public resource."
                )
        return self


class AccessPolicy(AccessPolicyCreate, table=True):
    """Table for access control"""

    # TBD: consider totally removing the id here and
    # use the combination of identity_id, resource_id, and action
    # as composite primary key? => Not a good idea, as identity_id is optional - due to public resources
    # id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    identity_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="identifiertypelink.id", index=True
    )
    # identity_id: Optional[uuid.UUID] = Field(
    #     default=None, primary_key=True, nullable=True
    # )
    # identity_id: Optional[uuid.UUID] = Field(
    #     primary_key=True, default=None, index=True
    # )  # needs to be a foreign key / relationship for join statements?
    # identity_type: Optional["IdentityType"] = Field(default=None, index=True)
    # resource_id: uuid.UUID = Field(primary_key=True)  # , index=True)
    resource_id: uuid.UUID = Field(foreign_key="identifiertypelink.id", index=True)
    # resource_type: str = Field(index=True)
    # action: "Action" = Field()  # not using primary_key=True here means,
    # that the other two (identity_id & resource_id need to be unique) are the primary key
    # That is, only one level of Action (should be the highest) is stored in the database!
    # allows multiple levels of Action to be stored in the database:
    action: "Action" = Field()

    __table_args__ = (UniqueConstraint("identity_id", "resource_id", "action"),)
    # identity_id: uuid.UUID = Field(primary_key=True)
    # identity_type: "IdentityType" = Field(index=True)
    # resource_id: uuid.UUID = Field(primary_key=True)
    # resource_type: "ResourceType" = Field(index=True)
    # action: "Action" = Field()
    # override: bool = Field(default=False)


class AccessPolicyRead(AccessPolicyCreate):
    """Read model for access policies"""

    id: int


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
        foreign_key="identifiertypelink.id", index=True
    )
    resource_id: uuid.UUID = Field(foreign_key="identifiertypelink.id", index=True)
    time: datetime = Field(default=datetime.now(), index=True)
    status_code: int = Field()


class AccessLogRead(AccessLogCreate):
    """Read model access attempt logs"""

    id: int
    time: datetime


class ResourceHierarchyCreate(SQLModel):
    """Create model for resource hierarchy"""

    parent_id: uuid.UUID
    # parent_type: "ResourceType"
    child_id: uuid.UUID
    # child_type: "ResourceType"
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )

    @model_validator(mode="after")
    def either_inherit_or_not(self):
        """Validates either inherit is set or not"""
        if self.inherit is True:
            if (self.parent_id == self.child_resource_id) and (
                self.parent_type == self.child_type
            ):
                raise ValueError("A resource cannot inherit from itself.")
        return self


class ResourceHierarchy(SQLModel, table=True):
    """Table for resource hierarchy"""

    parent_id: uuid.UUID = Field(primary_key=True)
    # parent_type: "ResourceType" = Field(index=True)
    child_id: uuid.UUID = Field(primary_key=True)
    # child_type: "ResourceType" = Field(index=True)
    inherit: bool = Field(
        default=False,
        description="Set to true, if the child inherits permissions from this parent.",
    )

    __table_args__ = (UniqueConstraint("parent_id", "child_id"),)


class ResourceHierarchyRead(ResourceHierarchyCreate):
    """Read model for resource hierarchy"""

    pass
