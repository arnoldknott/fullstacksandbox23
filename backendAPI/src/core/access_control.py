import logging

from typing import TYPE_CHECKING
from uuid import UUID
from fastapi import HTTPException


if TYPE_CHECKING:
    from core.types import CurrentUserData, Action


logger = logging.getLogger(__name__)


class AccessControl:
    def __init__(self) -> None:
        pass

    async def __write_policy(self):
        """Writes a permission to the database"""
        # TBD: only owners and admins of an object can write a policy
        # with get_async_session() as session:
        #     pass

    async def __read_policy(self):
        """Gets the permission from the database"""
        # TBD: everyone can read a policy
        # with get_async_session() as session:
        #     pass
        return True

    async def __delete_policy(self):
        """Deletes a permission in the database"""
        # TBD: only owners and admins of an object can delete a policy
        # with get_async_session() as session:
        #     pass

    async def allows(
        self, user: "CurrentUserData", resource_id: UUID, action: "Action"
    ) -> bool:
        """Checks if the user has permission to perform the action on the resource"""
        # TBD: get the hierarchy and overrides for resource and user
        # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
        policy = await self.__read_policy()
        print("=== access control called ===")
        if policy:
            return True
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    async def adds_grant(
        identity: "CurrentUserData", resource_id: UUID, action: "Action"
    ) -> bool:
        """Grants a new permission to for a resource"""
        pass

    async def removes_grant(
        identity: "CurrentUserData", resource_id: UUID, action: "Action"
    ) -> bool:
        """Removes a permission for a resource"""
        pass
