from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from core.security import CurrentUserData, Action


class AccessControl:
    def __init__(self) -> None:
        pass

    async def permits(
        user: "CurrentUserData", resource_id: UUID, action: "Action"
    ) -> bool:
        """Checks if the user has permission to perform the action on the resource"""
        pass
