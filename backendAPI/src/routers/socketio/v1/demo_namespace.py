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
            guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
            crud=ProtectedResourceCRUD,
            callback_on_connect=self.callback_on_connect,
        )
        # self.namespace = namespace

    async def callback_on_connect(self, sid):
        """Callback on connect for socket.io namespaces."""
        # print("=== demo_namespace - callback_on_connect - sid ===")
        # print(sid)
        # if self.server.get_session(sid):
        # session = await self.server.get_session(sid, namespace=self.namespace)
        session = await self._get_session_data(sid)
        # print("=== demo_namespace - callback_on_connect - session ===")
        # print(session, flush=True)
        user_name = session["user_name"] if session else "ANONYMOUS"
        # if session:
        await self.server.emit(
            "demo_message",
            f"Welcome {user_name} to {self.namespace}.",
            namespace=self.namespace,
        )
        # else:
        #     await self.server.emit(
        #         "demo_message",
        #         f"Welcome ANONYMOUS to {self.namespace}.",
        #         namespace=self.namespace,
        #     )
        return "callback_on_connect"

    async def on_demo_message(self, sid, data):
        """Demo message event for socket.io namespaces with guards."""
        session = await self._get_session_data(sid)
        user_name = session["user_name"] if session else "ANONYMOUS"
        await self.server.emit(
            "demo_message",
            f"{user_name}: {data}",
            namespace=self.namespace,
        )


demo_namespace_router = DemoNamespace("/demo-namespace")
# socketio_server.register_namespace(ProtectedEvents())
