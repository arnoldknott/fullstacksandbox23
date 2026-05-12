from models.quiz import (
    # Quiz, QuizCreate, QuizRead, QuizUpdate,
    QuestionCreate,
    QuestionRead,
    QuestionUpdate,
    MessageCreate,
    MessageRead,
    MessageUpdate,
    NumericalCreate,
    NumericalRead,
    NumericalUpdate,
    Message,
    Numerical,
    Question,
)

from .base import BaseCRUD

# class QuizCRUD(
#     BaseCRUD[
#         Quiz,
#         QuizCreate,
#         QuizRead,
#         QuizUpdate,
#     ]
# ):
#     def __init__(self):
#         super().__init__(Quiz, allow_standalone=True)


class QuestionCRUD(
    BaseCRUD[
        Question,
        QuestionCreate,
        QuestionRead,
        QuestionUpdate,
    ]
):
    def __init__(self):
        super().__init__(Question, allow_standalone=True, allow_public_create=True)


class MessageCRUD(
    BaseCRUD[
        Message,
        MessageCreate,
        MessageRead,
        MessageUpdate,
    ]
):
    def __init__(self):
        super().__init__(Message, allow_standalone=True, allow_public_create=True)


class NumericalCRUD(
    BaseCRUD[
        Numerical,
        NumericalCreate,
        NumericalRead,
        NumericalUpdate,
    ]
):
    def __init__(self):
        super().__init__(Numerical, allow_public_create=True)
