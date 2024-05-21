import uuid
from typing import Optional

from sqlmodel import Field, SQLModel

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


class ProtectedResourceRead(ProtectedResourceCreate):
    id: uuid.UUID


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


class ProtectedChildRead(ProtectedChildCreate):
    id: uuid.UUID


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
