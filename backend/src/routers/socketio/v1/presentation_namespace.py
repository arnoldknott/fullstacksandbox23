import logging

from core.security import AllowAnonymous, Guards, LinkedInGuard, MicrosoftGuard
from core.types import EventGuard
from crud.presentation import PresentationCRUD
from models.presentation import Presentation

from .base import BaseNamespace

logger = logging.getLogger(__name__)

guards = [
    EventGuard(
        event="connect",
        guards=Guards(MicrosoftGuard(), LinkedInGuard(), AllowAnonymous())(),
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
            *args,
            **kwargs,
        )
