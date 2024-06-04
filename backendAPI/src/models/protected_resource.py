import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .access import ResourceHierarchy

# region ProtectedResource


class ProtectedResourceCreate(SQLModel):
    name: str
    description: Optional[str] = None


class ProtectedResource(ProtectedResourceCreate, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    protected_children: Optional[List["ProtectedChild"]] = Relationship(
        back_populates="protected_resources",
        link_model=ResourceHierarchy,
        sa_relationship_kwargs={
            # "lazy": "selectin",
            # "lazy": "subquery",
            # "lazy": "select",
            "lazy": "joined",
            # "lazy": "dynamic",
            # "lazy": "noload",
            # TBD: is foreign() needed here?
            "primaryjoin": "ProtectedResource.id == ResourceHierarchy.parent_id",
            "secondaryjoin": "ProtectedChild.id == ResourceHierarchy.child_id",
        },
    )


class ProtectedResourceRead(ProtectedResourceCreate):
    id: uuid.UUID
    protected_children: Optional[List["ProtectedChildReadNoParents"]] = None


class ProtectedResourceUpdate(ProtectedResourceCreate):
    name: Optional[str] = None


# endregion ProtectedResource

# region ProtectedChild


class ProtectedChildCreate(SQLModel):
    title: str


class ProtectedChild(ProtectedChildCreate, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    protected_resources: Optional[List["ProtectedResource"]] = Relationship(
        back_populates="protected_children",
        link_model=ResourceHierarchy,
        # primaryjoin="ProtectedChild.id == ResourceHierarchy.child_id",
        sa_relationship_kwargs={
            # "lazy": "selectin",
            # "lazy": "subquery",
            # "lazy": "select",
            "lazy": "joined",
            # "lazy": "dynamic",
            # "lazy": "noload",
            "primaryjoin": "ProtectedChild.id == foreign(ResourceHierarchy.child_id)",  # TBD: is foreign() needed here?
            "secondaryjoin": "foreign(ProtectedResource.id) == foreign(ResourceHierarchy.parent_id)",  # TBD: is foreign() needed here?
        },
    )


class ProtectedChildReadNoParents(ProtectedChildCreate):
    id: uuid.UUID


class ProtectedChildRead(ProtectedChildCreate):
    id: uuid.UUID
    protected_resources: Optional[List["ProtectedResourceRead"]] = None


class ProtectedChildUpdate(ProtectedChildCreate):
    title: Optional[str] = None


# endregion ProtectedChild


# region ProtectedGrandChild


class ProtectedGrandChildCreate(SQLModel):
    text: str


class ProtectedGrandChild(ProtectedGrandChildCreate, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class ProtectedGrandChildRead(ProtectedGrandChildCreate):
    id: uuid.UUID


class ProtectedGrandChildUpdate(ProtectedGrandChildCreate):
    text: Optional[str] = None


# endregion ProtectedGrandChild
