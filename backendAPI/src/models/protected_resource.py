from datetime import datetime
from typing import Optional  # , TYPE_CHECKING

from sqlmodel import Field, SQLModel


class ProtectedResourceCreate(SQLModel):
    name: str
    description: Optional[str] = None
    last_accessed_at: Optional[datetime] = datetime.now()


class ProtectedResource(ProtectedResourceCreate, table=True):
    protected_resource_id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    last_updated_at: datetime = Field(default=datetime.now())
    last_accessed_at: datetime = Field(default=datetime.now())

    # Note: so far all times are UTC!


class ProtectedResourceRead(ProtectedResourceCreate):
    demo_resource_id: int
    last_accessed_at: datetime


class ProtectedResourceUpdate(ProtectedResourceCreate):
    name: Optional[str] = None
    # last_updated_at: datetime = Field(default=datetime.now(), exclude=True)
