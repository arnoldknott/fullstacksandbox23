from .base import BaseCRUD

from models.quiz import (
    # Quiz,
    # QuizCreate,
    # QuizRead,
    # QuizUpdate,
    Question,
    # QuestionCreate,
    # QuestionRead,
    # QuestionUpdate,
    Message,
    # MessageCreate,
    # MessageRead,
    # MessageUpdate,
    Numerical,
    # NumericalCreate,
    # NumericalRead,
    # NumericalUpdate,
)


# class QuizCRUD(
#     BaseCRUD[
#         Quiz,
#         Quiz.Create,
#         Quiz.Read,
#         Quiz.Update,
#     ]
# ):
#     def __init__(self):
#         super().__init__(Quiz, allow_standalone=True)


class QuestionCRUD(
    BaseCRUD[
        Question,
        Question.Create,
        Question.Read,
        Question.Update,
    ]
):
    def __init__(self):
        super().__init__(Question, allow_standalone=True, allow_public_create=True)


class MessageCRUD(
    BaseCRUD[
        Message,
        Message.Create,
        Message.Read,
        Message.Update,
    ]
):
    def __init__(self):
        super().__init__(Message, allow_standalone=True, allow_public_create=True)


class NumericalCRUD(
    BaseCRUD[
        Numerical,
        Numerical.Create,
        Numerical.Read,
        Numerical.Update,
    ]
):
    def __init__(self):
        super().__init__(Numerical, allow_public_create=True)
