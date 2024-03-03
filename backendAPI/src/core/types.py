from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional


class CurrentUserData(BaseModel):
    """Model for the current user data - acts as interface for the request from endpoint to crud."""

    # TBD: add the user_id and remove azure_user_id!
    # user_id: UUID# not this one -> it's not in the HTTP request.
    # Class Access needs to resolve that from database. Consider caching in Redis!
    azure_user_id: UUID
    roles: Optional[List[str]]
    groups: Optional[List[UUID]]
    # scopes: List[str]# should not be relevant for access control?


class Action(Enum):
    """Enum for the actions that can be performed on a resource"""

    read = "read"
    write = "write"
    own = "own"
