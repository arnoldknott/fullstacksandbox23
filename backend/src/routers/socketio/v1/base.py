import logging
from typing import Any, Dict, List, Optional, Type, TypedDict, TypeVar
from urllib.parse import parse_qs
from uuid import UUID

import socketio
from sqlmodel import SQLModel

from core.config import config
from core.security import (
    check_token_against_guards,
    get_token_payload_from_cache,
)
from core.types import (
    Action,
    CurrentUserData,
    EventGuard,
    GuardTypes,
    IdentityType,
    ResourceType,
)
from crud import register_crud
from crud.access import (
    AccessLoggingCRUD,
    AccessPolicyCRUD,
)
from models.access import (
    AccessPolicyCreate,
    AccessPolicyDelete,
    AccessPolicyUpdate,
    BaseHierarchyCreate,
)
from routers.socketio.v1 import register_namespace, registry_namespaces

logger = logging.getLogger(__name__)


BaseSchemaTypeRead = TypeVar("BaseSchemaTypeRead", bound=SQLModel)


class SocketIoSessionData(TypedDict, total=False):
    """Data stored in the socket.io session."""

    user_name: str
    # current_user: CurrentUserData
    # session_id below is the Redis session-id, not the socket.io session-id (sid)
    session_id: Optional[str]
    query_strings: Optional[str]


