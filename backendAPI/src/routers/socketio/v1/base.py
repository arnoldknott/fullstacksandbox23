import logging

import socketio
from sqlmodel import SQLModel

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


class BaseNamespace(socketio.AsyncNamespace):
    """Base class for socket.io namespaces."""

    def __init__(
        self,
        namespace: str = None,
        room: str = None,
        guards: GuardTypes = None,
        crud=None,
        create_model: SQLModel = None,
        read_model: SQLModel = None,
        update_model: SQLModel = None,
        callback_on_connect=None,
        callback_on_disconnect=None,
    ):
        super().__init__(namespace=namespace)
        self.guards = guards
        self.crud = crud
        self.create_model = create_model
        self.read_model = read_model
        self.update_model = update_model
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

    async def on_connect(
        self,
        sid,
        environ,
        auth=None,
    ):
        """Connect event for socket.io namespaces."""
        logger.info(f"Client connected with session id: {sid}.")
        guards = self.guards
        if guards is not None:
            try:
                # TBD: add get scopes from guards - potentially distinguish between MSGraph scopes and backendAPI scopes?!
                # catch and handle an expired token gracefully and return something to the client on a different message channel,
                # so it can initiate the authentication process and come back with a new session id
                token = await get_token_from_cache(
                    auth["session_id"], [f"api://{config.API_SCOPE}/socketio"]
                )
                token_payload = await get_azure_token_payload(token)
                current_user = await check_token_against_guards(token_payload, guards)
                session_data = {
                    "user_name": token_payload["name"],
                    "current_user": current_user,
                }
                await self.server.save_session(
                    sid, session_data, namespace=self.namespace
                )
                logger.info(
                    f"Client authenticated to access protected namespace {self.namespace}."
                )
            except Exception:
                logger.error(f"Client with session id {sid} failed to authenticate.")
                raise ConnectionRefusedError("Authorization failed")
        else:
            current_user = None
            logger.info(f"Client authenticated to public namespace {self.namespace}.")
        if self.callback_on_connect is not None:
            await self.callback_on_connect(sid)

    async def on_transfer(self, sid, data):
        """Transfer (write, read and update) event for socket.io namespaces."""
        logger.info(f"Exchanged data with client {sid}")
        if self.crud is not None:
            try:
                # handle incoming data and put back on this event handler
                print("=== base - on_transfer - sid ===")
                print(sid, flush=True)
            except Exception as err:
                logger.error(f"Failed to exchange data with client {sid}.")
                print(err)
        else:
            # Distributes incoming data to all clients in the namespace
            self.server.emit(
                "transfer",
                data,
                namespace=self.namespace,
            )

    async def on_get_all(self, sid):
        """Get all event for socket.io namespaces."""
        logger.info(f"Get all data request from client {sid}.")
        try:
            session = await self._get_session_data(sid)
            async with self.crud() as crud:
                data = await crud.read(session["current_user"])
            if self.read_model is not None:
                for idx, item in enumerate(data):
                    data[idx] = self.read_model.model_validate(item)
            for item in data:
                await self.server.emit(
                    "transfer",
                    item.model_dump(mode="json"),
                    namespace=self.namespace,
                    to=sid,
                )
        except Exception as error:
            logger.error(f"Failed to get all data for client {sid}.")
            print(error)
            # TBD: return an error message to the client - either on "transfer" or a dedicated "error" event

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")
        if self.callback_on_disconnect is not None:
            await self.callback_on_disconnect(sid)
