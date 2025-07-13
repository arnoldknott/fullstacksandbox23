from typing import List, Optional
import logging
from urllib.parse import parse_qs
from uuid import UUID
from pydantic import BaseModel
import socketio
from sqlmodel import SQLModel

from core.config import config
from core.security import (
    check_token_against_guards,
    get_token_payload_from_cache,
)
from models.access import AccessPolicyCreate, AccessPolicyUpdate
from core.types import CurrentUserData, EventGuard, GuardTypes
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD

logger = logging.getLogger(__name__)


class SocketIoSessionData(BaseModel):
    """Data stored in the socket.io session."""

    user_name: str
    current_user: CurrentUserData
    session_id: str  # That's the Redis session-id, not the socket.io session-id (sid)


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
        event_guards: List[EventGuard] = [],
        crud=None,
        create_model: SQLModel = None,
        read_model: SQLModel = None,
        read_extended_model: SQLModel = None,
        update_model: SQLModel = None,
        callback_on_connect=None,
        callback_on_disconnect=None,
    ):
        super().__init__(namespace=namespace)
        self.event_guards = event_guards
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

    async def _get_token_payload_if_authenticated(
        self, session_id: str
    ) -> Optional[dict]:
        """Get the token payload from the cache if authenticated."""
        logger.info("🧦 Getting token payload from cache")
        token_payload = await get_token_payload_from_cache(
            session_id, [f"api://{config.API_SCOPE}/socketio"]
        )
        if not token_payload:
            raise ConnectionRefusedError("Authorization failed.")
        return token_payload

    def _get_event_guards(self, event: str) -> Optional[GuardTypes]:
        """Get the guards for the event."""
        if self.event_guards:
            guard = next(
                (guard.guards for guard in self.event_guards if guard.event == event),
                None,
            )
            return guard
        return None

    async def _get_session_data(self, sid) -> Optional[SocketIoSessionData]:
        """Get socketio session data from the socketio server."""
        logger.info(f"🧦 Get session data for client with session id {sid}.")
        try:
            return await self.server.get_session(sid, namespace=self.namespace)
        except Exception as err:
            logger.error(
                f"Failed to get session data for client with session id {sid}."
            )
            logger.error(err)

    async def _get_current_user_and_check_guard(
        self, sid, guard_name: str
    ) -> CurrentUserData:
        """Check the auth token against the event guards."""

        current_user = None

        session = await self._get_session_data(sid)
        guards = self._get_event_guards(guard_name)
        if guards is not None:
            token_payload = await self._get_token_payload_if_authenticated(
                session["session_id"]
            )
        current_user = await check_token_against_guards(token_payload, guards)

        if current_user is None:
            logger.error(
                f"🧦 Client with session id {sid} is missing current_user data."
            )
            self._emit_status(sid, {"error": "No Current User found."})
        else:
            return current_user

    async def _get_all(
        self, sid, current_user: CurrentUserData, request_access_data=False
    ):
        """Get all event for socket.io namespaces."""
        logger.info(f"🧦 Get all data request from client {sid}.")
        try:
            async with self.crud() as crud:
                data = await crud.read(current_user)
            if self.read_model is not None:
                for idx, item in enumerate(data):
                    data[idx] = self.read_model.model_validate(item)
            for item in data:
                if request_access_data:
                    access_data = await self._get_access_data(
                        sid, current_user, item.id
                    )
                    item = self.read_extended_model.model_validate(item)
                    item.access_right = access_data["access_right"]
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

    async def _get_access_data(self, sid, current_user, resource_id=UUID):
        """Get access data from the socketio session."""
        logger.info(f"🧦 Get access data for resource {resource_id} for client {sid}.")
        # session = await self._get_session_data(sid)
        # Consider splitting the accesss policy and access log CRUDs into separate methods
        async with AccessPolicyCRUD() as policy_crud:
            access_permission = await policy_crud.check_access(
                current_user, resource_id
            )
            try:
                access_policies = await policy_crud.read_access_policies_by_resource_id(
                    current_user, resource_id
                )
            except Exception:
                access_policies = []
        async with AccessLoggingCRUD() as logging_crud:
            try:
                creation_date = await logging_crud.read_resource_created_at(
                    current_user, resource_id=resource_id
                )
                last_modified_date = await logging_crud.read_resource_last_modified_at(
                    current_user, resource_id
                )
            except Exception:
                creation_date = None
                last_modified_date = None
        return {
            "access_right": access_permission.action,
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
        logger.info(f"🧦 Client connected with session id: {sid}.")
        # Parse 'request-access-data' from query string using urllib.parse.parse_qs
        query_strings = environ.get("QUERY_STRING", "")
        print("=== routers - socketio - v1 - on_connect - parse_qs(query_strings) ===")
        print(parse_qs(query_strings), flush=True)

        request_access_data = (
            parse_qs(query_strings).get("request-access-data")[0]
            if "request-access-data" in query_strings
            else None
        )
        identity_ids = (
            parse_qs(query_strings).get("identity-id")[0].split(",")
            if "identity-id" in query_strings
            else []
        )
        print("=== routers - socketio - v1 - on_connect - identity_ids ===")
        print(identity_ids, flush=True)
        guards = self._get_event_guards("connect")
        if guards is not None:
            try:

                # TBD: catch and handle an expired token gracefully and return something to the client on a different message channel,
                # so it can initiate the authentication process and come back with a new session id
                token_payload = await self._get_token_payload_if_authenticated(
                    auth["session-id"]
                )
                current_user = await check_token_against_guards(token_payload, guards)
                session_data: SocketIoSessionData = {
                    "user_name": token_payload["name"],
                    # "current_user": current_user,
                    "session_id": auth["session-id"],
                }
                await self.server.save_session(
                    sid, session_data, namespace=self.namespace
                )
                logger.info(
                    f"🧦 Client authenticated to access protected namespace {self.namespace}."
                )
            except Exception:
                logger.error(f"🧦 Client with session id {sid} failed to authenticate.")
                raise ConnectionRefusedError("Authorization failed.")
        else:
            current_user = None
            logger.info(
                f"🧦 Client authenticated to public namespace {self.namespace}."
            )
        for identity_id in identity_ids:
            if identity_id:
                # Assign the identity id to the room for hierarchical resource system
                await self.server.enter_room(
                    sid, f"identity:{identity_id}", namespace=self.namespace
                )
                logger.info(
                    f"🧦 Client with session id {sid} entered room {identity_id}."
                )
        if self.callback_on_connect is not None:
            await self.callback_on_connect(
                sid, current_user=current_user, request_access_data=request_access_data
            )

    # "submit" is communication from client to server
    async def on_submit(self, sid, data):
        """Gets data from client and issues a create or update based on id is present or not."""
        logger.info(f"🧦 Data submitted from client {sid}")
        try:

            if self.crud is not None:
                try:
                    database_object = None
                    if (
                        "id" in data and data["id"][:4] != "new_"
                    ):  # validate if id is a valid UUID
                        current_user = await self._get_current_user_and_check_guard(
                            sid, "submit:update"
                        )
                        resource_id = UUID(data["id"])
                        # if id is present, it is an update
                        # validate data with update model
                        object_update = self.update_model(**data)
                        async with self.crud() as crud:
                            database_object = await crud.update(
                                current_user, resource_id, object_update
                            )
                            await self._emit_status(
                                sid,
                                {
                                    "success": "updated",
                                    "id": str(database_object.id),
                                },
                            )
                    else:
                        # if id is not present, it is a create
                        # validate data with create model
                        current_user = await self._get_current_user_and_check_guard(
                            sid, "submit:create"
                        )
                        object_create = self.create_model(**data)
                        async with self.crud() as crud:
                            # TBD: check the hierarchical resource system all the way through other events as well!
                            parent_id = data.get("parent_id", None)
                            inherit = data.get("inherit", False)
                            database_object = await crud.create(
                                object_create, current_user, parent_id, inherit
                            )
                            await self._emit_status(
                                sid,
                                {
                                    "success": "created",
                                    "id": str(database_object.id),
                                    "submitted_id": data.get("id"),
                                },
                            )
                    # if database_object is not None:
                    #     await self.server.emit(
                    #         "transfer",
                    #         database_object.model_dump(mode="json"),
                    #         namespace=self.namespace,
                    #         to=sid,
                    #     )
                except Exception as error:
                    logger.error(f"🧦 Failed to write data from client {sid}.")
                    print(error, flush=True)
                    await self._emit_status(sid, {"error": str(error)})
            else:
                # Distributes incoming data to all clients in the namespace
                # "transfer" is communication from server to client
                self.server.emit(
                    "transfer",
                    data,
                    namespace=self.namespace,
                )
        except Exception as error:
            logger.error(f"🧦 Failed to write data from client {sid}.")
            await self._emit_status(sid, {"error": str(error)})

    async def on_delete(self, sid, resource_id: UUID):
        """Delete event for socket.io namespaces."""
        logger.info(f"🧦 Delete request from client {sid}.")
        try:
            current_user = await self._get_current_user_and_check_guard(sid, "delete")
            async with self.crud() as crud:
                await crud.delete(current_user, resource_id)
            await self.server.emit(
                "deleted",
                resource_id,
                namespace=self.namespace,
            )
            await self._emit_status(sid, {"success": "deleted", "id": resource_id})
        except Exception as error:
            logger.error(f"🧦 Failed to delete item for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    async def on_share(
        self, sid, access_policy: AccessPolicyCreate | AccessPolicyUpdate
    ):
        """Share event for socket.io namespaces."""
        logger.info(f"🧦 Share request from client {sid}.")
        # TBD: validate the AccessPolicyCreate model!
        try:
            current_user = await self._get_current_user_and_check_guard(sid, "share")
            print("=== routers - socketio - v1 - on_share - access_policy ===")
            print(access_policy, flush=True)
            try:
                access_policy = AccessPolicyCreate(**access_policy)
                print(
                    "=== routers - socketio - v1 - on_share - access_policy is create ==="
                )
                print(access_policy, flush=True)
            except Exception as _error:
                try:
                    access_policy = AccessPolicyUpdate(**access_policy)
                    print(
                        "=== routers - socketio - v1 - on_share - access_policy is update ==="
                    )
                    print(access_policy, flush=True)
                except Exception as error:
                    logger.error(
                        f"🧦 Failed to validate access policy for client {sid}."
                    )
                    print(error, flush=True)
                    await self._emit_status(sid, {"error": str(error)})
        except Exception as error:
            logger.error(f"🧦 Failed update access attempted from client {sid}.")
            print(error, flush=True)
            await self._emit_status(sid, {"error": str(error)})

    #     try:
    #         async with self.crud() as crud:
    #             await crud.check_identifier_type_link(access_policy.resource_id)
    #             current_user = await self._get_current_user_and_check_guard(
    #                 sid, "share"
    #             )
    #             async with AccessPolicyCRUD() as crud:
    #                 await crud.create(access_policy, current_user)
    #         await self._emit_status(
    #             sid,
    #             {
    #                 "success": "shared",
    #                 "resource_id": access_policy.resource_id,
    #                 "identity_id": access_policy.identity_id,
    #                 "action": access_policy.action,
    #                 "public": access_policy.public,
    #             },
    #         )
    #     except Exception as error:
    #         logger.error(f"🧦 Failed to share item for client {sid}.")
    #         print(error)
    #         await self._emit_status(sid, {"error": str(error)})

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"🧦 Client with session id {sid} disconnected.")
        if self.callback_on_disconnect is not None:
            await self.callback_on_disconnect(sid)
