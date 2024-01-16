import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class GroupUserLink(SQLModel, table=True):
    group_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="group.id", primary_key=True
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
