from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel


def get_all_models(SQLModel=SQLModel):
    all_models = []

    for subclass in SQLModel.__subclasses__():
        all_models.append(subclass)
        all_models.extend(get_all_models(subclass))

    return all_models


# TBD: consider moving this to src/models/access.py?
class GuardTypes(BaseModel):
    """Protectors for the routes"""

    scopes: Optional[List[str]] = []
    roles: Optional[List[str]] = []
    groups: Optional[List[UUID]] = []


# For guarding events in socketio namespaces.
class EventGuard(BaseModel):
    """Guards for the events in socket.io namespaces"""

    event: str
    guards: GuardTypes


# TBD: consider moving this to src/models/access.py or src/core/security.py?
class CurrentUserData(BaseModel):
    """Model for the current user data - acts as interface for the request from endpoint to crud."""

    # Class Access needs to resolve that from database. Consider caching in Redis!
    user_id: UUID
    azure_token_roles: Optional[List[str]] = []
    azure_token_groups: Optional[List[UUID]] = []


# TBD: consider moving this to src/models/access.py?
class Action(str, Enum):
    """Enum for the actions that can be performed on a resource"""

    read = "read"
    write = "write"
    own = "own"


# Types identify resources in the identifier type table - used for registering resources and identities.
class EntityType(str, Enum):
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


# Resource versions of types
class ResourceType(EntityType):
    """Enum for the types of resources to identify which table a resource uuid belongs to"""

    # The values need to match the exact name of the model class.

    # TBD: consider getting those values programmatically from models?
    # or make this enum a collection of the models and add
    # a method __str__(self) that returns the name of the model?
    presentation = "Presentation"
    # quiz = "Quiz"
    question = "Question"
    # Messages are useful anywhere:
    # in chats, comments, and answers to (quiz-)questions
    message = "Message"
    # A numerical resource is a resource that holds a numerical value
    # useful for quiz answers, and exercise solutions
    numerical = "Numerical"
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


# Identity versions of types
class IdentityType(EntityType):
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
