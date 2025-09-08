import logging
from typing import List, Optional, TypeVar
from urllib.parse import parse_qs
from uuid import UUID

import socketio
from pydantic import BaseModel
from sqlmodel import SQLModel

from crud import register_crud
from routers.socketio.v1 import registry_namespaces, register_namespace
from core.config import config
from core.security import (
    check_token_against_guards,
    get_token_payload_from_cache,
)
from core.types import CurrentUserData, EventGuard, GuardTypes
from crud.access import AccessLoggingCRUD, AccessPolicyCRUD
from models.access import (
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessPolicyUpdate,
    BaseHierarchyCreate,
)

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


BaseSchemaTypeRead = TypeVar("BaseSchemaTypeRead", bound=SQLModel)


class SocketIoSessionData(BaseModel):
    """Data stored in the socket.io session."""

    user_name: str
    current_user: CurrentUserData
    session_id: str  # That's the Redis session-id, not the socket.io session-id (sid)


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
        register_crud(crud()) if crud is not None else None
        register_namespace(crud(), namespace) if crud is not None else None
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
        self, sid, current_user: CurrentUserData, request_access_data: bool = False
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
                    item.access_policies = access_data["access_policies"]
                    item.creation_date = access_data["creation_date"]
                    item.last_modified_date = access_data["last_modified_date"]
                if item.id not in self.server.rooms(sid, self.namespace):
                    await self.server.enter_room(
                        sid, f"resource:{str(item.id)}", namespace=self.namespace
                    )
                await self.server.emit(
                    "transferred",
                    item.model_dump(mode="json"),
                    namespace=self.namespace,
                    to=sid,
                )
        except Exception as error:
            logger.error(f"Failed to get all data for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    async def _get_access_data(self, sid, current_user, resource_id: UUID):
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
                    current_user, resource_id=resource_id
                )
            except Exception:
                creation_date = None
                last_modified_date = None
        # TBD: add typing AccessData for access_data
        access_data = {
            "access_right": access_permission.action,
            "access_policies": access_policies if access_policies else None,
            "creation_date": creation_date if creation_date else None,
            "last_modified_date": last_modified_date if last_modified_date else None,
        }
        return access_data
        # {
        # "access_right": access_permission.action,
        # "access_policies": access_policies,
        # "creation_date": creation_date,
        #     "last_modified_date": last_modified_date,
        # }

    async def _emit_status(
        self,
        sid,
        data: object,
        rooms: Optional[List[str]] = None,
        namespace: str = None,
    ):
        """Emit a status event to the client."""
        receivers = [sid]
        if rooms is not None:
            receivers += rooms
        if namespace is None:
            namespace = self.namespace
        await self.server.emit(
            "status",
            data,
            namespace=namespace,
            to=receivers,  # TBD: consider adding admin room here
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
        # print("=== routers - socketio - v1 - on_connect - parse_qs(query_strings) ===")
        # print(parse_qs(query_strings), flush=True)
        request_access_data = (
            parse_qs(query_strings).get("request-access-data")[0]
            if "request-access-data" in query_strings
            else None
        )
        identity_ids = (
            parse_qs(query_strings).get("identity-ids")[0].split(",")
            if "identity-ids" in query_strings
            else []
        )
        resource_ids = (
            parse_qs(query_strings).get("resource-ids")[0].split(",")
            if "resource-ids" in query_strings
            else []
        )
        # TBD: consider switching the if and for
        for identity_id in identity_ids:
            if identity_id:
                # Assign the identity id to the room for hierarchical resource system
                await self.server.enter_room(
                    sid, f"identity:{identity_id}", namespace=self.namespace
                )
                logger.info(
                    f"🧦 Client with session id {sid} entered room {identity_id}."
                )
        # TBD: consider only relying on information from the backend
        # instead of retrieving identities from client side!
        # But allow the frontend client to request identity spaces!
        # print("=== routers - socketio - v1 - on_connect - identity_ids ===")
        # print(identity_ids, flush=True)
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
                    "query_strings": query_strings,
                }
                await self.server.save_session(
                    sid, session_data, namespace=self.namespace
                )
                if "Admin" in current_user.azure_token_roles:
                    await self.server.enter_room(
                        sid,
                        "role:Admin",
                        namespace=self.namespace,
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
        if self.callback_on_connect is not None:
            await self.callback_on_connect(
                sid,
                current_user=current_user,
                request_access_data=request_access_data,
                resource_ids=resource_ids,
            )

    async def on_read(self, sid, resource_id: Optional[UUID] = None):
        """Read event for socket.io namespaces."""
        logger.info(f"🧦 Read request from client {sid} for resource {resource_id}.")
        try:
            # read event has same guards as on_connect
            # why would a user otherwise be allowed to connect,
            # if not even allowed to read anything?
            current_user = await self._get_current_user_and_check_guard(sid, "connect")
            async with self.crud() as crud:
                session = await self._get_session_data(sid)
                request_access_data = (
                    parse_qs(session["query_strings"]).get("request-access-data")[0]
                    if "request-access-data" in session["query_strings"]
                    else None
                )
                if resource_id is None:
                    await self._get_all(sid, current_user, request_access_data)
                else:
                    database_object = await crud.read_by_id(resource_id, current_user)
                    if self.read_model is not None:
                        database_object = self.read_model.model_validate(
                            database_object
                        )
                    if request_access_data:
                        access_data = await self._get_access_data(
                            sid, current_user, database_object.id
                        )
                        database_object = self.read_extended_model.model_validate(
                            database_object
                        )
                        database_object.access_right = access_data["access_right"]
                        database_object.access_policies = access_data["access_policies"]
                        database_object.creation_date = access_data["creation_date"]
                        database_object.last_modified_date = access_data[
                            "last_modified_date"
                        ]
                    if database_object.id not in self.server.rooms(sid, self.namespace):
                        await self.server.enter_room(
                            sid,
                            f"resource:{str(database_object.id)}",
                            namespace=self.namespace,
                        )
                    await self.server.emit(
                        "transferred",
                        database_object.model_dump(mode="json"),
                        namespace=self.namespace,
                        to=sid,
                    )
                    # await self.server.enter_room(
                    #     sid,
                    #     f"resource:{str(database_object.id)}",
                    #     namespace=self.namespace,
                    # )
        except Exception as error:
            logger.error(f"🧦 Failed to read data from client {sid}.")
            print(error)
            # In case user was accessing a resource after an unshare event:
            await self.server.emit(
                "deleted",
                resource_id,
                namespace=self.namespace,
                to=sid,
            )
            # TBD: consider changing this - can be misleading:
            # it's not necessarily deleted: might be the user's access has changed.
            await self._emit_status(sid, {"success": "deleted", "id": str(resource_id)})
            await self._emit_status(
                sid, {"error": f"Resource {str(resource_id)} not found."}
            )
            # await self._emit_status(sid, {"error": str(error)})

    # "submit" is communication from client to server
    async def on_submit(self, sid, data):
        """Gets data from client and issues a create or update based on id is present or not."""
        logger.info(f"🧦 Data submitted from client {sid}")
        try:
            if self.crud is not None:
                payload = data.get("payload", None)
                try:
                    database_object = None
                    if (
                        "id" in payload and payload["id"][:4] != "new_"
                    ):  # validate if id is a valid UUID
                        current_user = await self._get_current_user_and_check_guard(
                            sid, "submit:update"
                        )
                        resource_id = UUID(payload["id"])
                        # if id is present, it is an update
                        # validate data with update model
                        object_update = self.update_model(**payload)
                        async with self.crud() as crud:
                            # TBD: check the hierarchical resource system all the way through other events as
                            database_object = await crud.update(
                                current_user, resource_id, object_update
                            )
                            # if updating user is not in the resource room yet, add that user:
                            if database_object.id not in self.server.rooms(
                                sid, self.namespace
                            ):
                                await self.server.enter_room(
                                    sid,
                                    f"resource:{str(database_object.id)}",
                                    namespace=self.namespace,
                                )
                            # transfer after update is necessary for other clients,
                            # which are in the same room of this resource_id to get the updated data
                            await self.server.emit(
                                "transferred",
                                database_object.model_dump(mode="json"),
                                namespace=self.namespace,
                                to=f"resource:{str(database_object.id)}",
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
                        object_create = self.create_model(**payload)
                        parent_id = data.get("parent_id", None)
                        inherit = data.get("inherit", False)
                        async with self.crud() as crud:
                            # TBD: check the hierarchical resource system all the way through other events as well!
                            database_object = await crud.create(
                                object_create, current_user, parent_id, inherit
                            )
                            await self.server.enter_room(
                                sid,
                                f"resource:{str(database_object.id)}",
                                namespace=self.namespace,
                            )
                            await self._emit_status(
                                sid,
                                {
                                    "success": "created",
                                    "id": str(database_object.id),
                                    "submitted_id": payload.get("id", None),
                                },
                            )
                            # transfer after create is necessary for other clients,
                            await self.server.emit(
                                "status",
                                {
                                    "success": "shared",
                                    "id": str(database_object.id),
                                },
                                namespace=self.namespace,
                                to=["role:Admin"],
                            )
                    # if database_object is not None:
                    #     await self.server.emit(
                    #         "transferred",
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
                # "transferred" is communication from server to client
                self.server.emit(
                    "transferred",
                    data,
                    namespace=self.namespace,
                )
        except Exception as error:
            logger.error(f"🧦 Failed to write data from client {sid}.")
            await self._emit_status(sid, {"error": str(error)})

    async def on_delete(self, sid, entity_id: UUID):
        """Delete event for socket.io namespaces."""
        logger.info(f"🧦 Delete request from client {sid}.")
        try:
            current_user = await self._get_current_user_and_check_guard(sid, "delete")
            async with self.crud() as crud:
                await crud.delete(current_user, entity_id)
            await self.server.close_room(entity_id, namespace=self.namespace)
            await self.server.emit(
                "deleted",
                entity_id,
                namespace=self.namespace,
            )
            await self._emit_status(sid, {"success": "deleted", "id": entity_id})
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
            # print("===  socketio - SHARE - access_policy ===")
            # print(access_policy, flush=True)
            if "action" not in access_policy:
                access_policy = AccessPolicyDelete(**access_policy)
                async with AccessPolicyCRUD() as crud:
                    await crud.delete(current_user, access_policy)
                    # print("=== socketio - DELETE - access_policy ===", flush=True)
                    await self._emit_status(
                        sid,
                        {
                            "success": "unshared",
                            "id": str(access_policy.resource_id),
                        },
                        rooms=[f"identity:{str(access_policy.identity_id)}"],
                    )
                # print("=== socketio - DELETE - access_policy ===", flush=True)
            elif "new_action" not in access_policy:
                # print(
                #     "=== routers - socketio - v1 - on_share - CREATE - access_policy ==="
                # )
                # pprint(access_policy)
                access_policy = AccessPolicyCreate(**access_policy)
                async with AccessPolicyCRUD() as crud:
                    await crud.create(access_policy, current_user)
                # print("=== socketio - CREATE - access_policy ===", flush=True)
                await self._emit_status(
                    sid,
                    {
                        "success": "shared",
                        "id": str(access_policy.resource_id),
                    },
                    rooms=[f"identity:{access_policy.identity_id}"],
                )
                # print("=== socketio - CREATE - access_policy ===", flush=True)
            elif "action" != "new_action":
                access_policy = AccessPolicyUpdate(**access_policy)
                async with AccessPolicyCRUD() as crud:
                    await crud.update(current_user, access_policy)
                # print("=== socketio - UPDATE - access_policy ===", flush=True)
                await self._emit_status(
                    sid,
                    {
                        "success": "shared",
                        "id": str(access_policy.resource_id),
                    },
                    rooms=[f"identity:{str(access_policy.identity_id)}"],
                )
                # print("=== socketio - UPDATE - access_policy ===", flush=True)
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

    async def on_link(self, sid, hierarchy: BaseHierarchyCreate):
        """Link event for socket.io namespaces."""
        logger.info(f"🧦 Link request from client {sid}.")
        try:
            hierarchy = BaseHierarchyCreate(**hierarchy)
            current_user = await self._get_current_user_and_check_guard(
                sid, "submit:create"
            )
            async with self.crud() as crud:
                await crud.add_child_to_parent(
                    hierarchy.child_id,
                    hierarchy.parent_id,
                    current_user,
                    hierarchy.inherit,
                )
                parent_types = await crud._get_types_from_ids([hierarchy.parent_id])
                parent_type = parent_types[0].type if parent_types else None
            status = (
                {
                    "success": "linked",
                    "id": str(hierarchy.child_id),
                    "parent_id": str(hierarchy.parent_id),
                    "inherit": hierarchy.inherit,
                },
            )
            await self._emit_status(
                sid, status, [f"resource:{str(hierarchy.child_id)}"]
            )
            parent_namespace = registry_namespaces.get(parent_type)
            await self._emit_status(
                sid,
                status,
                [f"resource:{str(hierarchy.parent_id)}"],
                namespace=parent_namespace,
            )
        except Exception as error:
            logger.error(f"🧦 Failed to link item for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    # TBD: write tests for this:
    async def on_unlink(self, sid, hierarchy: BaseHierarchyCreate):
        """Unlink event for socket.io namespaces."""
        logger.info(f"🧦 Unlink request from client {sid}.")
        try:
            hierarchy = BaseHierarchyCreate(**hierarchy)
            current_user = await self._get_current_user_and_check_guard(
                sid, "submit:update"
            )
            async with self.crud() as crud:
                await crud.remove_child_from_parent(
                    hierarchy.child_id, hierarchy.parent_id, current_user
                )
                parent_types = await crud._get_types_from_ids([hierarchy.parent_id])
                parent_type = parent_types[0].type if parent_types else None
            status = (
                {
                    "success": "unlinked",
                    "id": str(hierarchy.child_id),
                    "parent_id": str(hierarchy.parent_id),
                },
            )
            await self._emit_status(
                sid,
                status,
                [
                    f"resource:{str(hierarchy.child_id)}",
                ],
            )
            parent_namespace = registry_namespaces.get(parent_type)
            # TBD: emit in both namespaces with only one emit,
            # that is change _emit_status to always include own namespace or
            # specify own namespace explicitly in argument namespaces?
            await self._emit_status(
                sid,
                status,
                [f"resource:{str(hierarchy.parent_id)}"],
                namespace=parent_namespace,
            )
        except Exception as error:
            logger.error(f"🧦 Failed to unlink item for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    async def on_disconnect(self, sid):
        """Disconnect event for socket.io namespaces."""
        logger.info(f"🧦 Client with session id {sid} disconnected.")
        if self.callback_on_disconnect is not None:
            await self.callback_on_disconnect(sid)
