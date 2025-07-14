from core.types import GuardTypes
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


class UeberGroupNamespace(BaseNamespace):
    """Socket.IO interface for Ueber Groups."""

    def __init__(self, namespace=None):
        super().__init__(
            namespace=namespace,
            guards=GuardTypes(scopes=["socketio", "api.write"], roles=["User"]),
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


ueber_group_router = UeberGroupNamespace("/ueber-group")
