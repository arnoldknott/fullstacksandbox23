import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.security import (
    Guards,
    check_token_against_guards,
    get_http_access_token_payload,
)
from core.types import GuardTypes
from crud.quiz import QuizCRUD, QuestionCRUD, MessageCRUD, NumericalCRUD
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

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

quiz_view = BaseView(QuizCRUD)
question_view = BaseView(QuestionCRUD)
message_view = BaseView(MessageCRUD)
numerical_view = BaseView(NumericalCRUD)


# region Quiz

@router.post("/", status_code=201)
async def post_quiz(
    quiz: QuizCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Quiz:
    """Creates a new quiz."""
    return await quiz_view.post(quiz, token_payload, guards)


@router.get("/", status_code=200)
async def get_quizzes(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[QuizRead]:
    """Returns all quizzes."""
    return await quiz_view.get(token_payload, guards)


@router.get("/{resource_id}", status_code=200)
async def get_quiz_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> QuizRead:
    """Returns a quiz."""
    return await quiz_view.get_by_id(resource_id, token_payload, guards)


@router.get("/public/{resource_id}", status_code=200)
async def get_public_quiz_by_id(
    resource_id: UUID,
) -> QuizRead:
    """Returns a public quiz without authentication."""
    return await quiz_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/{resource_id}", status_code=200)
async def put_quiz(
    resource_id: UUID,
    quiz: QuizUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Quiz:
    """Updates a quiz."""
    return await quiz_view.put(resource_id, quiz, token_payload, guards)


@router.delete("/{resource_id}", status_code=200)
async def delete_quiz(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> None:
    """Deletes a quiz."""
    return await quiz_view.delete(resource_id, token_payload, guards)


# endregion Quiz

# region Question

@router.post("/question/", status_code=201)
async def post_question(
    question: QuestionCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Question:
    """Creates a new question."""
    return await question_view.post(question, token_payload, guards)


@router.get("/question/", status_code=200)
async def get_questions(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[QuestionRead]:
    """Returns all questions."""
    return await question_view.get(token_payload, guards)


@router.get("/question/{resource_id}", status_code=200)
async def get_question_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> QuestionRead:
    """Returns a question."""
    return await question_view.get_by_id(resource_id, token_payload, guards)


@router.get("/question/public/{resource_id}", status_code=200)
async def get_public_question_by_id(
    resource_id: UUID,
) -> QuestionRead:
    """Returns a public question without authentication."""
    return await question_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/question/{resource_id}", status_code=200)
async def put_question(
    resource_id: UUID,
    question: QuestionUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Question:
    """Updates a question."""
    return await question_view.put(resource_id, question, token_payload, guards)


@router.delete("/question/{resource_id}", status_code=200)
async def delete_question(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> None:
    """Deletes a question."""
    return await question_view.delete(resource_id, token_payload, guards)


# endregion Question

# region Message

@router.post("/message/", status_code=201)
async def post_message(
    message: MessageCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Message:
    """Creates a new message."""
    return await message_view.post(message, token_payload, guards)


@router.post("/message/public", status_code=201)
async def post_public_message(
    message: MessageCreate,
) -> Message:
    """Creates a new public message without authentication."""
    return await message_view.post_with_public_access(
        message, token_payload=None, guards=None
    )


@router.get("/message/", status_code=200)
async def get_messages(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[MessageRead]:
    """Returns all messages."""
    return await message_view.get(token_payload, guards)


@router.get("/message/{resource_id}", status_code=200)
async def get_message_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> MessageRead:
    """Returns a message."""
    return await message_view.get_by_id(resource_id, token_payload, guards)


@router.get("/message/public/{resource_id}", status_code=200)
async def get_public_message_by_id(
    resource_id: UUID,
) -> MessageRead:
    """Returns a public message without authentication."""
    return await message_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/message/{resource_id}", status_code=200)
async def put_message(
    resource_id: UUID,
    message: MessageUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Message:
    """Updates a message."""
    return await message_view.put(resource_id, message, token_payload, guards)


@router.delete("/message/{resource_id}", status_code=200)
async def delete_message(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> None:
    """Deletes a message."""
    return await message_view.delete(resource_id, token_payload, guards)


# endregion Message

# region Numerical

@router.post("/numerical/", status_code=201)
async def post_numerical(
    numerical: NumericalCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Numerical:
    """Creates a new numerical answer."""
    return await numerical_view.post(numerical, token_payload, guards)


@router.post("/numerical/public", status_code=201)
async def post_public_numerical(
    numerical: NumericalCreate,
) -> Numerical:
    """Creates a new public numerical answer without authentication."""
    return await numerical_view.post_with_public_access(
        numerical, token_payload=None, guards=None
    )


@router.get("/numerical/", status_code=200)
async def get_numericals(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[NumericalRead]:
    """Returns all numerical answers."""
    return await numerical_view.get(token_payload, guards)


@router.get("/numerical/{resource_id}", status_code=200)
async def get_numerical_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> NumericalRead:
    """Returns a numerical answer."""
    return await numerical_view.get_by_id(resource_id, token_payload, guards)


@router.get("/numerical/public/{resource_id}", status_code=200)
async def get_public_numerical_by_id(
    resource_id: UUID,
) -> NumericalRead:
    """Returns a public numerical answer without authentication."""
    return await numerical_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/numerical/{resource_id}", status_code=200)
async def put_numerical(
    resource_id: UUID,
    numerical: NumericalUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> Numerical:
    """Updates a numerical answer."""
    return await numerical_view.put(resource_id, numerical, token_payload, guards)


@router.delete("/numerical/{resource_id}", status_code=200)
async def delete_numerical(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read", "api.write"], roles=["User"])),
) -> None:
    """Deletes a numerical answer."""
    return await numerical_view.delete(resource_id, token_payload, guards)


# endregion Numerical