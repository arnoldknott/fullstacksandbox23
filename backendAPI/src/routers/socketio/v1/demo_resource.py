# import logging

from .base import BaseNamespace

from core.types import EventGuard, GuardTypes
from crud.demo_resource import DemoResourceCRUD
from models.demo_resource import (
    DemoResourceCreate,
    DemoResourceExtended,
    DemoResourceRead,
    DemoResourceUpdate,
)

# logger = logging.getLogger(__name__)

# protect the events with requirements for scopes, roles and groups in users access token
event_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    )
]


class DemoResourceNamespace(BaseNamespace):
    """Socket.IO interface for Demo Resources."""

    def __init__(self, namespace=None):
        super().__init__(
            namespace=namespace,
            event_guards=event_guards,
            crud=DemoResourceCRUD,
            create_model=DemoResourceCreate,
            read_model=DemoResourceRead,
            read_extended_model=DemoResourceExtended,
            update_model=DemoResourceUpdate,
            callback_on_connect=self.callback_on_connect,
        )
        # self.namespace = namespace

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all demo resources:
        await self._get_all(sid, *args, **kwargs)


demo_resource_router = DemoResourceNamespace("/demo-resource")
