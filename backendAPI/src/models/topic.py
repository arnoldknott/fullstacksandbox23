import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TopicCreate(SQLModel):
    """Schema for creating a group."""

    is_active: bool = True


class Topic(TopicCreate, table=True):
    """Schema for a group in the database."""

    topic_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    last_updated_at: datetime = Field(default=datetime.now())

    # create the relationships and back population to versions here??


class TopicRead(TopicCreate):
    """Schema for reading a group."""

    topic_id: uuid.UUID  # no longer optional - needs to exist now

    # add everything, that should be shown from the backpopulations here
    # but only what's realistically needed!


class TopicUpdate(TopicCreate):
    """Schema for updating a group."""

    is_active: Optional[bool] = None
