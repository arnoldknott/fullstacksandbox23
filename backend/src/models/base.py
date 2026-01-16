"""
Base model utilities for automatic SQLModel schema generation.

This module provides a factory-based approach for generating SQLModel schemas (Create, Read, Update, Extended)
with standardized patterns for attributes, relationships, and table models.

Key Components:
    - Attribute: Specification for model attributes (fields)
    - Relationship: Specification for ResourceHierarchy/IdentityHierarchy relationships
    - create_model(): Factory function to generate model schemas
    - Mixins: AccessRightsMixin, AccessPolicyMixin, CreatedAtMixin, UpdatedAtMixin

Usage Example:
    ```python
    from models.base import create_model, Attribute, Relationship, RelationshipHierarchyType
    from core.types import ResourceType

    ProtectedChild = create_model(
        name="ProtectedChild",
        table=True,
        attributes=[
            Attribute(name="title", type="str"),
        ],
        relationships=[
            Relationship(
                back_populates="protected_children",
                related_entity=ResourceType.protected_resource,
                hierarchy_type=RelationshipHierarchyType.child,
            )
        ]
    )

    # Access schemas:
    # ProtectedChild         - Table model (if table=True)
    # ProtectedChild.Create  - Create schema (for API input)
    # ProtectedChild.Read    - Read schema (for API output with relationships)
    # ProtectedChild.Update  - Update schema (all fields optional)
    # ProtectedChild.Extended - Extended schema (Read + access mixins)

    # Drop-in replacement for manual schema definitions:
    ProtectedChildCreate = ProtectedChild.Create
    ProtectedChildRead = ProtectedChild.Read
    ProtectedChildUpdate = ProtectedChild.Update
    ProtectedChildExtended = ProtectedChild.Extended
    ```

Features:
    - Automatic Create/Read/Update/Extended schema generation
    - Hardcoded id field with identifiertypelink foreign key
    - Standardized ResourceHierarchy/IdentityHierarchy relationships
    - Per-schema exclusion of attributes/relationships
    - Automatic relationship naming from ResourceType/IdentityType enum keys
    - Customizable extended mixins
    - Forward reference handling (call rebuild_model_forward_refs() after all models defined)
"""

import uuid
from datetime import datetime
from typing import Any, List, Optional, Set, Tuple, Type
from enum import Enum
import sys

from pydantic import BaseModel
from sqlmodel import Field, Relationship as SQLModelRelationship, SQLModel
from sqlmodel.main import SQLModelMetaclass

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
    extended = "extended"


class RelationshipHierarchyType(str, Enum):
    """Enum for relationship hierarchy types"""

    parent = "parent"
    child = "child"


class Attribute(BaseModel):
    """Attributes for the app's base model"""

    name: str
    type: str  # String representation of type, e.g., "str", "Optional[str]", "int"
    field_value: Any = None  # Can be a Field(...) or a default value or None
    exclude: Set[ModelTypes] = set()  # Set of schema types to exclude from


class Relationship(BaseModel):
    """Relationships for the app's base model"""

    name: Optional[str] = None  # Name of the relationship; auto-generated if None
    related_entity: ResourceType | IdentityType
    hierarchy_type: RelationshipHierarchyType
    back_populates: str
    exclude: Set[ModelTypes] = set()  # Set of schema types to exclude from
    read_schema_name: Optional[str] = (
        None  # Override for Read schema (e.g., "ProtectedChildReadNoParents")
    )


# Utility functions
def _get_hierarchy_model(model_name: str):
    """Determine if a model is a Resource or Identity and return the appropriate hierarchy model."""
    from models.access import ResourceHierarchy, IdentityHierarchy

    if model_name in ResourceType.list():
        return ResourceHierarchy, "ResourceHierarchy"
    elif model_name in IdentityType.list():
        return IdentityHierarchy, "IdentityHierarchy"
    else:
        raise ValueError(f"{model_name} is not a valid ResourceType or IdentityType")


