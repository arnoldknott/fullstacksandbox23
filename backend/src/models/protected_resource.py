import uuid

from typing import Optional

# from sqlmodel import Field, Relationship, SQLModel

# from .access import ResourceHierarchy
# TBD: rename AppRelationship into Rrelationship, when sqlmodel is out?
from .base import (
    create_model,
    Attribute,
    Relationship,
    RelationshipHierarchyType,
    rebuild_model_forward_refs,
)
from core.types import ResourceType

# region ProtectedResource


# class ProtectedResourceCreate(SQLModel):
#     name: str
#     description: Optional[str] = None


# class ProtectedResource(ProtectedResourceCreate, table=True):
#     id: Optional[uuid.UUID] = Field(
#         default_factory=uuid.uuid4,
#         foreign_key="identifiertypelink.id",
#         primary_key=True,
#     )
#     protected_children: Optional[List["ProtectedChild"]] = Relationship(
#         back_populates="protected_resources",
#         link_model=ResourceHierarchy,
#         sa_relationship_kwargs={
#             "lazy": "joined",
#             "viewonly": True,
#             "primaryjoin": "ProtectedResource.id == foreign(ResourceHierarchy.parent_id)",
#             "secondaryjoin": "ProtectedChild.id == foreign(ResourceHierarchy.child_id)",
#         },
#     )


# class ProtectedResourceRead(ProtectedResourceCreate):
#     id: uuid.UUID
#     protected_children: Optional[List["ProtectedChildReadNoParents"]] = None


# class ProtectedResourceUpdate(ProtectedResourceCreate):
#     name: Optional[str] = None


ProtectedResource = create_model(
    name="ProtectedResource",
    attributes=[
        Attribute(name="name", type=str),
        Attribute(name="description", type=Optional[str], field_value=None),
    ],
    relationships=[
        Relationship(
            name="protected_children",
            back_populates="protected_resources",
            related_entity=ResourceType.protected_child,
            hierarchy_type=RelationshipHierarchyType.parent,
        )
    ],
)

# print("=== ProtectedResource model created ===")
# print(ProtectedResource.protected_children)

ProtectedResourceCreate = ProtectedResource.Create
ProtectedResourceRead = ProtectedResource.Read
ProtectedResourceUpdate = ProtectedResource.Update
# ProtectedResourceExtended = ProtectedResource.Extended


# endregion ProtectedResource

# region ProtectedChild


# class ProtectedChildCreate(SQLModel):
#     title: str


# class ProtectedChild(ProtectedChildCreate, table=True):
#     id: Optional[uuid.UUID] = Field(
#         default_factory=uuid.uuid4,
#         foreign_key="identifiertypelink.id",
#         primary_key=True,
#     )
#     protected_resources: Optional[List["ProtectedResource"]] = Relationship(
#         back_populates="protected_children",
#         link_model=ResourceHierarchy,
#         sa_relationship_kwargs={
#             "lazy": "joined",
#             "viewonly": True,
#             "primaryjoin": "ProtectedChild.id == foreign(ResourceHierarchy.child_id)",
#             "secondaryjoin": "ProtectedResource.id == foreign(ResourceHierarchy.parent_id)",
#         },
#     )


# class ProtectedChildReadNoParents(ProtectedChildCreate):
#     id: uuid.UUID


# class ProtectedChildRead(ProtectedChildCreate):
#     id: uuid.UUID
#     protected_resources: Optional[List["ProtectedResourceRead"]] = None


# class ProtectedChildUpdate(ProtectedChildCreate):
#     title: Optional[str] = None


# Create ProtectedChild model
ProtectedChild = create_model(
    name="ProtectedChild",
    attributes=[
        Attribute(name="title", type=str),
    ],
    relationships=[
        Relationship(
            name="protected_resources",
            back_populates="protected_children",
            related_entity=ResourceType.protected_resource,
            hierarchy_type=RelationshipHierarchyType.child,
        )
    ],
)

ProtectedChildCreate = ProtectedChild.Create
ProtectedChildRead = ProtectedChild.Read
ProtectedChildUpdate = ProtectedChild.Update
# ProtectedChildExtended = ProtectedChild.Extended


class ProtectedChildReadNoParents(ProtectedChildCreate):
    id: uuid.UUID


# endregion ProtectedChild


# region ProtectedGrandChild


# class ProtectedGrandChildCreate(SQLModel):
#     text: str


# class ProtectedGrandChild(ProtectedGrandChildCreate, table=True):
#     id: Optional[uuid.UUID] = Field(
#         default_factory=uuid.uuid4,
#         foreign_key="identifiertypelink.id",
#         primary_key=True,
#     )


# class ProtectedGrandChildRead(ProtectedGrandChildCreate):
#     id: uuid.UUID


# class ProtectedGrandChildUpdate(ProtectedGrandChildCreate):
#     text: Optional[str] = None

# Create ProtectedGrandChild model
ProtectedGrandChild = create_model(
    name="ProtectedGrandChild",
    attributes=[
        Attribute(name="text", type=str),
    ],
)

ProtectedGrandChildCreate = ProtectedGrandChild.Create
ProtectedGrandChildRead = ProtectedGrandChild.Read
ProtectedGrandChildUpdate = ProtectedGrandChild.Update
# ProtectedGrandChildExtended = ProtectedGrandChild.Extended


# endregion ProtectedGrandChild


# Rebuild all the models with forward references, i.e. with relationships to each other
rebuild_model_forward_refs(ProtectedResource, ProtectedChild)
