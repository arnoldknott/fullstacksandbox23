import logging

import socketio

from core.config import config
from core.security import (
    check_token_against_guards,
    get_azure_token_payload,
    get_token_from_cache,
)
from core.types import GuardTypes

logger = logging.getLogger(__name__)

socketio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # disable CORS in Socket.IO, as FastAPI handles CORS!
    logger=False,
    engineio_logger=False,  # prevents the ping and pong messages from being logged
)

if config.SOCKETIO_ADMIN_USERNAME and config.SOCKETIO_ADMIN_PASSWORD:
    socketio_server.instrument(
        auth={
            "username": config.SOCKETIO_ADMIN_USERNAME,
            "password": config.SOCKETIO_ADMIN_PASSWORD,
        }
    )


@socketio_server.event
async def connect(sid):
    """Connect event for socket.io."""
    logger.warning(f"Client connected with session id: {sid} outside namespaces.")
    print(f"=== routers - socketio - v1 - connect - sid {sid} / outside namespaces ===")


@socketio_server.event
async def disconnect(sid):
    """Disconnect event for socket.io."""
    logger.warning(f"Client with session id {sid} disconnected / outside namespaces.")


@socketio_server.on("*")
async def catch_all(event, sid, data):
    """Catch all events for socket.io, that don't have an event handler defined."""
    logger.warning(
        f"Caught an event from client {sid} to event {event} in unassigned namespace."
    )
    print("=== routers - socketio - v1 - catch_all - event ===")
    print(event)
    print("=== routers - socketio - v1 - catch_all - sid ===")
    print(sid)
    print("=== routers - socketio - v1 - catch_all - data ===")
    print(data, flush=True)


# class PresentationInterests(socketio.AsyncNamespace):
#     """Handling presentation interests for socket.io."""

#     def __init__(self, namespace: str = None):
#         super().__init__(namespace=namespace)
#         self.average = {
#             "Repository": 0.0,
#             "Infrastructure": 0.0,
#             "Architecture": 0.0,
#             "Security": 0.0,
#             "Backend": 0.0,
#             "Frontend": 0.0,
#         }
#         self.count = {
#             "Repository": 0,
#             "Infrastructure": 0,
#             "Architecture": 0,
#             "Security": 0,
#             "Backend": 0,
#             "Frontend": 0,
#         }
#         self.comments = []

#     async def on_connect(self, sid, environ):
#         """Connect event for socket.io namespaces."""
#         logger.info(f"Client connected with session id: {sid}.")
#         for topic in self.average:
#             await self.emit(
#                 "averages",
#                 {
#                     "topic": topic,
#                     "average": self.average[topic],
#                     "count": self.count[topic],
#                 },
#                 to=sid,
#             )
#         for comment in self.comments:
#             await self.emit(
#                 "server_comments",
#                 {"topic": comment["topic"], "comment": comment["comment"]},
#                 to=sid,
#             )

#     async def on_disconnect(self, sid):
#         """Disconnect event for socket.io namespaces."""
#         logger.info(f"Client with session id {sid} disconnected.")

#     async def on_comments(self, sid, data):
#         """Presentation interests for socket.io."""
#         logger.info(f"Received message from client {sid}.")

#         self.comments.append({"topic": data["topic"], "comment": data["comment"]})
#         await self.emit(
#             "server_comments", {"topic": data["topic"], "comment": data["comment"]}
#         )

#         old_average = self.average[data["topic"]]
#         old_count = self.count[data["topic"]]

#         new_average = (old_average * old_count + data["value"]) / (old_count + 1)
#         self.count[data["topic"]] += 1
#         new_count = self.count[data["topic"]]
#         self.average[data["topic"]] = new_average

#         await self.emit(
#             "averages",
#             {"topic": data["topic"], "average": new_average, "count": new_count},
#         )


# presentation_interests_router = PresentationInterests("/presentation_interests")


class BaseNamespace(socketio.AsyncNamespace):
    """Base class for socket.io namespaces."""

    def __init__(
        self,
        namespace: str = None,
        room: str = None,
        guards: GuardTypes = None,
        crud=None,
        callback_on_connect=None,
        callback_on_disconnect=None,
    ):
        super().__init__(namespace=namespace)
        self.guards = guards
        self.crud = crud
        self.server = socketio_server
        self.namespace = namespace
        self.room = room
        self.callback_on_connect = callback_on_connect
        self.callback_on_disconnect = callback_on_disconnect

    async def _get_session_data(self, sid):
        """Get socketio session data from the socketio server."""
        try:
            return await self.server.get_session(sid, namespace=self.namespace)
        except Exception as err:
            logger.error(
                f"Failed to get session data for client with session id {sid}."
            )
            logger.error(err)

    async def callback_in_base_namespace(self):
        print("=== base - callback ===")
        return "callback"

    async def on_connect(
        self,
        sid,
        environ,
        auth=None,
    ):
        """Connect event for socket.io namespaces."""
        logger.info(f"Client connected with session id: {sid}.")
        guards = self.guards
        # print("=== base - on_connect - self.namespace ===")
        # print(self.namespace, flush=True)
        # print("=== base - on_connect - guards ===")
        # print(guards, flush=True)
        # print("=== base - on_connect - auth ===")
        # print(auth, flush=True)
        if guards is not None:
            try:
                # TBD: add get scopes from guards - potentially distinguish between MSGraph scopes and backendAPI scopes?!
                # token = await get_token_from_cache(auth["session_id"], ["User.Read"])
                # catch and handle an expired token gracefully and return something to the client on a different message channel,
                # so it can initiate the authentication process and come back with a new session id
                token = await get_token_from_cache(
                    auth["session_id"], [f"api://{config.API_SCOPE}/socketio"]
                )  # TBD: add get scopes from guards - potentially distinguish between MSGraph scopes and backendAPI scopes?!
                token_payload = await get_azure_token_payload(token)
                # print("=== base - on_connect - token_payload ===")
                # print(token_payload, flush=True)
                print("=== base - on_connect - token_payload - name ===")
                print(token_payload["name"], flush=True)
                current_user = await check_token_against_guards(token_payload, guards)
                session_data = {
                    "user_name": token_payload["name"],
                    "current_user": current_user,
                }
                print("=== base - on_connect - session_data ===")
                print(session_data, flush=True)
                await self.server.save_session(
                    sid, session_data, namespace=self.namespace
                )
                # print("=== base - on_connect - current_user ===")
                # print(current_user, flush=True)
                print("=== base - on_connect - session saved ===", flush=True)
                logger.info(
                    f"Client authenticated to access protected namespace {self.namespace}."
                )
            except Exception:
                logger.error(f"Client with session id {sid} failed to authenticate.")
                # print("=== base - on_connect - Exception ===")
                # print(err, flush=True)
                raise ConnectionRefusedError("Authorization failed")
        else:
            current_user = None
            logger.info(f"Client authenticated to public namespace {self.namespace}.")
        if self.callback_on_connect is not None:
            # This works:
            # print("=== base - on_connect - callback_on_connect ===")
            await self.callback_on_connect(sid)

        # current_user = await check_token_against_guards(token_payload, self.guards)
        # print("=== base - on_connect - sid - current_user ===")
        # print(current_user, flush=True)
        # await self.server.emit(
        #     "demo_message",
        #     f"Started session with id: {sid}",
        #     namespace=self.namespace,
        #     callback=self.callback_in_base_namespace,
        # )
        # TBD: should not return anything or potentially true?
        # return "OK from server"

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")
        if self.callback_on_disconnect is not None:
            await self.callback_on_disconnect(sid)
