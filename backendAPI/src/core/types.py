from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

# import models


class CurrentUserData(BaseModel):
    """Model for the current user data - acts as interface for the request from endpoint to crud."""

    # TBD: add the user_id and remove azure_user_id!
    # user_id: UUID# not this one -> it's not in the HTTP request.
    # Class Access needs to resolve that from database. Consider caching in Redis!
    # azure_user_id: UUID
    user_id: UUID
    roles: Optional[List[str]] = []
    groups: Optional[List[UUID]] = []
    # scopes: List[str]# should not be relevant for access control?


class Action(Enum):
    """Enum for the actions that can be performed on a resource"""

    read = "read"
    write = "write"
    own = "own"


class ResourceType(str, Enum):
    """Enum for the types of resources to identify which table a resource uuid belongs to"""

    # The values need to match the exact name of the model class.

    # for sandbox only:
    category = "Category"  # potentially keep for production
    tag = "Tag"  # potentially keep for production
    demo_resource = "DemoResource"
    protected_resource = "ProtectedResource"
    # for future use:
    module = "Module"
    section = "Section"
    subsection = "Subsection"
    topic = "Topic"
    element = "Element"

    @classmethod
    def list(cls):
        return list(map(lambda x: x.value, cls._member_map_.values()))


class IdentityType(str, Enum):
    """Enum for the types of identities to identify which table an identity uuid belongs"""

    user = "User"
    # admin = "admin"
    # group = "group"
    azure_group = "AzureGroup"
    # brightspace_group = "brightspace_group"
    # discord_group = "discord_group"
    # google_group = "google_group"

    @classmethod
    def list(cls):
        return list(map(lambda x: x.value, cls._member_map_.values()))


# using models in stead of strings:
# class ResourceType(Enum):
#     """Enum for the types of resources to identify which table a resource uuid belongs to"""

#     # for sandbox only:
#     category = Category  # potentially keep for production
#     tag = Tag  # potentially keep for production
#     demo_resource = DemoResource
#     protected_resource = ProtectedResource
#     # for future use:
#     # module = models.Module
#     # section = models.Section
#     # subsection = models.Subsection
#     # topic = models.Topic
#     # element = models.Element


# class IdentityType(Enum):
#     """Enum for the types of identities to identify which table an identity uuid belongs"""

#     user = User
#     azure_group = AzureGroup
#     # user = "user"
#     # # admin = "admin"
#     # group = "group"
#     # azure_group = "azure_group"
#     # # brightspace_group = "brightspace_group"
#     # # discord_group = "discord_group"
#     # # google_group = "google_group"
