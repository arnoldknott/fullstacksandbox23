from typing import Annotated, Optional

from pydantic import AfterValidator, BeforeValidator, HttpUrl
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


def convert_empty_path_to_null(path: str | None) -> str | None:
    # Treat empty/blank as "not set"
    if path is None:
        return None
    if not isinstance(path, str):
        raise ValueError("path must be a string or null")
    received = path.strip()
    if received == "":
        return None
    # # optional: normalize slash style
    # if not received.startswith("/"):
    #     received = f"/{received}"
    return received


def validate_endpoint_path(path: str | None) -> str | None:
    """Validates that path forms a valid http/https URL when combined with the
    frontend origin, ensuring the stored relative path is a reachable endpoint.
    Falls back to 'http://localhost' when FRONTEND_SVELTE_ORIGIN is unset."""
    if path is None:
        return None
    print(f"=== validate_endpoint_path - path ===")
    print(path, flush=True)
    print(f"=== validate_endpoint_path - FRONTEND_SVELTE_ORIGIN ===")
    print(config.FRONTEND_SVELTE_ORIGIN, flush=True)
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
            type=Annotated[
                Optional[str],
                BeforeValidator(convert_empty_path_to_null),
                AfterValidator(validate_endpoint_path),
            ],
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
PresentationCreate = Presentation.Create
PresentationRead = Presentation.Read
PresentationUpdate = Presentation.Update
PresentationExtended = Presentation.Extended
