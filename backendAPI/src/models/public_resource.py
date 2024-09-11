import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class PublicResourceCreate(SQLModel):
    comment: str = Field(max_length=500)


class PublicResource(PublicResourceCreate, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class PublicResourceUpdate(PublicResourceCreate):
    pass


class PublicResourceRead(PublicResourceCreate):
    id: uuid.UUID
