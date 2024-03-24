import logging
from core.security import CurrentAccessToken
from typing import List
from uuid import UUID

logger = logging.getLogger(__name__)


# TBD: implement rate limiting
# TBD: implement pagination
# TBD: implement sorting
# TBD: implement filtering
# TBD: implement searching
# TBD: implement CORS
# TBD: implement caching


class BaseView:
    """Base class for all views"""

    def __init__(self, crud):
        self.crud = crud

    # note: in python private methods are not really private: name mangling!
    async def __guards(self, token_payload, scopes, roles, groups):
        """Executes the guards to check if token has required scopes, roles and groups."""
        token = CurrentAccessToken(token_payload)
        for scope in scopes:
            await token.has_scope(scope)
        for role in roles:
            # TBD: define role overrides here: "Admin" overrides "User"? or should that be taken care of in security?
            # This would be relevant if a route is protected with both "Admin" and "User" roles.
            # But still, there could be a sense in having a "User" role, There might be Admins, which are not Users.
            # But then again - what's the point having an Amin if it can't do everything?
            await token.has_role(role)
        for group in groups:
            await token.has_group(group)
        return await token.provides_current_user()

    async def post(
        self,
        token_payload,
        object,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        logger.info("POST view calls create CRUD")
        current_user = await self.__guards(token_payload, scopes, roles, groups)
        async with self.crud() as crud:
            # created_object = await crud.create(object)
            # Refactor into this:
            created_object = await crud.create(object, current_user)
        return created_object

    async def get(
        self,
        # get operation does not need a token_payload, if the resource is public
        token_payload=None,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        logger.info("GET view to retrieve all objects from read CRUD")
        current_user = None
        if token_payload:
            current_user = self.__guards(token_payload, scopes, roles, groups)
        async with self.crud() as crud:
            objects = await crud.read(current_user)

        return objects

    async def get_by_id(
        self,
        id,
        token_payload=None,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        logger.info("GET by id view to retrieve specific object from read CRUD")
        current_user = None
        if token_payload:
            current_user = self.__guards(token_payload, scopes, roles, groups)
        async with self.crud() as crud:
            object = await crud.read_by_id(id, current_user)
        return object

    async def put(
        self,
        id,
        token_payload,
        object,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        logger.info("PUT updates a specific object through update CRUD")
        current_user = await self.__guards(token_payload, scopes, roles, groups)
        async with self.crud() as crud:
            updated_object = await crud.update(id, object, current_user)
        return updated_object

    async def delete(
        self,
        id,
        token_payload,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        logger.info("DELETE removes a specific object through delete CRUD")
        current_user = await self.__guards(token_payload, scopes, roles, groups)
        async with self.crud() as crud:
            deleted_object = await crud.delete(id, current_user)
        return deleted_object
