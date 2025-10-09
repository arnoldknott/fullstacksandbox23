import logging

import socketio

from core.config import config

logger = logging.getLogger(__name__)

redis_manager = socketio.AsyncRedisManager(
    f"redis://socketio:{config.REDIS_SOCKETIO_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_SOCKETIO_DB}",
    channel="socketio",
    logger=logger,
)

socketio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # disable CORS in Socket.IO, as FastAPI handles CORS!
    logger=False,
    engineio_logger=False,  # prevents the ping and pong messages from being logged
    client_manager=redis_manager,
)

if config.SOCKETIO_ADMIN_USERNAME and config.SOCKETIO_ADMIN_PASSWORD:
    socketio_server.instrument(
        auth={
            "username": config.SOCKETIO_ADMIN_USERNAME,
            "password": config.SOCKETIO_ADMIN_PASSWORD,
        }
    )
