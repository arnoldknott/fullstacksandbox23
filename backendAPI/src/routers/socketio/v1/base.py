import logging

import socketio

from core.security import get_azure_token_payload
from core.types import GuardTypes

logger = logging.getLogger(__name__)

# socketio_server = socketio.AsyncServer(async_mode="asgi")
socketio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # disable CORS in Socket.IO, as FastAPI handles CORS!
    logger=True,
    engineio_logger=True,
)

# print("=== routers - socketio - v1 - vars(socketio_server) ===")
# pprint(vars(socketio_server))
# print("=== routers - socketio - v1 - dir(socketio_server) ===")
# pprint(dir(socketio_server))
# print("=== routers - socketio - v1 - var(socketio_app) ===")
# pprint(socketio_app)
# print("=== routers - socketio - v1 - dir(socketio_app) ===")
# pprint(dir(socketio_app))
# print("=== routers - socketio - v1 - flush ===", flush=True)


# TBD: add auth as FastAPI Depends
@socketio_server.event
async def connect(sid, environ, auth):
    """Connect event for socket.io."""
    logger.info(f"Client connected with session id: {sid}.")
    # print("=== routers - socketio - v1 - connect - sid ===", flush=True)
    # print(sid, flush=True)
    # print("=== routers - socketio - v1 - environ ===", flush=True)
    # pprint(environ)
    # print("=== routers - socketio - v1 - auth ===", flush=True)
    # pprint(auth)
    # print(" ", flush=True)
    await socketio_server.emit("message", f"Hello new client with session id {sid}")
    # TBD: add rooms and namespaces?
    # TBD: or refuse connection
    # for example if authentication is not successful:
    # raise ConnectionRefusedError("Connection refused")


@socketio_server.event
async def disconnect(sid):
    """Disconnect event for socket.io."""
    logger.info(f"Client with session id {sid} disconnected.")
    print("=== routers - socketio - v1 - disconnect - sid ===")
    print(sid)


# TBD: don't log the data, as it may contain sensitive information!
@socketio_server.on("*")
async def catch_all(event, sid, data):
    """Catch all events for socket.io, that don't have an event handler defined."""
    logger.info(f"Caught event {data} from client {sid}.")
    print("=== routers - socketio - v1 - catch_all - event ===")
    print(event)
    print("=== routers - socketio - v1 - catch_all - sid ===")
    print(sid)
    print("=== routers - socketio - v1 - catch_all - data ===")
    print(data, flush=True)


@socketio_server.event
async def demo_message(sid, data):
    """Demo message event for socket.io."""
    logger.info(f"Received message from client {sid}: {data}")
    await socketio_server.emit("demo_message", f"Message received from client: {data}")


# @socketio_server.event(namespace="/protected_events")
# async def protected_message(sid, data):
#     """Protected message event for socket.io."""
#     logger.info(f"Received protected message from client {sid}: {data}")
#     await socketio_server.emit(
#         "protected_message",
#         f"Protected message received from client: {data}",
#         namespace="/protected_events",
#     )


class PresentationInterests(socketio.AsyncNamespace):
    """Handling presentation interests for socket.io."""

    def __init__(self, namespace: str = None):
        super().__init__(namespace=namespace)
        self.average = {
            "Repository": 0.0,
            "Infrastructure": 0.0,
            "Architecture": 0.0,
            "Security": 0.0,
            "Backend": 0.0,
            "Frontend": 0.0,
        }
        self.count = {
            "Repository": 0,
            "Infrastructure": 0,
            "Architecture": 0,
            "Security": 0,
            "Backend": 0,
            "Frontend": 0,
        }
        self.comments = []

    async def on_connect(self, sid, environ):
        """Connect event for socket.io namespaces."""
        logger.info(f"Client connected with session id: {sid}.")
        for topic in self.average:
            await self.emit(
                "averages",
                {
                    "topic": topic,
                    "average": self.average[topic],
                    "count": self.count[topic],
                },
            )
        for comment in self.comments:
            await self.emit(
                "server_comments",
                {"topic": comment["topic"], "comment": comment["comment"]},
            )

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")

    async def on_comments(self, sid, data):
        """Presentation interests for socket.io."""
        logger.info(f"Received message from client {sid}.")

        self.comments.append({"topic": data["topic"], "comment": data["comment"]})
        await self.emit(
            "server_comments", {"topic": data["topic"], "comment": data["comment"]}
        )

        old_average = self.average[data["topic"]]
        old_count = self.count[data["topic"]]

        new_average = (old_average * old_count + data["value"]) / (old_count + 1)
        self.count[data["topic"]] += 1
        new_count = self.count[data["topic"]]
        self.average[data["topic"]] = new_average

        await self.emit(
            "averages",
            {"topic": data["topic"], "average": new_average, "count": new_count},
        )


presentation_interests_router = PresentationInterests("/presentation_interests")


# TBD: rename into BaseNamespace!
class BaseEvents(socketio.AsyncNamespace):
    """Base class for socket.io namespaces."""

    def __init__(
        self,
        namespace: str = None,
        room: str = None,
        guards: GuardTypes = None,
        crud=None,
    ):
        super().__init__(namespace=namespace)
        self.guards = guards
        self.crud = crud
        self.server = socketio_server
        self.room = room

    async def callback(self):
        print("=== base - callback ===")
        return "callback"

    async def on_connect(
        self,
        sid,
        environ,
        auth=None,
    ):
        """Connect event for socket.io namespaces."""
        # TBD: add a try-except block around the authentication and return specific authentication failed error.
        guards = self.guards
        print("=== base - on_connect - sid ===")
        print(sid, flush=True)
        # print("=== base - on_connect - environ ===")
        # pprint(environ)
        print("=== base - on_connect - auth ===")
        print(auth, flush=True)
        print("=== base - on_connect - guards ===")
        print(guards, flush=True)
        logger.info(f"Client connected with session id: {sid}.")

        token_payload = await get_azure_token_payload(auth)
        print("=== base - on_connect - token_payload ===")
        print(token_payload, flush=True)

        # current_user = await check_token_against_guards(token_payload, self.guards)
        # print("=== base - on_connect - sid - current_user ===")
        # print(current_user, flush=True)
        emit_response = await self.server.emit(
            "protected_message",
            f"Hello new client with session id {sid}",
            namespace=self.namespace,
            callback=self.callback,
        )
        print("=== base - on_connect - emit_response ===")
        print(emit_response, flush=True)
        return "OK from server"

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")
