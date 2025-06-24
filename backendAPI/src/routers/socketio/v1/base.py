import logging
from urllib.parse import parse_qs
from uuid import UUID

import socketio
from sqlmodel import SQLModel
from core.config import config
from core.security import (
    check_token_against_guards,
    get_azure_token_payload,
    get_token_from_cache,
)
from core.types import GuardTypes
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD

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
        read_extended_model: SQLModel = None,
        update_model: SQLModel = None,
        callback_on_connect=None,
        callback_on_disconnect=None,
    ):
        super().__init__(namespace=namespace)
        self.guards = guards
        self.crud = crud
        self.create_model = create_model
        self.read_model = read_model
        self.read_extended_model = read_extended_model
        self.update_model = update_model
        self.server = socketio_server
        self.namespace = namespace
        self.room = room  # use in hierarchical resource system for parent resource id and/or identity (group) id? Can be assigned after authentication by using enter_room()
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

    async def _get_all(self, sid, request_access_data=False):
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
                if request_access_data:
                    access_data = await self._get_access_data(sid, item.id)
                    item = self.read_extended_model.model_validate(item)
                    item.user_right = access_data["user_right"]
                    if access_data["access_policies"]:
                        item.access_policies = access_data["access_policies"]
                    if access_data["creation_date"]:
                        item.creation_date = access_data["creation_date"]
                    if access_data["last_modified_date"]:
                        item.last_modified_date = access_data["last_modified_date"]
                await self.server.emit(
                    "transfer",
                    item.model_dump(mode="json"),
                    namespace=self.namespace,
                    to=sid,
                )
        except Exception as error:
            logger.error(f"Failed to get all data for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    async def _get_access_data(self, sid, resource_id=UUID):
        """Get access data from the socketio session."""
        session = await self._get_session_data(sid)
        # Consider splitting the accesss policy and access log CRUDs into separate methods
        async with AccessPolicyCRUD() as policy_crud:
            access_permission = await policy_crud.check_access(
                session["current_user"], resource_id
            )
            try:
                access_policies = await policy_crud.read_access_policies_by_resource_id(
                    session["current_user"], resource_id
                )
            except Exception:
                access_policies = []
        async with AccessLoggingCRUD() as logging_crud:
            try:
                creation_date = await logging_crud.read_resource_created_at(
                    session["current_user"], resource_id=resource_id
                )
                last_modified_date = await logging_crud.read_resource_last_modified_at(
                    session["current_user"], resource_id
                )
            except Exception:
                creation_date = None
                last_modified_date = None
        return {
            "user_right": access_permission.action,
            "access_policies": access_policies,
            "creation_date": creation_date,
            "last_modified_date": last_modified_date,
        }

    async def _emit_status(self, sid, data: object):
        """Emit a status event to the client."""
        await self.server.emit(
            "status",
            data,
            namespace=self.namespace,
            to=sid,
        )

    async def on_connect(
        self,
        sid,
        environ,
        auth=None,
    ):
        """Connect event for socket.io namespaces."""
        logger.info(f"Client connected with session id: {sid}.")
        # Parse 'request-access-data' from query string using urllib.parse.parse_qs
        query_string = environ.get("QUERY_STRING", "")
        request_access_data = parse_qs(query_string).get("request-access-data")
        if request_access_data:
            request_access_data = (
                True
                if (
                    request_access_data[0] == "true" or request_access_data[0] == "True"
                )
                else False
            )
        else:
            request_access_data = False
        # is_request-access-data = request-access-data == "true"
        # print(f"=== base - on_connect - sid: {sid} - request-access-data: {request-access-data} ===")
        # print(request-access-data, flush=True)
        guards = self.guards
        if guards is not None:
            try:
                # TBD: add get scopes from guards - potentially distinguish between MSGraph scopes and backendAPI scopes?!
                # catch and handle an expired token gracefully and return something to the client on a different message channel,
                # so it can initiate the authentication process and come back with a new session id
                token = await get_token_from_cache(
                    auth["session-id"], [f"api://{config.API_SCOPE}/socketio"]
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
                # await self._emit_status(sid, {"error": "Authorization failed."})
                raise ConnectionRefusedError("Authorization failed.")
        else:
            current_user = None
            logger.info(f"Client authenticated to public namespace {self.namespace}.")
        if self.callback_on_connect is not None:
            await self.callback_on_connect(sid, request_access_data=request_access_data)

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

    async def on_delete(self, sid, resource_id: UUID):
        """Delete event for socket.io namespaces."""
        logger.info(f"Delete request from client {sid}.")
        try:
            session = await self._get_session_data(sid)
            async with self.crud() as crud:
                await crud.delete(session["current_user"], resource_id)
            await self.server.emit(
                "remove",
                resource_id,
                namespace=self.namespace,
            )
            await self._emit_status(
                sid, {"success": f"Item with id {resource_id} deleted successfully."}
            )
        except Exception as error:
            logger.error(f"Failed to delete item for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"Client with session id {sid} disconnected.")
        if self.callback_on_disconnect is not None:
            await self.callback_on_disconnect(sid)
