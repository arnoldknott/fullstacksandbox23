from pydantic_extra_types.language_code import LanguageAlpha2
from typing import Optional

from .base import (
    create_model,
    Attribute,
    Relationship,
    RelationshipHierarchyType,
)

from core.types import ResourceType

Quiz = create_model(
    name="Quiz",
    attributes=[
        Attribute(name="title", type=str),
    ],
    relationships=[
        Relationship(
            name="presentations",
            back_populates="quizzes",
            related_entity=ResourceType.presentation,
            hierarchy_type=RelationshipHierarchyType.child,
        ),
        Relationship(
            name="questions",
            back_populates="quizzes",
            related_entity=ResourceType.question,
            hierarchy_type=RelationshipHierarchyType.parent,
        ),
    ],
)


# QuizCreate = Quiz.Create
# QuizRead = Quiz.Read
# QuizUpdate = Quiz.Update
# QuizExtended = Quiz.Extended


Question = create_model(
    name="Question",
    attributes=[
        Attribute(name="question", type=str),
        Attribute(name="language", type=LanguageAlpha2, field_value="en"),
    ],
    relationships=[
        # Questions can be in many quizzes - note the answers are also following along!
        Relationship(
            name="quizzes",
            back_populates="questions",
            related_entity=ResourceType.quiz,
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

# QuestionCreate = Question.Create
# QuestionRead = Question.Read
# QuestionUpdate = Question.Update
# QuestionExtended = Question.Extended


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

# MessageCreate = Message.Create
# MessageRead = Message.Read
# MessageUpdate = Message.Update
# MessageExtended = Message.Extended

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
# NumericalCreate = Numerical.Create
# NumericalRead = Numerical.Read
# NumericalUpdate = Numerical.Update
# NumericalExtended = Numerical.Extended

# rebuild_model_forward_refs(Quiz, Message, Numerical)
