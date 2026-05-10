from typing import Annotated, Optional, TypeAlias

from pydantic import AfterValidator, HttpUrl
from sqlmodel import Field

# from .quiz import Quiz, QuizRead
from core.config import config
from core.types import ResourceType

from .base import (
    Attribute,
    Relationship,
    RelationshipHierarchyType,
    create_model,
)


def validate_endpoint_path(path: str | None) -> str | None:
    """Validates that path forms a valid http/https URL when combined with the
    frontend origin, ensuring the stored relative path is a reachable endpoint.
    Falls back to 'http://localhost' when FRONTEND_SVELTE_ORIGIN is unset."""
    if path is None:
        return None
    HttpUrl(f"{config.FRONTEND_SVELTE_ORIGIN}{path}")
    return path


Presentation = create_model(
    name="Presentation",
    attributes=[
        # Source is the location fo the source code
        # This can be internal in this repository
        # or somewhere in another repo
        Attribute(name="source", type=str),
        # Path is the endpoint path to access the presentation
        # If Path is set, the presentation is accessible via the API at this path
        # otherwise it is accessible via the API at /presentations/{id} using the uuid of the presentation
        Attribute(
            name="path",
            type=Annotated[Optional[str], AfterValidator(validate_endpoint_path)],
            field_value=Field(
                unique=True,
                index=True,
            ),
        ),
    ],
    # These could be comments - not needed yet
    # relationships=[
    #     Relationship(
    #         name="comments",
    #         back_populates="presentations",
    #         related_entity=ResourceType.message,
    #         hierarchy_type=RelationshipHierarchyType.parent,
    #     )
    # ],
    relationships=[
        # Relationship(
        #     name="quizzes",
        #     back_populates="presentations",
        #     related_entity=ResourceType.quiz,
        #     hierarchy_type=RelationshipHierarchyType.parent,
        # ),
        Relationship(
            name="questions",
            back_populates="presentations",
            related_entity=ResourceType.question,
            hierarchy_type=RelationshipHierarchyType.parent,
        ),
    ],
)

# TBD: Figure out how to do this better - maybe a generic way to create these type aliases?
PresentationCreate: TypeAlias = Presentation.Create
PresentationRead: TypeAlias = Presentation.Read
PresentationUpdate: TypeAlias = Presentation.Update
PresentationExtended: TypeAlias = Presentation.Extended
