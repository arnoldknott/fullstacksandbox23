from typing import Optional

from pydantic_extra_types.language_code import LanguageAlpha2

from core.types import ResourceType

from .base import (
    Attribute,
    Relationship,
    RelationshipHierarchyType,
    create_model,
)

# Quiz = create_model(
#     name="Quiz",
#     attributes=[
#         Attribute(name="title", type=str),
#     ],
#     relationships=[
#         Relationship(
#             name="presentations",
#             back_populates="quizzes",
#             related_entity=ResourceType.presentation,
#             hierarchy_type=RelationshipHierarchyType.child,
#         ),
#         Relationship(
#             name="questions",
#             back_populates="quizzes",
#             related_entity=ResourceType.question,
#             hierarchy_type=RelationshipHierarchyType.parent,
#         ),
#     ],
# )


# TBD: For code based entites,
# add a a mixin "source", that specifies the source code location of the entity
# including type (internal | github | gitlab | ...), repo, path, branch.

# TBD: create a mixin to provide a "label" for all models,
# which needs to be unique within the parent
# so it will act as the identifier of this entity in code based entities,
# like quizzes, presentations, questions, etc.

Question = create_model(
    name="Question",
    attributes=[
        Attribute(name="question", type=str),
        Attribute(name="language", type=LanguageAlpha2, field_value="en"),
    ],
    relationships=[
        # Questions can be in many quizzes/presentations - note the answers are also following along!
        # Relationship(
        #     name="quizzes",
        #     back_populates="questions",
        #     related_entity=ResourceType.quiz,
        #     hierarchy_type=RelationshipHierarchyType.child,
        # ),
        Relationship(
            name="presentations",
            back_populates="questions",
            related_entity=ResourceType.presentation,
            hierarchy_type=RelationshipHierarchyType.child,
        ),
        Relationship(
            name="messages",
            back_populates="questions",
            related_entity=ResourceType.message,
            hierarchy_type=RelationshipHierarchyType.parent,
        ),
        Relationship(
            name="numericals",
            back_populates="questions",
            related_entity=ResourceType.numerical,
            hierarchy_type=RelationshipHierarchyType.parent,
        ),
    ],
)

# TBD: Figure out how to do this better - maybe a generic way to create these type aliases?
QuestionCreate = Question.Create
QuestionRead = Question.Read
QuestionUpdate = Question.Update
QuestionExtended = Question.Extended

# TBD: add another step: A Question has many Answers
# Intention: the parent needs to have write access to create answers
# So the parent to a mesage / numerical should be an Answer entity, not a Question.
# Or on the long run: create an Action: "link", so own, write, read, link?


# For regular text answers, reuse Message model:
Message = create_model(
    name="Message",
    attributes=[
        # Sourece is the location fo the source code
        Attribute(name="content", type=str),
        Attribute(name="language", type=LanguageAlpha2, field_value="en"),
    ],
    relationships=[
        # Turn into one-to-many; there si only one question per answer!
        Relationship(
            name="questions",
            back_populates="messages",
            related_entity=ResourceType.question,
            hierarchy_type=RelationshipHierarchyType.child,
        )
    ],
)

# TBD: Figure out how to do this better - maybe a generic way to create these type aliases?
MessageCreate = Message.Create
MessageRead = Message.Read
MessageUpdate = Message.Update
MessageExtended = Message.Extended

# For numerical answers, create Numerical model:
# For now float also covers integers,
# can be extended later if needed
Numerical = create_model(
    name="Numerical",
    attributes=[
        Attribute(name="value", type=float),
        Attribute(name="tolerance", type=Optional[float], field_value=None),
    ],
    relationships=[
        Relationship(
            name="questions",
            back_populates="numericals",
            related_entity=ResourceType.question,
            hierarchy_type=RelationshipHierarchyType.child,
        )
    ],
)

# TBD: Figure out how to do this better - maybe a generic way to create these type aliases?
NumericalCreate = Numerical.Create
NumericalRead = Numerical.Read
NumericalUpdate = Numerical.Update
NumericalExtended = Numerical.Extended