class BaseNamespace(socketio.AsyncNamespace):
    """Base class for socket.io namespaces."""

    def __init__(
        self,
        server: socketio.AsyncServer,
        namespace: Optional[str] = None,
        room: Optional[str] = None,
        event_guards: List[EventGuard] = [],
        crud=None,
        create_model: Optional[Type[SQLModel]] = None,
        read_model: Optional[Type[SQLModel]] = None,
        read_extended_model: Optional[Type[SQLModel]] = None,
        update_model: Optional[Type[SQLModel]] = None,
        callback_on_connect=None,
        callback_on_disconnect=None,
    ):
        super().__init__(namespace=namespace)
        self.event_guards = event_guards
        self.crud = crud
        if crud is not None:
            register_crud(crud())
            register_namespace(crud(), namespace)
        self.create_model = create_model
        self.read_model = read_model
        self.read_extended_model = read_extended_model
        self.update_model = update_model
        self.server = server
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
    ) -> Optional[CurrentUserData]:
        """Check the auth token against the event guards."""

        current_user = None

        session = await self._get_session_data(sid)
        guards = self._get_event_guards(guard_name)
        ### This solution works for none-protected events, but a user is logged in anyways:
        # try:
        #     token_payload = await self._get_token_payload_if_authenticated(
        #         session["session_id"]
        #     )
        #     current_user = await check_token_against_guards(token_payload, guards)
        # except Exception as _error:
        #     logger.info(f"🧦 Client with session id {sid} authenticated.")

        # if guards is not None and current_user is None:
        #     logger.error(
        #         f"🧦 Client with session id {sid} is missing current_user data."
        #     )
        #     self._emit_status(sid, {"error": "No Current User found."})
        # return current_user

        try:
            session_id = session.get("session_id") if session is not None else None
            if session_id is None:
                raise ConnectionRefusedError("No session id.")
            token_payload = await self._get_token_payload_if_authenticated(session_id)
            current_user = await check_token_against_guards(token_payload, guards)
        except Exception as error:
            if guards is not None:
                if current_user is None:
                    logger.error(
                        # f"🧦 Client with session id {sid} is missing current_user data."
                        f"🧦 Failed to authenticate client {sid}."
                    )
                    # self._emit_status(sid, {"error": "No Current User found."})
                    # await self._emit_status(sid, {"error": str(error)})
                raise error
            else:
                logger.info(
                    f"🧦 Client {sid} accessing namespace {self.namespace} publically."
                )
        return current_user

    async def _get_all(  # noqa: C901
        self,
        sid,
        current_user: Optional[CurrentUserData] = None,
        request_access_data: bool = False,
        parent_id: Optional[UUID] = None,
    ):
        """Get all event for socket.io namespaces."""
        logger.info(f"🧦 Get all data request from client {sid}.")
        if self.crud is None:
            return
        try:
            async with self.crud() as crud:
                data = await crud.read(current_user)

                allowed_child_ids = None
                if parent_id:
                    try:
                        parent_uuid = (
                            parent_id
                            if isinstance(parent_id, UUID)
                            else UUID(str(parent_id))
                        )
                        # if crud.model.__name__ in ResourceType.list():
                        async with crud.hierarchy_CRUD() as hierarchy_crud:
                            hierarchies = await hierarchy_crud.read(
                                current_user=current_user, parent_id=parent_uuid
                            )
                            allowed_child_ids = {h.child_id for h in hierarchies}
                        # elif crud.model.__name__ in IdentityType.list():
                        #     async with IdentityHierarchyCRUD() as hierarchy_crud:
                        #         hierarchies = await hierarchy_crud.read(
                        #             current_user=current_user,
                        #             parent_id=parent_uuid
                        #         )
                        #         allowed_child_ids = {h.child_id for h in hierarchies}
                    except ValueError:
                        logger.error(f"Invalid parent_id UUID format: {parent_id}")
                        allowed_child_ids = (
                            set()
                        )  # Empty set = filter out everything, silently fails.

                if self.read_model is not None:
                    for idx, item in enumerate(data):
                        data[idx] = self.read_model.model_validate(item)

            for item in data:
                # Skip if parent_id filter is active and item is not a child
                if parent_id and item.id not in (allowed_child_ids or set()):  # type: ignore[attr-defined]
                    continue

                if request_access_data:
                    access_data = await self._get_access_data(
                        sid, current_user, item.id  # type: ignore[attr-defined]
                    )
                    assert self.read_extended_model is not None
                    item = self.read_extended_model.model_validate(item)
                    item.access_right = access_data["access_right"]  # type: ignore[attr-defined]
                    item.access_policies = access_data["access_policies"]  # type: ignore[attr-defined]
                    item.creation_date = access_data["creation_date"]  # type: ignore[attr-defined]
                    item.last_modified_date = access_data["last_modified_date"]  # type: ignore[attr-defined]
                if item.id not in self.server.rooms(sid, self.namespace or "/"):  # type: ignore[attr-defined]
                    await self.server.enter_room(
                        sid, f"resource:{str(item.id)}", namespace=self.namespace  # type: ignore[attr-defined]
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
                resource_id=resource_id, current_user=current_user
            )
            try:
                access_policies = await policy_crud.read_access_policies_by_resource_id(
                    current_user=current_user, resource_id=resource_id
                )
            except Exception:
                access_policies = []
        async with AccessLoggingCRUD() as logging_crud:
            try:
                creation_date = await logging_crud.read_resource_created_at(
                    resource_id=resource_id, current_user=current_user
                )
                last_modified_date = await logging_crud.read_resource_last_modified_at(
                    resource_id=resource_id, current_user=current_user
                )
            except Exception:
                logger.info(f"🧦 No access data found for {resource_id}.")
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
        namespace: Optional[str] = None,
    ):
        """Emit a status event to the client."""
        receivers = [sid, "role:Admin"]
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
            parse_qs(query_strings).get("request-access-data", [""])[0]
            if "request-access-data" in query_strings
            else None
        )
        request_access_data = (
            True
            if request_access_data == "true"
            or request_access_data == "True"
            or request_access_data
            else False
        )
        identity_ids = (
            parse_qs(query_strings).get("identity-ids", [""])[0].split(",")
            if "identity-ids" in query_strings
            else []
        )
        resource_ids = (
            parse_qs(query_strings).get("resource-ids", [""])[0].split(",")
            if "resource-ids" in query_strings
            else []
        )
        parent_id = (
            parse_qs(query_strings).get("parent-id", [""])[0]
            if "parent-id" in query_strings
            else ""
        )
        join_admin_room = (
            parse_qs(query_strings).get("join-admin-room", [""])[0]
            if "join-admin-room" in query_strings
            else ""
        )
        join_admin_room = (
            True
            if join_admin_room == "true" or join_admin_room == "True" or join_admin_room
            else False
        )
        # TBD: consider switching the if and for
        for identity_id in identity_ids:
            if identity_id:
                # Assign the identity id to the room for hierarchical resource system
                # TBD: Is access control necessary here?
                # AccessCRUD.allows(
                #   resource_id=identity_id,
                #   Action=Action.read
                #   identity_id=current_user.identity_id
                # )
                # Nothing is emitted here - the checks are done at reading, before transferring data!
                # If access is added here, move down to after authentication!
                # In cas it's added here, then also add the th try .. except as in submit,
                # that allows public access if no guards are set!
                await self.server.enter_room(
                    sid, f"identity:{identity_id}", namespace=self.namespace
                )
                logger.info(
                    f"🧦 Client with session id {sid} entered room {identity_id}."
                )
        if parent_id:
            await self.server.enter_room(
                sid, f"parent:{parent_id}", namespace=self.namespace
            )
        # TBD: consider only relying on information from the backend
        # instead of retrieving identities from client side!
        # But allow the frontend client to request identity spaces!
        # print("=== routers - socketio - v1 - on_connect - identity_ids ===")
        # print(identity_ids, flush=True)
        guards = self._get_event_guards("connect")
        ### THis solution works for none-protected events, but a user is logged in anyways:
        try:
            # TBD: catch and handle an expired token gracefully and return something to the client on a different message channel,
            # so it can initiate the authentication process and come back with a new session id
            auth_session_id = auth["session-id"] if auth else None
            if auth_session_id is None:
                raise ConnectionRefusedError("No session id provided.")
            token_payload = await self._get_token_payload_if_authenticated(
                auth_session_id
            )
            current_user = await check_token_against_guards(token_payload, guards)
            session_data: SocketIoSessionData = {
                "user_name": (token_payload or {}).get("name", ""),
                # "current_user": current_user,
                "session_id": auth_session_id,
                "query_strings": query_strings,
            }
            await self.server.save_session(sid, session_data, namespace=self.namespace)
            # if "Admin" in current_user.azure_token_roles:
            if (
                current_user is not None
                and "Admin" in (current_user.azure_token_roles or [])
                and join_admin_room
            ):
                await self.server.enter_room(
                    sid,
                    "role:Admin",
                    namespace=self.namespace,
                )
            logger.info(
                f"🧦 Client authenticated to access protected namespace {self.namespace}."
            )
        except Exception as error:
            if guards is not None:
                print(
                    "=== routers - socketio - v1 - on_connect - authentication error ==="
                )
                print(error, flush=True)
                logger.error(f"🧦 Client with session id {sid} failed to authenticate.")
                raise ConnectionRefusedError("Authorization failed.")
            else:
                current_user = None
                session_data: SocketIoSessionData = {
                    "user_name": "Anonymous",
                    "query_strings": query_strings,
                }
                await self.server.save_session(
                    sid, session_data, namespace=self.namespace
                )
                logger.info(
                    # f"🧦 Client authenticated to public namespace {self.namespace}."
                    f"🧦 Client {sid} accessing namespace {self.namespace} publically."
                )

        # if guards is not None:
        #     try:
        #         # TBD: catch and handle an expired token gracefully and return something to the client on a different message channel,
        #         # so it can initiate the authentication process and come back with a new session id
        #         token_payload = await self._get_token_payload_if_authenticated(
        #             auth["session-id"]
        #         )
        #         current_user = await check_token_against_guards(token_payload, guards)
        #         session_data: SocketIoSessionData = {
        #             "user_name": token_payload["name"],
        #             # "current_user": current_user,
        #             "session_id": auth["session-id"],
        #             "query_strings": query_strings,
        #         }
        #         await self.server.save_session(
        #             sid, session_data, namespace=self.namespace
        #         )
        #         if "Admin" in current_user.azure_token_roles:
        #             await self.server.enter_room(
        #                 sid,
        #                 "role:Admin",
        #                 namespace=self.namespace,
        #             )
        #         logger.info(
        #             f"🧦 Client authenticated to access protected namespace {self.namespace}."
        #         )
        #     except Exception:
        #         logger.error(f"🧦 Client with session id {sid} failed to authenticate.")
        #         raise ConnectionRefusedError("Authorization failed.")
        # else:
        #     current_user = None
        #     logger.info(
        #         f"🧦 Client authenticated to public namespace {self.namespace}."
        #     )
        if self.callback_on_connect is not None:
            await self.callback_on_connect(
                sid,
                current_user=current_user,
                request_access_data=request_access_data,
                resource_ids=resource_ids,
                parent_id=parent_id,
            )

    async def on_read(self, sid, resource_id: Optional[UUID] = None):
        """Read event for socket.io namespaces."""
        logger.info(f"🧦 Read request from client {sid} for resource {resource_id}.")
        try:
            # read event has same guards as on_connect
            # why would a user otherwise be allowed to connect,
            # if not even allowed to read anything?
            current_user = await self._get_current_user_and_check_guard(sid, "connect")
            if self.crud is None:
                return
            async with self.crud() as crud:
                session = await self._get_session_data(sid)
                session_query_strings = (
                    session.get("query_strings") if session is not None else ""
                ) or ""
                request_access_data = (
                    parse_qs(session_query_strings).get("request-access-data", [""])[0]
                    if "request-access-data" in session_query_strings
                    else None
                )
                request_access_data = (
                    True
                    if request_access_data == "true"
                    or request_access_data == "True"
                    or request_access_data
                    else False
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
                        guards = self._get_event_guards("connect")
                        assert self.read_extended_model is not None
                        database_object = self.read_extended_model.model_validate(
                            database_object
                        )
                        if guards is None and current_user is None:
                            creation_date = None
                            last_modified_date = None
                            try:
                                async with AccessLoggingCRUD() as logging_crud:
                                    creation_date = (
                                        await logging_crud.read_resource_created_at(
                                            resource_id=resource_id
                                        )
                                    )
                                    last_modified_date = await logging_crud.read_resource_last_modified_at(
                                        resource_id=resource_id
                                    )
                            except Exception:
                                logger.info(
                                    "Failed to get creation and modification dates with public access."
                                )
                                print(
                                    "=== routers - socketio - v1 - on_read - public access - failed to get dates ==="
                                )
                            database_object.access_right = Action.read
                            database_object.creation_date = creation_date
                            database_object.last_modified_date = last_modified_date
                        else:
                            access_data = await self._get_access_data(
                                sid, current_user, database_object.id  # type: ignore[attr-defined]
                            )
                            # database_object = self.read_extended_model.model_validate(
                            #     database_object
                            # )
                            database_object.access_right = access_data["access_right"]
                            database_object.access_policies = access_data[
                                "access_policies"
                            ]
                            database_object.creation_date = access_data["creation_date"]
                            database_object.last_modified_date = access_data[
                                "last_modified_date"
                            ]
                    if database_object.id not in self.server.rooms(sid, self.namespace or "/"):  # type: ignore[attr-defined]
                        await self.server.enter_room(
                            sid,
                            f"resource:{str(database_object.id)}",  # type: ignore[attr-defined]
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
    # TBD: remove noqa, when emiting the link status events is gathered in a separate method.
    async def on_submit(self, sid, data):  # noqa: C901
        """Gets data from client and issues a create or update based on id is present or not."""
        logger.info(f"🧦 Data submitted from client {sid}")
        try:
            if self.crud is not None:
                payload = data.get("payload", None)

                # Determine event name
                if "id" in payload and payload["id"][:4] != "new_":
                    event_name = "submit:update"
                else:
                    event_name = "submit:create"

                # Get guards for this event
                guards = self._get_event_guards(event_name)

                # Try to authenticate
                current_user = None
                try:
                    current_user = await self._get_current_user_and_check_guard(
                        sid, event_name
                    )
                except Exception as error:
                    # If guards exist, authentication is required - fail
                    if guards is not None:
                        logger.error(f"🧦 Failed authenticating {sid}.")
                        # await self._emit_status(sid, {"error": str(error)})
                        raise error
                    # If guards=None, continue without authentication
                    logger.info(f"Public access (no authentication) for {event_name}")

                try:
                    database_object = None
                    if event_name == "submit:update":
                        # TBD: add handling of parent_id if present in data
                        resource_id = UUID(payload["id"])
                        # if id is present, it is an update
                        # validate data with update model
                        assert self.update_model is not None
                        object_update = self.update_model(**payload)
                        async with self.crud() as crud:
                            # TBD: check the hierarchical resource system all the way through other events as
                            database_object = await crud.update(
                                current_user, resource_id, object_update
                            )
                            # if updating user is not in the resource room yet, add that user:
                            if (
                                database_object.id
                                not in self.server.rooms(  # type: ignore[attr-defined]
                                    sid, self.namespace or "/"
                                )
                            ):
                                await self.server.enter_room(
                                    sid,
                                    f"resource:{str(database_object.id)}",  # type: ignore[attr-defined]
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
                        assert self.create_model is not None
                        object_create = self.create_model(**payload)
                        parent_id = data.get("parent_id", None)
                        # TBD: add tests for inherit, public and public_action flags
                        # in protected resource hierarchy
                        # (There are tests for public in QuizNamespace already.)
                        inherit = data.get("inherit", False)
                        public = data.get("public", False)
                        public_action = data.get("public_action", Action.read)
                        async with self.crud() as crud:
                            # TBD: check the hierarchical resource system all the way through other events as well!
                            database_object = await crud.create(
                                object_create,
                                current_user,
                                parent_id,
                                inherit,
                                public,
                                public_action,
                            )
                            parent_type = None
                            if parent_id is not None:
                                parent_types = await crud._get_types_from_ids(
                                    [parent_id]
                                )
                                parent_type = (
                                    parent_types[0].type if parent_types else None
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
                            # so they get notified through a "shared" event.
                            rooms = []
                            if parent_id is not None:
                                # This one is for emiting in child-namespace, room "parend_id",
                                # so all clients that are in that room get the update about the new child resource
                                # and can decide what to do with it based on the parent_id information.
                                # Is it atcually necessary to emit this in the child-namespace?
                                # Probably yes, becasue some children might not be connected to the parent_namespace,
                                # but still want to list all their parents.
                                rooms += [f"parent:{parent_id}"]
                                # emit same status as in "on_link" - duplicate here
                                # TBD: consider refactoring into a separate method,
                                # to avoid that dublication.
                                status = {
                                    "success": "linked",
                                    "id": str(database_object.id),
                                    "parent_id": str(parent_id),
                                    "inherit": inherit,
                                }
                                # Currently one of those emits is tested in
                                # test_connect_create_read_update_delete_sub_group
                                # TBD: add another test for the other emit
                                await self._emit_status(
                                    sid, status, [f"resource:{str(database_object.id)}"]
                                )
                                parent_namespace = registry_namespaces.get(parent_type)
                                await self._emit_status(
                                    sid,
                                    status,
                                    [f"resource:{str(parent_id)}"],
                                    namespace=parent_namespace,
                                )
                            await self._emit_status(
                                sid,
                                {
                                    "success": "shared",
                                    "id": str(database_object.id),
                                },
                                rooms=rooms,
                            )
                            # This previous implementation prevented the status to be sent to the clinet, which called [sid].
                            # await self.server.emit(
                            #     "status",
                            #     {
                            #         "success": "shared",
                            #         "id": str(database_object.id),
                            #     },
                            #     namespace=self.namespace,
                            #     to=rooms,
                            # )
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
                await self.server.emit(
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
        if self.crud is None:
            await self._emit_status(sid, {"error": "No CRUD configured."})
            return
        try:
            current_user = await self._get_current_user_and_check_guard(sid, "delete")
            async with self.crud() as crud:
                await crud.delete(current_user, entity_id)
                if crud.model.__name__ in ResourceType.list():
                    await self.server.close_room(
                        f"resource:{str(entity_id)}", namespace=self.namespace
                    )
                elif crud.model.__name__ in IdentityType.list():
                    await self.server.close_room(
                        f"identity:{str(entity_id)}", namespace=self.namespace
                    )
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

    async def on_share(self, sid, access_policy: Dict[str, Any]):
        """Share event for socket.io namespaces."""
        logger.info(f"🧦 Share request from client {sid}.")
        # TBD: validate the AccessPolicyCreate model!
        try:
            current_user = await self._get_current_user_and_check_guard(sid, "share")
            # print("===  socketio - SHARE - access_policy ===")
            # print(access_policy, flush=True)
            if "action" not in access_policy:
                access_policy_delete = AccessPolicyDelete(**access_policy)
                async with AccessPolicyCRUD() as crud:
                    await crud.delete(current_user, access_policy_delete)
                    # print("=== socketio - DELETE - access_policy ===", flush=True)
                    await self._emit_status(
                        sid,
                        {
                            "success": "unshared",
                            "id": str(access_policy_delete.resource_id),
                        },
                        rooms=[f"identity:{str(access_policy_delete.identity_id)}"],
                    )
                # print("=== socketio - DELETE - access_policy ===", flush=True)
            elif (
                "new_action" not in access_policy
                or access_policy["action"] != access_policy["new_action"]
            ):
                # elif "new_action" not in access_policy:
                # print(
                #     "=== routers - socketio - v1 - on_share - CREATE - access_policy ==="
                # )
                # pprint(access_policy)
                resource_id_value: Any = access_policy.get("resource_id")
                identity_id_value: Any = access_policy.get("identity_id")
                if "new_action" not in access_policy:
                    access_policy_create = AccessPolicyCreate(**access_policy)
                    async with AccessPolicyCRUD() as crud:
                        await crud.create(access_policy_create, current_user)
                    resource_id_value = access_policy_create.resource_id
                    identity_id_value = access_policy_create.identity_id
                    # print("=== socketio - CREATE - access_policy ===", flush=True)
                elif access_policy["action"] != access_policy["new_action"]:
                    access_policy_update = AccessPolicyUpdate(**access_policy)
                    async with AccessPolicyCRUD() as crud:
                        await crud.update(current_user, access_policy_update)
                    resource_id_value = access_policy_update.resource_id
                    identity_id_value = access_policy_update.identity_id
                    # print("=== socketio - UPDATE - access_policy ===", flush=True)
                await self._emit_status(
                    sid,
                    {
                        "success": "shared",
                        "id": str(resource_id_value),
                    },
                    rooms=[f"identity:{str(identity_id_value)}"],
                )
                # print("=== socketio - CREATE - access_policy ===", flush=True)
            # elif access_policy["action"] != access_policy["new_action"]:
            #     access_policy = AccessPolicyUpdate(**access_policy)
            #     async with AccessPolicyCRUD() as crud:
            #         await crud.update(current_user, access_policy)
            #     # print("=== socketio - UPDATE - access_policy ===", flush=True)
            #     await self._emit_status(
            #         sid,
            #         {
            #             "success": "shared",
            #             "id": str(access_policy.resource_id),
            #         },
            #         rooms=[f"identity:{str(access_policy.identity_id)}"],
            #     )
            #     print("=== socketio - UPDATE - access_policy ===", flush=True)
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

    async def on_link(self, sid, hierarchy: Dict[str, Any]):
        """Link event for socket.io namespaces."""
        logger.info(f"🧦 Link request from client {sid}.")
        if self.crud is None:
            await self._emit_status(sid, {"error": "No CRUD configured."})
            return
        try:
            hierarchy_obj = BaseHierarchyCreate(**hierarchy)
            current_user = await self._get_current_user_and_check_guard(
                sid, "submit:create"
            )
            async with self.crud() as crud:
                await crud.add_child_to_parent(
                    hierarchy_obj.child_id,
                    hierarchy_obj.parent_id,
                    current_user,
                    hierarchy_obj.inherit,
                )
                parent_types = await crud._get_types_from_ids([hierarchy_obj.parent_id])
                parent_type = parent_types[0].type if parent_types else None
            status = {
                "success": "linked",
                "id": str(hierarchy_obj.child_id),
                "parent_id": str(hierarchy_obj.parent_id),
                "inherit": hierarchy_obj.inherit,
            }
            await self._emit_status(
                sid, status, [f"resource:{str(hierarchy_obj.child_id)}"]
            )
            parent_namespace = registry_namespaces.get(parent_type)
            await self._emit_status(
                sid,
                status,
                [f"resource:{str(hierarchy_obj.parent_id)}"],
                namespace=parent_namespace,
            )
        except Exception as error:
            logger.error(f"🧦 Failed to link item for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    # TBD: write tests for this:
    async def on_unlink(self, sid, hierarchy: Dict[str, Any]):
        """Unlink event for socket.io namespaces."""
        logger.info(f"🧦 Unlink request from client {sid}.")
        if self.crud is None:
            await self._emit_status(sid, {"error": "No CRUD configured."})
            return
        try:
            hierarchy_obj = BaseHierarchyCreate(**hierarchy)
            current_user = await self._get_current_user_and_check_guard(
                sid, "submit:update"
            )
            async with self.crud() as crud:
                await crud.remove_child_from_parent(
                    hierarchy_obj.child_id, hierarchy_obj.parent_id, current_user
                )
                parent_types = await crud._get_types_from_ids([hierarchy_obj.parent_id])
                parent_type = parent_types[0].type if parent_types else None
            status = (
                {
                    "success": "unlinked",
                    "id": str(hierarchy_obj.child_id),
                    "parent_id": str(hierarchy_obj.parent_id),
                },
            )
            await self._emit_status(
                sid,
                status,
                [
                    f"resource:{str(hierarchy_obj.child_id)}",
                ],
            )
            parent_namespace = registry_namespaces.get(parent_type)
            # TBD: emit in both namespaces with only one emit,
            # that is change _emit_status to always include own namespace or
            # specify own namespace explicitly in argument namespaces?
            await self._emit_status(
                sid,
                status,
                [f"resource:{str(hierarchy_obj.parent_id)}"],
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
