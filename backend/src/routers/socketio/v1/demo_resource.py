# import logging

from core.types import EventGuard, GuardTypes
from crud.demo_resource import DemoResourceCRUD
from models.demo_resource import (
    DemoResourceCreate,
    DemoResourceExtended,
    DemoResourceRead,
    DemoResourceUpdate,
)

from .base import BaseNamespace

# logger = logging.getLogger(__name__)

# protect the events with requirements for scopes, roles and groups in users access token
event_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
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


class DemoResourceNamespace(BaseNamespace):
    """Socket.IO interface for Demo Resources."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/demo-resource",
            event_guards=event_guards,
            crud=DemoResourceCRUD,
            create_model=DemoResourceCreate,
            read_model=DemoResourceRead,
            read_extended_model=DemoResourceExtended,
            update_model=DemoResourceUpdate,
            callback_on_connect=self.callback_on_connect,
            *args,
            **kwargs,
        )
        # self.namespace = namespace

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all demo resources:
        current_user = kwargs.get("current_user")
        request_access_data = kwargs.get("request_access_data")
        parent_id = kwargs.get("parent_id")
        await self._get_all(sid, current_user, request_access_data, parent_id=parent_id)
