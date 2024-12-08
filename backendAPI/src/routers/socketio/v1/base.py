import logging

import socketio

from core.config import config
from core.security import get_azure_token_payload, get_token_from_cache
from core.types import GuardTypes

logger = logging.getLogger(__name__)

# socketio_server = socketio.AsyncServer(async_mode="asgi")
socketio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # disable CORS in Socket.IO, as FastAPI handles CORS!
    logger=True,
    engineio_logger=False,  # prevents the ping and pong messages from being logged
)


# TBD: add auth as FastAPI Depends
@socketio_server.event
async def connect(sid, environ, auth):
    """Connect event for socket.io."""
    logger.info(f"Client connected with session id: {sid}.")
    # print("=== routers - socketio - v1 - connect - sid ===", flush=True)
    # print(sid, flush=True)
    # print("=== routers - socketio - v1 - environ ===")
    # pprint(environ)
    # print("=== routers - socketio - v1 - auth['session_io'] ===")
    # pprint(auth["session_id"])
    # print(" ", flush=True)
    try:
        # await get_token_from_cache(auth["session_id"], ["User.Read"])
        # Works:
        # token = await get_token_from_cache(auth["session_id"])
        # print("=== routers - socketio - v1 - token ===")
        # print(token)
        # print(" ", flush=True)
        await socketio_server.emit("message", f"Hello new client with session id {sid}")
    except Exception as err:
        logger.error(f"Client with session id {sid} failed to authenticate.")
        print("=== routers - socketio - v1 - Exception ===")
        print(err, flush=True)
        raise ConnectionRefusedError("Authorization failed")
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
    logger.info(f"Caught an event {data} from client {sid}.")
    print("=== routers - socketio - v1 - catch_all - event ===")
    print(event)
    print("=== routers - socketio - v1 - catch_all - sid ===")
    print(sid)
    print("=== routers - socketio - v1 - catch_all - data ===")
    print(data, flush=True)


# TBD: refactor into always using the BaseNamespace!
@socketio_server.event
async def public_message(sid, data):
    """Public message event for socket.io."""
    logger.info(f"Received message from client {sid}: {data}")
    await socketio_server.emit(
        "public_message", f"Message received from client: {data}"
    )


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
                to=sid,
            )
        for comment in self.comments:
            await self.emit(
                "server_comments",
                {"topic": comment["topic"], "comment": comment["comment"]},
                to=sid,
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


class BaseNamespace(socketio.AsyncNamespace):
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
        try:
            guards = self.guards
            print("=== base - on_connect - guards ===")
            print(guards, flush=True)
            print("=== base - on_connect - auth ===")
            print(auth, flush=True)
            logger.info(f"Client connected with session id: {sid}.")
            # TBD: add get scopes from guards - potentially distinguish between MSGraph scopes and backendAPI scopes?!
            # token = await get_token_from_cache(auth["session_id"], ["User.Read"])
            token = await get_token_from_cache(
                auth["session_id"], [f"api://{config.API_SCOPE}/socketio"]
            )  # TBD: add get scopes from guards - potentially distinguish between MSGraph scopes and backendAPI scopes?!
            token_payload = await get_azure_token_payload(token)
            print("=== base - on_connect - token_payload ===")
            print(token_payload, flush=True)
        except Exception as err:
            logger.error(f"Client with session id {sid} failed to authenticate.")
            print("=== base - on_connect - Exception ===")
            print(err, flush=True)
            raise ConnectionRefusedError("Authorization failed")

        # current_user = await check_token_against_guards(token_payload, self.guards)
        # print("=== base - on_connect - sid - current_user ===")
        # print(current_user, flush=True)
        await self.server.emit(
            "demo_message",
            f"Started session with id: {sid}",
            namespace=self.namespace,
            callback=self.callback,
        )
        # TBD: should not return anything or potentially true?
        # return "OK from server"

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")
