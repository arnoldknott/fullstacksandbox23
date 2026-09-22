from core.security import Guards, MicrosoftGuard

# import logging
from core.types import EventGuard
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
        guards=Guards(
            MicrosoftGuard(scopes=["socketio", "api.read"], roles=["User"])
        )(),
    ),
    EventGuard(
        event="submit:create",
        guards=Guards(
            MicrosoftGuard(scopes=["socketio", "api.write"], roles=["User"])
        )(),
    ),
    EventGuard(
        event="submit:update",
        guards=Guards(
            MicrosoftGuard(scopes=["socketio", "api.write"], roles=["User"])
        )(),
    ),
    EventGuard(
        event="delete",
        guards=Guards(
            MicrosoftGuard(scopes=["socketio", "api.write"], roles=["User"])
        )(),
    ),
    EventGuard(
        event="share",
        guards=Guards(
            MicrosoftGuard(scopes=["socketio", "api.write"], roles=["User"])
        )(),
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
            *args,
            **kwargs,
        )
        # self.namespace = namespace
