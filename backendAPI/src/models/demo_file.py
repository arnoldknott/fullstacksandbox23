import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class DemoFileCreate(SQLModel):
    name: str


class DemoFile(DemoFileCreate, table=True):
    name: str = Field(index=True, unique=True)
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )


class DemoFileRead(DemoFileCreate):
    id: uuid.UUID


class DemoFileUpdate(DemoFileCreate):
    pass
