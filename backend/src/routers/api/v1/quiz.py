import logging
from uuid import UUID

from typing import Annotated
from fastapi import APIRouter, Depends, Query

from core.security import (
    Guards,
    get_http_access_token_payload,
)
from core.types import GuardTypes

# from crud.quiz import QuizCRUD, QuestionCRUD, MessageCRUD, NumericalCRUD
from crud.quiz import QuestionCRUD, MessageCRUD, NumericalCRUD
from models.quiz import Question, Message, Numerical

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

# quiz_view = BaseView(QuizCRUD)
question_view = BaseView(QuestionCRUD)
message_view = BaseView(MessageCRUD)
numerical_view = BaseView(NumericalCRUD)


# region Quiz


# @router.post("/", status_code=201)
# async def post_quiz(
#     quiz: Quiz.Create,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(
#         Guards(scopes=["api.read", "api.write"], roles=["User"])
#     ),
# ) -> Quiz:
#     """Creates a new quiz."""
#     return await quiz_view.post(quiz, token_payload, guards)


# @router.get("/", status_code=200)
# async def get_quizzes(
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
# ) -> list[Quiz.Read]:
#     """Returns all quizzes."""
#     return await quiz_view.get(token_payload, guards)


# @router.get("/{resource_id}", status_code=200)
# async def get_quiz_by_id(
#     resource_id: UUID,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
# ) -> Quiz.Read:
#     """Returns a quiz."""
#     return await quiz_view.get_by_id(resource_id, token_payload, guards)


# @router.get("/public/{resource_id}", status_code=200)
# async def get_public_quiz_by_id(
#     resource_id: UUID,
# ) -> Quiz.Read:
#     """Returns a public quiz without authentication."""
#     return await quiz_view.get_by_id(resource_id, token_payload=None, guards=None)


# @router.put("/{resource_id}", status_code=200)
# async def put_quiz(
#     resource_id: UUID,
#     quiz: Quiz.Update,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(
#         Guards(scopes=["api.read", "api.write"], roles=["User"])
#     ),
# ) -> Quiz:
#     """Updates a quiz."""
#     return await quiz_view.put(resource_id, quiz, token_payload, guards)


# @router.delete("/{resource_id}", status_code=200)
# async def delete_quiz(
#     resource_id: UUID,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(
#         Guards(scopes=["api.read", "api.write"], roles=["User"])
#     ),
# ) -> None:
#     """Deletes a quiz."""
#     return await quiz_view.delete(resource_id, token_payload, guards)


# endregion Quiz

# region Question


@router.post("/question/", status_code=201)
async def post_question(
    question: Question.Create,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> Question:
    """Creates a new question."""
    return await question_view.post(question, token_payload, guards)


@router.post("/question/{question_id}/message/", status_code=201)
async def post_question_message(
    question_id: UUID,
    message: Message.Create,
    inherit: Annotated[bool, Query()] = True,
    public: Annotated[bool, Query()] = False,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> Message:
    """Creates a new message answer for a question."""
    return await question_view.post_add_child_to_parent(
        parent_id=question_id,
        child_create=message,
        child_view=message_view,
        token_payload=token_payload,
        guards=guards,
        inherit=inherit,
        public=public,
    )


@router.get("/question/", status_code=200)
async def get_questions(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[Question.Read]:
    """Returns all questions."""
    return await question_view.get(token_payload, guards)


@router.get("/question/{resource_id}", status_code=200)
async def get_question_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> Question.Read:
    """Returns a question."""
    return await question_view.get_by_id(resource_id, token_payload, guards)


@router.get("/question/public/{resource_id}", status_code=200)
async def get_public_question_by_id(
    resource_id: UUID,
) -> Question.Read:
    """Returns a public question without authentication."""
    return await question_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/question/{resource_id}", status_code=200)
async def put_question(
    resource_id: UUID,
    question: Question.Update,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> Question:
    """Updates a question."""
    return await question_view.put(resource_id, question, token_payload, guards)


@router.delete("/question/{resource_id}", status_code=200)
async def delete_question(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> None:
    """Deletes a question."""
    return await question_view.delete(resource_id, token_payload, guards)


# endregion Question

# region Message


# @router.post("/message/", status_code=201)
# async def post_message(
#     message: Message.Create,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(
#         Guards(scopes=["api.read", "api.write"], roles=["User"])
#     ),
# ) -> Message:
#     """Creates a new message."""
#     return await message_view.post(message, token_payload, guards)


# @router.post("/message/public", status_code=201)
# async def post_public_message(
#     message: Message.Create,
# ) -> Message:
#     """Creates a new public message without authentication."""
#     return await message_view.post_with_public_access(
#         message, token_payload=None, guards=None
#     )


@router.get("/message/", status_code=200)
async def get_messages(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[Message.Read]:
    """Returns all messages."""
    return await message_view.get(token_payload, guards)


@router.get("/message/{resource_id}", status_code=200)
async def get_message_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> Message.Read:
    """Returns a message."""
    return await message_view.get_by_id(resource_id, token_payload, guards)


@router.get("/message/public/{resource_id}", status_code=200)
async def get_public_message_by_id(
    resource_id: UUID,
) -> Message.Read:
    """Returns a public message without authentication."""
    return await message_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/message/{resource_id}", status_code=200)
async def put_message(
    resource_id: UUID,
    message: Message.Update,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> Message:
    """Updates a message."""
    return await message_view.put(resource_id, message, token_payload, guards)


@router.delete("/message/{resource_id}", status_code=200)
async def delete_message(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> None:
    """Deletes a message."""
    return await message_view.delete(resource_id, token_payload, guards)


# endregion Message

# region Numerical


# @router.post("/numerical/", status_code=201)
# async def post_numerical(
#     numerical: Numerical.Create,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(
#         Guards(scopes=["api.read", "api.write"], roles=["User"])
#     ),
# ) -> Numerical:
#     """Creates a new numerical answer."""
#     return await numerical_view.post(numerical, token_payload, guards)


# @router.post("/numerical/public", status_code=201)
# async def post_public_numerical(
#     numerical: Numerical.Create,
# ) -> Numerical:
#     """Creates a new public numerical answer without authentication."""
#     return await numerical_view.post_with_public_access(
#         numerical, token_payload=None, guards=None
#     )


@router.get("/numerical/", status_code=200)
async def get_numericals(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> list[Numerical.Read]:
    """Returns all numerical answers."""
    return await numerical_view.get(token_payload, guards)


@router.get("/numerical/{resource_id}", status_code=200)
async def get_numerical_by_id(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
) -> Numerical.Read:
    """Returns a numerical answer."""
    return await numerical_view.get_by_id(resource_id, token_payload, guards)


@router.get("/numerical/public/{resource_id}", status_code=200)
async def get_public_numerical_by_id(
    resource_id: UUID,
) -> Numerical.Read:
    """Returns a public numerical answer without authentication."""
    return await numerical_view.get_by_id(resource_id, token_payload=None, guards=None)


@router.put("/numerical/{resource_id}", status_code=200)
async def put_numerical(
    resource_id: UUID,
    numerical: Numerical.Update,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> Numerical:
    """Updates a numerical answer."""
    return await numerical_view.put(resource_id, numerical, token_payload, guards)


@router.delete("/numerical/{resource_id}", status_code=200)
async def delete_numerical(
    resource_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(
        Guards(scopes=["api.read", "api.write"], roles=["User"])
    ),
) -> None:
    """Deletes a numerical answer."""
    return await numerical_view.delete(resource_id, token_payload, guards)


# endregion Numerical
