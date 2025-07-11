import logging

from core.types import EventGuard, GuardTypes

from .base import BaseNamespace

# from crud.protected_resource import ProtectedResourceCRUD


logger = logging.getLogger(__name__)


# # @sio.event
# # async def demo_message(sid, data):
# #     """Demo message event for socket.io."""
# #     print("=== demo_events - demo_message ===", flush=True)
# #     logger.info(f"Received message from client {sid}: {data}")
# #     await sio.emit("message", f"Message received from client {sid}: {data}")

# protect the events with requirements for scopes, roles and groups in users access token
event_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
    )
]


class DemoNamespace(BaseNamespace):
    """Protected class for socket.io namespaces."""

    def __init__(self, namespace=None):
        super().__init__(
            namespace=namespace,
            event_guards=event_guards,
            # crud=ProtectedResourceCRUD,
            callback_on_connect=self.callback_on_connect,
            callback_on_disconnect=self.callback_on_disconnect,
        )
        # self.namespace = namespace

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        session = await self._get_session_data(sid)
        user_name = session["user_name"] if session else "ANONYMOUS"
        await self.server.emit(
            "demo_message",
            f"Welcome {user_name} to {self.namespace}.",
            namespace=self.namespace,
        )
        await self.server.emit(
            "demo_message",
            f"Your session ID is {sid}.",
            namespace=self.namespace,
            to=sid,
        )
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

    async def callback_on_disconnect(self, sid):
        """Callback on disconnect for socket.io namespaces."""
        logger.info(f"🧦 Client with session id {sid} disconnected.")
        session = await self._get_session_data(sid)
        # print("=== demo_namespace - callback_on_disconnect - session ===")
        # print(session, flush=True)
        user_name = session["user_name"] if session else "ANONYMOUS"
        # print(
        #     f"=== demo_namespace - callback_on_disconnect - session['user_name'] === {user_name}"
        # )
        # print(session["user_name"], flush=True)
        await self.server.emit(
            "demo_message",
            f"{user_name} has disconnected from /demo-namespace. Goodbye!",
            namespace=self.namespace,
        )
        # print(
        #     "=== demo_namespace - callback_on_disconnect - announcement sent to everyone ===",
        #     flush=True,
        # )
        await self.server.emit(
            "demo_message",
            f"Your session with ID {sid} is ending.",
            namespace=self.namespace,
            to=sid,
        )
        # print(
        #     "=== demo_namespace - callback_on_disconnect - goodbye message sent to client ===",
        #     flush=True,
        # )
        await self.server.sleep(3)  # Give time for the messages to be sent
        return "callback_on_disconnect"


demo_namespace_router = DemoNamespace("/demo-namespace")
# socketio_server.register_namespace(ProtectedEvents())
