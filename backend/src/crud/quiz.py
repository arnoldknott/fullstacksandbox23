from .base import BaseCRUD

from models.quiz import (
    Quiz,
    QuizCreate,
    QuizRead,
    QuizUpdate,
    Question,
    QuestionCreate,
    QuestionRead,
    QuestionUpdate,
    Message,
    MessageCreate,
    MessageRead,
    MessageUpdate,
    Numerical,
    NumericalCreate,
    NumericalRead,
    NumericalUpdate,
)

class QuizCRUD(
    BaseCRUD[
        Quiz,
        QuizCreate,
        QuizRead,
        QuizUpdate,
    ]
):
    def __init__(self):
        super().__init__(Quiz)

class QuestionCRUD(
    BaseCRUD[
        Question,
        QuestionCreate,
        QuestionRead,
        QuestionUpdate,
    ]
):
    def __init__(self):
        super().__init__(Question)

class MessageCRUD(
    BaseCRUD[
        Message,
        MessageCreate,
        MessageRead,
        MessageUpdate,
    ]
):
    def __init__(self):
        super().__init__(Message)

class NumericalCRUD(
    BaseCRUD[
        Numerical,
        NumericalCreate,
        NumericalRead,
        NumericalUpdate,
    ]
):
    def __init__(self):
        super().__init__(Numerical)