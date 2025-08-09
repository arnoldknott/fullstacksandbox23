from core.types import EventGuard, GuardTypes
from crud.identity import (  # UserCRUD,; GroupCRUD,; SubGroupCRUD,; SubSubGroupCRUD,
    UeberGroupCRUD,
)
from models.identity import (  # UserCreate,; UserRead,; UserExtended,; UserUpdate,; GroupCreate,; GroupRead,; GroupExtended,; GroupUpdate,; SubGroupCreate,; SubGroupRead,; SubGroupExtended,; SubGroupUpdate,; SubSubGroupCreate,; SubSubGroupRead,; SubSubGroupExtended,; SubSubGroupUpdate,
    UeberGroupCreate,
    UeberGroupExtended,
    UeberGroupRead,
    UeberGroupUpdate,
)

from .base import BaseNamespace


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
