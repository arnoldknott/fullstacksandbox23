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


class ResourceType(str, Enum):
    """Enum for the types of resources to identify which table a resource uuid belongs to"""

    demo_resource = "demo_resource"
    protected_resource = "protected_resource"
    module = "module"
    section = "section"
    subsection = "subsection"
    topic = "topic"
    element = "element"


class IdentityType(UUID, Enum):
    """Enum for the types of identities to identify which table an identity uuid belongs"""

    user = "user"
    # group = "group"
    azure_group = "azure_group"
    # brightspace_group = "brightspace_group"
    # discord_group = "discord_group"
    # google_group = "google_group"