def _build_hierarchy_relationship(
    model_name: str,
    rel_spec: Relationship,
) -> SQLModelRelationship:
    """
    Build a standardized Relationship(...) for ResourceHierarchy or IdentityHierarchy.

    Args:
        model_name: Name of the model being created
        rel_spec: Relationship specification

    Returns:
        SQLModel Relationship object with all hardcoded sa_relationship_kwargs
    """
    hierarchy_model, hierarchy_name = _get_hierarchy_model(model_name)
    related_entity_name = rel_spec.related_entity.value  # CamelCase class name

    # Determine join directions based on hierarchy_type
    if rel_spec.hierarchy_type == RelationshipHierarchyType.parent:
        # This model is the parent
        primary_join = f"{model_name}.id == foreign({hierarchy_name}.parent_id)"
        secondary_join = (
            f"{related_entity_name}.id == foreign({hierarchy_name}.child_id)"
        )
    else:  # child
        # This model is the child
        primary_join = f"{model_name}.id == foreign({hierarchy_name}.child_id)"
        secondary_join = (
            f"{related_entity_name}.id == foreign({hierarchy_name}.parent_id)"
        )

    return SQLModelRelationship(
        back_populates=rel_spec.back_populates,
        link_model=hierarchy_model,
        sa_relationship_kwargs={
            "lazy": "noload",
            "viewonly": True,
            "primaryjoin": primary_join,
            "secondaryjoin": secondary_join,
        },
    )


