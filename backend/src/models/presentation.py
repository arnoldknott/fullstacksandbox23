from typing import Optional

from .base import (
    create_model,
    Attribute,
    Relationship,
    RelationshipHierarchyType,
)

# from .quiz import Quiz, QuizRead
from core.types import ResourceType

Presentation = create_model(
    name="Presentation",
    attributes=[
        # Source is the location fo the source code
        # This can be internal in this repository
        # or somewhere in another repo
        Attribute(name="source", type=str),
        # Path is the endpoint path to access the presentation
        # some might be hard coded and
        # some might have the [id] as a slug in the path
        # TBD: add unique contraint and valid path check
        Attribute(name="path", type=Optional[str], field_value=None),
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
