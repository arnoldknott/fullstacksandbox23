import logging

from core.types import EventGuard, GuardTypes
from crud.presentation import PresentationCRUD
from models.presentation import Presentation

from .base import BaseNamespace

logger = logging.getLogger(__name__)

guards = [
    EventGuard(event="connect", guards=None),  # GuardTypes(),  # allow public access
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


class PresentationNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Presentations."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/presentation",
            event_guards=guards,
            crud=PresentationCRUD,
            create_model=Presentation.Create,
            read_model=Presentation.Read,
            read_extended_model=Presentation.Extended,
            update_model=Presentation.Update,
            callback_on_connect=self.callback_on_connect,
            *args,
            **kwargs,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all demo resources:
        current_user = kwargs.get("current_user")
        request_access_data = bool(kwargs.get("request_access_data"))
        parent_id = kwargs.get("parent_id")
        await self._get_all(sid, current_user, request_access_data, parent_id=parent_id)
