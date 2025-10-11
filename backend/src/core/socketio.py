import logging

from fastapi import FastAPI
from socketio import AsyncRedisManager, AsyncServer

from core.config import config
from routers.socketio.v1.demo_namespace import DemoNamespace
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from routers.socketio.v1.identities import (
    GroupNamespace,
    SubGroupNamespace,
    SubSubGroupNamespace,
    UeberGroupNamespace,
    UserNamespace,
)
from routers.socketio.v1.interactive_documentation import InteractiveDocumentation
from routers.socketio.v1.public_namespace import PublicNamespace

logger = logging.getLogger(__name__)

print("👍 🧦 Socket.IO started")

# TBD: adda check if REDIS_SOCKETIO_PASSWORD and REDIS_SOCKETIO_DB are set, else raise an error
redis_manager = AsyncRedisManager(
    f"redis://socketio:{config.REDIS_SOCKETIO_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_SOCKETIO_DB}",
    channel="socketio",
    logger=logger,
)


socketio_server = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # disable CORS in Socket.IO, as FastAPI handles CORS!
    logger=False,
    engineio_logger=False,  # prevents the ping and pong messages from being logged
    client_manager=redis_manager,
)


# unnecessary?
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


def mount_socketio_app(fastapi_app: FastAPI):

    socketio_server.register_namespace(PublicNamespace(server=socketio_server))
    socketio_server.register_namespace(DemoNamespace(server=socketio_server))
    socketio_server.register_namespace(DemoResourceNamespace(server=socketio_server))
    socketio_server.register_namespace(UserNamespace(server=socketio_server))
    socketio_server.register_namespace(UeberGroupNamespace(server=socketio_server))
    socketio_server.register_namespace(GroupNamespace(server=socketio_server))
    socketio_server.register_namespace(SubGroupNamespace(server=socketio_server))
    socketio_server.register_namespace(SubSubGroupNamespace(server=socketio_server))
    # socketio_server.register_namespace(presentation_interests_router)
    # TBD: refactor the interactive documentation
    # into more generic features, like polls, quizzes, surveys, etc.
    socketio_server.register_namespace(InteractiveDocumentation(server=socketio_server))

    if config.SOCKETIO_ADMIN_USERNAME and config.SOCKETIO_ADMIN_PASSWORD:
        socketio_server.instrument(
            auth={
                "username": config.SOCKETIO_ADMIN_USERNAME,
                "password": config.SOCKETIO_ADMIN_PASSWORD,
            }
        )