class SchemaType(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    EXTENDED = "extended"


def _build_annotations_and_fields(  # noqa: C901
    attributes: List[Attribute],
    relationships: List[Relationship],
    schema_type: SchemaType,
):
    """Build annotations and fields dict for a schema type."""

    annotations = {}
    fields = {}

    # Process attributes
    for attr in attributes:
        if schema_type == SchemaType.CREATE and ModelTypes.create in attr.exclude:
            continue
        if schema_type == SchemaType.READ and ModelTypes.read in attr.exclude:
            continue
        if schema_type == SchemaType.UPDATE and ModelTypes.update in attr.exclude:
            continue
        if schema_type == SchemaType.EXTENDED and ModelTypes.extended in attr.exclude:
            continue

        # For UPDATE, make all fields Optional
        if schema_type == SchemaType.UPDATE:
            type_str = attr.type
            if not type_str.startswith("Optional["):
                type_str = f"Optional[{type_str}]"
            annotations[attr.name] = eval(type_str)
            fields[attr.name] = None
        else:
            annotations[attr.name] = eval(attr.type)
            if attr.field_value is not None:
                fields[attr.name] = attr.field_value

    # Add id field for Read and Extended schemas
    if schema_type in {SchemaType.READ, SchemaType.EXTENDED}:
        annotations["id"] = uuid.UUID

    # Process relationships for Read and Extended schemas
    if schema_type in {SchemaType.READ, SchemaType.EXTENDED}:
        for rel in relationships:
            if schema_type == SchemaType.READ and ModelTypes.read in rel.exclude:
                continue
            if (
                schema_type == SchemaType.EXTENDED
                and ModelTypes.extended in rel.exclude
            ):
                continue

            rel_name = rel.name or rel.related_entity.name
            related_class_name = (
                rel.read_schema_name or f"{rel.related_entity.value}Read"
            )
            annotations[rel_name] = Optional[List[related_class_name]]
            fields[rel_name] = None

    # Add mixin fields for Extended schema
    if schema_type == SchemaType.EXTENDED:
        for mixin in (
            AccessRightsMixin,
            AccessPolicyMixin,
            CreatedAtMixin,
            UpdatedAtMixin,
        ):
            if hasattr(mixin, "__annotations__"):
                for field_name, field_type in mixin.__annotations__.items():
                    annotations[field_name] = field_type
                    # Get default value from mixin if exists
                    if hasattr(mixin, field_name):
                        fields[field_name] = getattr(mixin, field_name)

    fields["__annotations__"] = annotations
    return annotations, fields


def create_model(
    name: str,
    attributes: List[Attribute],
    relationships: Optional[List[Relationship]] = None,
    table: bool = True,
    extended_mixins: Tuple[Type[BaseModel], ...] = (
        AccessRightsMixin,
        AccessPolicyMixin,
        CreatedAtMixin,
        UpdatedAtMixin,
    ),
):
    """
    Factory function to create SQLModel schemas with Create, Read, Update, and Extended variants.

    Args:
        name: Name of the model (e.g., "ProtectedChild")
        attributes: List of Attribute specifications
        relationships: List of Relationship specifications (optional)
        table: Whether to create a table model (default True)
        extended_mixins: Tuple of mixin classes for Extended schema

    Returns:
        A class with nested Create, Read, Update, Extended schemas.
        If table=True, returns the table model with schemas attached.

    Usage:
        ProtectedChild = create_model(
            name="ProtectedChild",
            table=True,
            attributes=[
                Attribute(name="title", type="str", field_value=...),
            ],
            relationships=[
                Relationship(
                    related_entity=ResourceType.protected_resource,
                    hierarchy_type=child,
                    back_populates="protected_children"
                )
            ]
        )

        # Access: ProtectedChild (table model)
        #         ProtectedChild.Create
        #         ProtectedChild.Read
        #         ProtectedChild.Update
        #         ProtectedChild.Extended
    """
    relationships = relationships or []

    # ===== Build Create Schema =====
    create_annotations, create_fields = _build_annotations_and_fields(
        attributes, relationships, SchemaType.CREATE
    )
    # create_annotations = {}
    # create_fields = {}

    # for attr in attributes:
    #     if ModelTypes.create in attr.exclude:
    #         continue
    #     create_annotations[attr.name] = eval(attr.type)
    #     if attr.field_value is not None:
    #         create_fields[attr.name] = attr.field_value

    # create_fields["__annotations__"] = create_annotations
    Create = type(f"{name}Create", (SQLModel,), create_fields)

    # ===== Build Read Schema =====
    read_annotations, read_fields = _build_annotations_and_fields(
        attributes, relationships, SchemaType.READ
    )
    # read_annotations = {**create_annotations}
    # read_fields = {}

    # # Add id to Read
    # read_annotations["id"] = uuid.UUID

    # # Add relationships to Read (with forward refs)
    # for rel in relationships:
    #     if ModelTypes.read in rel.exclude:
    #         continue
    #     rel_name = rel.name or rel.related_entity.name
    #     related_class_name = rel.read_schema_name or f"{rel.related_entity.value}Read"
    #     read_annotations[rel_name] = Optional[List[related_class_name]]
    #     read_fields[rel_name] = None

    # read_fields["__annotations__"] = read_annotations
    Read = type(f"{name}Read", (Create,), read_fields)

    # ===== Build Update Schema (all fields optional) =====
    update_annotations, update_fields = _build_annotations_and_fields(
        attributes, relationships, SchemaType.UPDATE
    )
    # update_annotations = {}
    # update_fields = {}

    # for attr in attributes:
    #     if ModelTypes.update in attr.exclude:
    #         continue
    #     # Make all fields Optional
    #     type_str = attr.type
    #     if not type_str.startswith("Optional["):
    #         type_str = f"Optional[{type_str}]"
    #     update_annotations[attr.name] = eval(type_str)
    #     update_fields[attr.name] = None

    # update_fields["__annotations__"] = update_annotations
    Update = type(f"{name}Update", (SQLModel,), update_fields)

    # ===== Build Extended Schema =====
    extended_annotations, extended_fields = _build_annotations_and_fields(
        attributes, relationships, SchemaType.EXTENDED
    )
    # extended_annotations = {**read_annotations}
    # extended_fields = {**read_fields}

    # # Add mixin fields to Extended
    # for mixin in extended_mixins:
    #     if hasattr(mixin, "__annotations__"):
    #         for field_name, field_type in mixin.__annotations__.items():
    #             extended_annotations[field_name] = field_type
    #             # Get default value from mixin if exists
    #             if hasattr(mixin, field_name):
    #                 extended_fields[field_name] = getattr(mixin, field_name)

    # extended_fields["__annotations__"] = extended_annotations
    Extended = type(f"{name}Extended", (Read, *extended_mixins), extended_fields)

    # ===== Build Table Model (if requested) =====
    if table:
        table_annotations = {**create_annotations}
        table_fields = {**create_fields}

        # Add hardcoded id field
        table_annotations["id"] = Optional[uuid.UUID]
        table_fields["id"] = Field(
            default_factory=uuid.uuid4,
            foreign_key="identifiertypelink.id",
            primary_key=True,
        )

        # Add relationships to table model
        for rel in relationships:
            rel_name = rel.name or rel.related_entity.name
            related_class_name = rel.related_entity.value
            table_annotations[rel_name] = Optional[List[related_class_name]]
            table_fields[rel_name] = _build_hierarchy_relationship(name, rel)

        table_fields["__annotations__"] = table_annotations
        table_fields["__tablename__"] = name.lower()

        # Create a base that has table=True
        # SQLModel needs table=True passed to its metaclass __new__
        # We do this by creating the class with the right bases and kwargs
        TableModel = SQLModelMetaclass(
            name,
            (Create,),
            table_fields,
            table=True,
        )

        # Attach schemas to table model
        TableModel.Create = Create
        TableModel.Read = Read
        TableModel.Update = Update
        TableModel.Extended = Extended

        # NOTE: Forward references in relationships may need model_rebuild() after all models are defined
        # Call TableModel.Read.model_rebuild() and TableModel.Extended.model_rebuild() if needed

        return TableModel
    else:
        # Return a container class with nested schemas
        # TBD: Where is that useful? If anywhere, write tests for it!
        Container = type(name, (BaseModel,), {})
        Container.Create = Create
        Container.Read = Read
        Container.Update = Update
        Container.Extended = Extended

        return Container


# Helper function for rebuilding forward references after all models are defined
def rebuild_model_forward_refs(*models):
    """
    Rebuild forward references for models after all related models are defined.

    Usage:
        rebuild_model_forward_refs(ProtectedResource, ProtectedChild)
    """
    # Get caller's global namespace so Pydantic can resolve forward refs
    caller_globals = sys._getframe(1).f_globals

    for model in models:
        if hasattr(model, "Read"):
            model.Read.model_rebuild(_types_namespace=caller_globals)
        if hasattr(model, "Extended"):
            model.Extended.model_rebuild(_types_namespace=caller_globals)


# ===== EXAMPLE USAGE =====
#
# from models.base import (
#     create_model,
#     Attribute,
#     Relationship,
#     RelationshipHierarchyType,
#     rebuild_model_forward_refs,
# )
# from core.types import ResourceType
#
# # Create ProtectedResource model
# ProtectedResource = create_model(
#     name="ProtectedResource",
#     table=True,
#     attributes=[
#         Attribute(name="name", type="str"),
#         Attribute(name="description", type="Optional[str]", field_value=None),
#     ],
#     relationships=[
#         Relationship(
#             related_entity=ResourceType.protected_child,
#             hierarchy_type=RelationshipHierarchyType.parent,
#             back_populates="protected_resources"
#         )
#     ]
# )
#
# # Create ProtectedChild model
# ProtectedChild = create_model(
#     name="ProtectedChild",
#     attributes=[
#         Attribute(name="title", type="str"),
#     ],
#     relationships=[
#         Relationship(
#             name="protected_resources",
#             back_populates="protected_children",
#             related_entity=ResourceType.protected_resource,
#             hierarchy_type=RelationshipHierarchyType.child
#         )
#     ]
# )
#
# # Rebuild forward references after all models are defined
# rebuild_model_forward_refs(ProtectedResource, ProtectedChild)
#
# # Drop-in replacement for existing code:
# ProtectedResourceCreate = ProtectedResource.Create
# ProtectedResourceRead = ProtectedResource.Read
# ProtectedResourceUpdate = ProtectedResource.Update
# ProtectedResourceExtended = ProtectedResource.Extended
#
# ProtectedChildCreate = ProtectedChild.Create
# ProtectedChildRead = ProtectedChild.Read
# ProtectedChildUpdate = ProtectedChild.Update
# ProtectedChildExtended = ProtectedChild.Extended
