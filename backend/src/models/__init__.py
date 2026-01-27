"""All models are imported here.
Database migrations - alembic - gets the connection to all used models here.
The folder also contains schemas, where schemas aren't explicit,
due to using sqlmodel."""

from models.base import rebuild_model_forward_refs
from .access import IdentityHierarchy  # noqa F401
from .access import ResourceHierarchy  # noqa F401
from .category import Category  # noqa F401
from .demo_file import DemoFile  # noqa F401
from .demo_resource import DemoResource  # noqa F401

# from .demo_resource_tag_link import DemoResourceTagLink  # noqa F401

# from .identity import AzureGroupUserLink  # noqa F401
from .identity import AzureGroup  # noqa F401
from .identity import User, UserAccount, UserProfile  # noqa F401
from .presentation import Presentation  # noqa F401

# from .quiz import Quiz, Question, Message, Numerical  # noqa F401
from .quiz import Question, Message, Numerical  # noqa F401

# from .presentation import Presentation, PresentationRead  # noqa F401
# from .quiz import MessageRead, NumericalRead, Quiz, QuizRead, Question, QuestionRead, Message, MessageRead, Numerical, NumericalRead  # noqa F401
from .protected_resource import (  # noqa F401
    ProtectedChild,
    ProtectedGrandChild,
    ProtectedResource,
)
from .public_resource import PublicResource  # noqa F401
from .tag import Tag  # noqa F401


PresentationCreate = Presentation.Create
PresentationRead = Presentation.Read
PresentationUpdate = Presentation.Update
PresentationExtended = Presentation.Extended
# QuizCreate = Quiz.Create
# QuizRead = Quiz.Read
# QuizUpdate = Quiz.Update
# QuizExtended = Quiz.Extended
QuestionCreate = Question.Create
QuestionRead = Question.Read
QuestionUpdate = Question.Update
QuestionExtended = Question.Extended
MessageCreate = Message.Create
MessageRead = Message.Read
MessageUpdate = Message.Update
MessageExtended = Message.Extended
NumericalCreate = Numerical.Create
NumericalRead = Numerical.Read
NumericalUpdate = Numerical.Update
NumericalExtended = Numerical.Extended

# rebuild_model_forward_refs(Presentation, Quiz, Question, Message, Numerical)
rebuild_model_forward_refs(Presentation, Question, Message, Numerical)
