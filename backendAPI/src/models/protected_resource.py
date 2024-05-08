import uuid
from datetime import datetime
from typing import Optional  # , TYPE_CHECKING

from sqlmodel import Field, SQLModel


class ProtectedResourceCreate(SQLModel):
    name: str
    description: Optional[str] = None
    last_accessed_at: Optional[datetime] = datetime.now()


class ProtectedResource(ProtectedResourceCreate, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )
    created_at: datetime = Field(default=datetime.now())
    # TBD: moce the last_updated_at and last_accessed_at to a resource access log table
    # together with action and identity_id
    # merge the last_accessed_at with the last_updated_at -> the action makes the difference!
    # add the http code to that table as well
    last_updated_at: datetime = Field(default=datetime.now())
    last_accessed_at: datetime = Field(default=datetime.now())

    # Note: so far all times are UTC!


class ProtectedResourceRead(ProtectedResourceCreate):
    id: uuid.UUID
    last_accessed_at: datetime


class ProtectedResourceUpdate(ProtectedResourceCreate):
    name: Optional[str] = None
    # last_updated_at: datetime = Field(default=datetime.now(), exclude=True)
