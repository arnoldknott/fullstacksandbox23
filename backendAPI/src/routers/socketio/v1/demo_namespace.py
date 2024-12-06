import logging

from core.types import GuardTypes
from crud.protected_resource import ProtectedResourceCRUD

from .base import BaseNamespace

logger = logging.getLogger(__name__)


# # @sio.event
# # async def demo_message(sid, data):
# #     """Demo message event for socket.io."""
# #     print("=== demo_events - demo_message ===", flush=True)
# #     logger.info(f"Received message from client {sid}: {data}")
# #     await sio.emit("message", f"Message received from client {sid}: {data}")


class DemoNamespace(BaseNamespace):
    """Protected class for socket.io namespaces."""

    def __init__(self, namespace=None):
        super().__init__(
            namespace=namespace,
            guards=GuardTypes(scopes=["sockets", "api.write"], roles=["User"]),
            crud=ProtectedResourceCRUD,
        )
        self.namespace = namespace

    async def on_demo_message(self, sid, data):
        """Demo message event for socket.io namespaces with guards."""
        logger.info(f"Received message from client {sid}: {data}")
        await self.server.emit(
            "demo_message",
            f"Demo message received from client: {data}",
            namespace=self.namespace,
        )


demo_namespace_router = DemoNamespace("/demo_namespace")
# socketio_server.register_namespace(ProtectedEvents())
