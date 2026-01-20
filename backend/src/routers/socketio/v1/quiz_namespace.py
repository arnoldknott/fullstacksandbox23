import logging

from core.types import EventGuard, GuardTypes
from crud.quiz import (
    QuestionCRUD,
    MessageCRUD,
    NumericalCRUD,
)
from models.quiz import (
    Question,
    Message,
    Numerical,
)

from .base import BaseNamespace

logger = logging.getLogger(__name__)

question_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(),  # allow public access
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class QuestionNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Questions."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/question",
            event_guards=message_guards,
            crud=QuestionCRUD,
            create_model=Question.Create,
            read_model=Question.Read,
            read_extended_model=Question.Extended,
            update_model=Question.Update,
            callback_on_connect=self.callback_on_connect,
            *args,
            **kwargs,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read events to fetch requested questions:
        resource_ids = kwargs.pop("resource_ids", None)
        for resource_id in resource_ids or []:
            await self.on_read(sid, resource_id=resource_id)


message_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(),  # allow public access
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(),  # allow public access
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class MessageNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Messages."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/message",
            event_guards=message_guards,
            crud=MessageCRUD,
            create_model=Message.Create,
            read_model=Message.Read,
            read_extended_model=Message.Extended,
            update_model=Message.Update,
            callback_on_connect=self.callback_on_connect,
            *args,
            **kwargs,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read events to fetch requested messages:
        resource_ids = kwargs.pop("resource_ids", None)
        for resource_id in resource_ids or []:
            await self.on_read(sid, resource_id=resource_id)


numerical_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(),  # allow public access
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(),  # allow public access
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class NumericalNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Numericals."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/numerical",
            event_guards=numerical_guards,
            crud=NumericalCRUD,
            create_model=Numerical.Create,
            read_model=Numerical.Read,
            read_extended_model=Numerical.Extended,
            update_model=Numerical.Update,
            callback_on_connect=self.callback_on_connect,
            *args,
            **kwargs,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read events to fetch requested numericals:
        resource_ids = kwargs.pop("resource_ids", None)
        for resource_id in resource_ids or []:
            await self.on_read(sid, resource_id=resource_id)
