from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel

# import models


def get_all_models(SQLModel=SQLModel):
    all_models = []

    for subclass in SQLModel.__subclasses__():
        all_models.append(subclass)
        all_models.extend(get_all_models(subclass))

    return all_models


class GuardTypes(BaseModel):
    """Protectors for the routes"""

    scopes: Optional[List[str]] = []
    roles: Optional[List[str]] = []
    groups: Optional[List[UUID]] = []


# class AppRoles(str, Enum):
#     """Enum for the roles that can be self-assigned to a user inside the app; Note: consent is required for some roles, handled by frontend!"""

#     # This is for services only, that don't require an account linking.
#     # For services that require an account linking, a linked account counts as an assigned role.

#     publicAIuser = "publicAIuser"
#     privateAIuser = "privateAIuser"


class CurrentUserData(BaseModel):
    """Model for the current user data - acts as interface for the request from endpoint to crud."""

    # TBD: add the user_id and remove azure_user_id!
    # user_id: UUID# not this one -> it's not in the HTTP request.
    # Class Access needs to resolve that from database. Consider caching in Redis!
    # azure_user_id: UUID
    user_id: UUID
    azure_token_roles: Optional[List[str]] = []
    azure_token_groups: Optional[List[UUID]] = []
    # scopes: List[str]# should not be relevant for access control?


class Action(str, Enum):
    """Enum for the actions that can be performed on a resource"""

    read = "read"
    write = "write"
    own = "own"


class BaseType(str, Enum):
    """Base enum for types of entities in the database"""

    # The values need to match the exact name of the model class.

    @classmethod
    def list(cls):
        return list(map(lambda x: x.value, cls._member_map_.values()))

    @classmethod
    def get_model(cls, entity_type: str):
        all_models = get_all_models()
        model = next(filter(lambda m: m.__name__ == entity_type, all_models), None)
        if model is None:
            raise ValueError(f"Table {entity_type} not found.")
        else:
            return model

    def __str__(self):
        return self.name


class ResourceType(BaseType):
    """Enum for the types of resources to identify which table a resource uuid belongs to"""

    # The values need to match the exact name of the model class.

    # TBD: consider getting those values programmatically from models?
    # or make this enum a collection of the models and add
    # a method __str__(self) that returns the name of the model?
    category = "Category"
    tag = "Tag"
    demo_resource = "DemoResource"
    protected_resource = "ProtectedResource"
    protected_child = "ProtectedChild"
    protected_grand_child = "ProtectedGrandChild"
    public_resource = "PublicResource"
    module = "Module"
    section = "Section"
    subsection = "Subsection"
    topic = "Topic"
    element = "Element"
    demo_file = "DemoFile"


# moved into hierarchy models - as this is used together with the models most of the time anyways:
# class BaseHierarchy:
#     """Class to define the hierarchy of the entities"""

#     relations = {}

#     @classmethod
#     def get_allowed_children_types(cls, entity_type: str) -> List[str]:
#         return cls.relations.get(entity_type, [])


# class ResourceHierarchy(BaseHierarchy):
#     """Class to define the hierarchy of the resources"""

#     relations = {
#         ResourceType.category: [
#             ResourceType.demo_resource,
#             ResourceType.protected_resource,
#             ResourceType.public_resource,
#         ],
#         ResourceType.protected_resource: [
#             ResourceType.protected_child,
#             ResourceType.protected_grand_child,
#         ],
#         ResourceType.protected_child: [
#             ResourceType.protected_grand_child,
#         ],
#         ResourceType.module: [
#             ResourceType.section,
#             ResourceType.topic,
#             ResourceType.element,
#         ],
#         ResourceType.section: [
#             ResourceType.subsection,
#             ResourceType.topic,
#             ResourceType.element,
#         ],
#         ResourceType.subsection: [ResourceType.topic, ResourceType.element],
#         ResourceType.topic: [ResourceType.element],
#     }


class IdentityType(BaseType):
    """Enum for the types of identities to identify which table an identity uuid belongs"""

    # TBD: consider getting those values programmatically?
    user = "User"
    user_account = "UserAccount"
    user_profile = "UserProfile"
    ueber_group = "UeberGroup"
    group = "Group"
    sub_group = "SubGroup"
    sub_sub_group = "SubSubGroup"
    azure_group = "AzureGroup"
    # brightspace_group = "brightspace_group"
    # discord_group = "discord_group"
    # google_group = "google_group"


# class IdentityHierarchy(BaseHierarchy):
#     """Class to define the hierarchy of the identities"""

#     relations = {
#         IdentityType.azure_group: [IdentityType.user],
#         IdentityType.group: [IdentityType.sub_group, IdentityType.user],
#         IdentityType.sub_group: [IdentityType.sub_sub_group, IdentityType.user],
#         IdentityType.sub_sub_group: [IdentityType.user],
#     }


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
