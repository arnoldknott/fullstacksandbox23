import logging

from crud.public_resource import PublicResourceCRUD

from .base import BaseNamespace

logger = logging.getLogger(__name__)


class PublicNamespace(BaseNamespace):
    """Protected class for socket.io namespaces."""

    def __init__(self):
        super().__init__(
            namespace="/public-namespace",
            crud=PublicResourceCRUD,
        )

    async def on_public_message(self, sid, data):
        """Public message event for public socket.io namespace."""
        logger.info(f"Received message from client {sid}: {data}")
        await self.server.emit(
            "public_message",
            f"Message received in public namespace from client: {data}",
            namespace=self.namespace,
        )


public_namespace_router = PublicNamespace()
