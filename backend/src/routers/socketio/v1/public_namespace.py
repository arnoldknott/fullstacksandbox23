import logging

from core.security import AllowAnonymous, Guards, MicrosoftGuard
from core.types import EventGuard
from crud.public_resource import PublicResourceCRUD

from .base import BaseNamespace

logger = logging.getLogger(__name__)


public_event_guards = [
    EventGuard(event=event, guards=Guards(MicrosoftGuard(), AllowAnonymous())())
    for event in ("connect", "submit:create", "submit:update", "delete", "share")
]


class PublicNamespace(BaseNamespace):
    """Public demonstration namespace with explicit anonymous admission."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/public-namespace",
            event_guards=public_event_guards,
            crud=PublicResourceCRUD,
            *args,
            **kwargs,
        )

    async def on_public_message(self, sid, data):
        """Public message event for public socket.io namespace."""
        logger.info(f"Received message from client {sid}: {data}")
        await self.server.emit(
            "public_message",
            f"Message received in public namespace from client: {data}",
            namespace=self.namespace,
        )
