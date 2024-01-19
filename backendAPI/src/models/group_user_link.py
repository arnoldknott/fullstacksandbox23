import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class GroupUserLink(SQLModel, table=True):
    azure_group_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="group.azure_group_id", primary_key=True
    )
    azure_user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.azure_user_id", primary_key=True
    )
