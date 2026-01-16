from datetime import datetime
from typing import List, Optional
from enum import Enum

from concurrent.interpreters import create
from pydantic import BaseModel
from sqlmodel import SQLModel

from core.types import Action, IdentityType, ResourceType
from models.access import AccessPolicyRead

# Model mixins - combine with the SQLModel-based models in src/models/*.py
# to extend the models with meta data,
# like access_rights, access_policies, created_at, updated_at


class AccessRightsMixin(BaseModel):
    """Mixin for access rights on a resource"""

    access_right: Optional[Action] = None


class AccessPolicyMixin(BaseModel):
    """Mixin for access policies on a resource"""

    access_policies: Optional[List[AccessPolicyRead]] = None


class CreatedAtMixin(BaseModel):
    """Mixin for created at timestamp"""

    creation_date: Optional[datetime] = None


class UpdatedAtMixin(BaseModel):
    """Mixin for updated at timestamp"""

    last_modified_date: Optional[datetime] = None

class ModelTypes(str, Enum):
    """Enum for excluding models in different schemas"""

    create = "create"
    read = "read"
    update = "update"

class RelationshipHierarchyType(str, Enum):
    """Enum for relationship hierarchy types"""

    parent = "parent"
    child = "child"

class Attribute(BaseModel):
    """Attributes for the app's base model"""

    name: str
    type: str
    field_parameters: dict
    exclude: Optional[ModelTypes] = None

class Relationship(BaseModel):
    """Relationships for the app's base model"""

    related_entity: ResourceType | IdentityType
    hierarchy_type: RelationshipHierarchyType
    back_populates: str
    exclude: Optional[ModelTypes] = None


class AppBaseModel(BaseModel):
    """Base model for all models"""

    attributes: List[Attribute]
    relationships: List[Relationship]
    extended_mixins: List[BaseModel] = AccessRightsMixin, AccessPolicyMixin, CreatedAtMixin, UpdatedAtMixin

    class Create(SQLModel):
        """Base 'create' schema"""
        pass

    class Read(SQLModel):
        """Base 'read' schema"""
        pass

    class Update(SQLModel):
        """Base 'update' schema"""
        pass

    class Extended(Read, AccessRightsMixin, AccessPolicyMixin, CreatedAtMixin, UpdatedAtMixin):
        """Base 'extended' schema"""
        pass