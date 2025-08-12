import logging
from core.types import EventGuard, GuardTypes
from crud.identity import (
    UserCRUD,
    GroupCRUD,
    SubGroupCRUD,
    SubSubGroupCRUD,
    UeberGroupCRUD,
)
from models.identity import (
    Me,
    UserCreate,
    UserRead,
    UserExtended,
    UserUpdate,
    UeberGroupCreate,
    UeberGroupExtended,
    UeberGroupRead,
    UeberGroupUpdate,
    GroupCreate,
    GroupRead,
    GroupExtended,
    GroupUpdate,
    SubGroupCreate,
    SubGroupRead,
    SubGroupExtended,
    SubGroupUpdate,
    SubSubGroupCreate,
    SubSubGroupRead,
    SubSubGroupExtended,
    SubSubGroupUpdate,
)

from .base import BaseNamespace

logger = logging.getLogger(__name__)

user_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["Admin"]),
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["Admin"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class UserNamespace(BaseNamespace):
    """Socket.IO interface for Users."""

    def __init__(self):
        super().__init__(
            namespace="/user",
            event_guards=user_guards,
            crud=UserCRUD,
            create_model=UserCreate,
            read_model=UserRead,
            read_extended_model=UserExtended,
            update_model=UserUpdate,
            # callback_on_connect=self.callback_on_connect,
        )

    # # TBD: consider adding returning Me on connect to UserNamespace
    # async def callback_on_connect(self, sid, current_user=None, *args, **kwargs):
    #     """Callback on connect for returns Me."""
    #     logger.info(f"🧦 Get all data request from client {sid}.")
    #     try:
    #         me = None
    #         # The CRUD in callback_on_connect does not work with admin tokens
    #         async with self.crud() as crud:
    #             me = await crud.read_me(current_user)
    #         await self.server.emit(
    #             "transfered",
    #             me.model_dump(mode="json"),
    #             namespace=self.namespace,
    #             to=sid,
    #         )
    #     except Exception as error:
    #         logger.error(f"Failed to current user data for client {sid}.")
    #         print(error)
    #         await self._emit_status(sid, {"error": str(error)})

    async def on_read_me(self, sid):
        """Callback on connect for returns Me."""
        logger.info(f"🧦 Get all data request from client {sid}.")
        try:
            current_user = await self._get_current_user_and_check_guard(sid, "connect")
            me = None
            # The CRUD in callback_on_connect does not work with admin tokens
            async with self.crud() as crud:
                me = await crud.read_me(current_user)
            await self.server.emit(
                "transfered",
                me.model_dump(mode="json"),
                namespace=self.namespace,
                to=sid,
            )
        except Exception as error:
            logger.error(f"Failed to current user data for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})

    async def on_update_me(self, sid, data):
        """Update Me event for socket.io namespaces."""
        logger.info(f"🧦 Update request from client {sid} for Me.")
        try:
            current_user = await self._get_current_user_and_check_guard(
                sid, "submit:update"
            )
            new_me = Me(**data)
            updated_me = None
            async with self.crud() as crud:
                updated_me = await crud.update_me(current_user, new_me)
            await self.server.emit(
                "transfered",
                updated_me.model_dump(mode="json"),
                namespace=self.namespace,
                to=sid,
            )
        except Exception as error:
            logger.error(f"Failed to update Me for client {sid}.")
            print(error)
            await self._emit_status(sid, {"error": str(error)})


user_router = UserNamespace()

ueber_group_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["Admin"]),
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["Admin"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class UeberGroupNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Groups."""

    def __init__(self):
        super().__init__(
            namespace="/ueber-group",
            event_guards=ueber_group_guards,
            crud=UeberGroupCRUD,
            create_model=UeberGroupCreate,
            read_model=UeberGroupRead,
            read_extended_model=UeberGroupExtended,
            update_model=UeberGroupUpdate,
            callback_on_connect=self.callback_on_connect,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all ueber groups:
        await self._get_all(sid, *args, **kwargs)


ueber_group_router = UeberGroupNamespace()


group_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class GroupNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Groups."""

    def __init__(self):
        super().__init__(
            namespace="/group",
            event_guards=group_guards,
            crud=GroupCRUD,
            create_model=GroupCreate,
            read_model=GroupRead,
            read_extended_model=GroupExtended,
            update_model=GroupUpdate,
            callback_on_connect=self.callback_on_connect,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all groups:
        await self._get_all(sid, *args, **kwargs)


group_router = GroupNamespace()

sub_group_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class SubGroupNamespace(BaseNamespace):
    """Socket.IO interface for Sub Groups."""

    def __init__(self):
        super().__init__(
            namespace="/sub-group",
            event_guards=sub_group_guards,
            crud=SubGroupCRUD,
            create_model=SubGroupCreate,
            read_model=SubGroupRead,
            read_extended_model=SubGroupExtended,
            update_model=SubGroupUpdate,
            callback_on_connect=self.callback_on_connect,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all sub groups:
        await self._get_all(sid, *args, **kwargs)


sub_group_router = SubGroupNamespace()

sub_sub_group_guards = [
    EventGuard(
        event="connect",
        guards=GuardTypes(scopes=["socketio", "api.read"], roles=["User"]),
    ),
    EventGuard(
        event="submit:create",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="submit:update",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="delete",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
    EventGuard(
        event="share",
        guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
    ),
]


class SubSubGroupNamespace(BaseNamespace):
    """Socket.IO interface for Sub Sub Groups."""

    def __init__(self):
        super().__init__(
            namespace="/sub-sub-group",
            event_guards=sub_sub_group_guards,
            crud=SubSubGroupCRUD,
            create_model=SubSubGroupCreate,
            read_model=SubSubGroupRead,
            read_extended_model=SubSubGroupExtended,
            update_model=SubSubGroupUpdate,
            callback_on_connect=self.callback_on_connect,
        )

    async def callback_on_connect(self, sid, *args, **kwargs):
        """Callback on connect for socket.io namespaces."""
        # trigger the read all event to fetch all sub sub groups:
        await self._get_all(sid, *args, **kwargs)


sub_sub_group_router = SubSubGroupNamespace()
