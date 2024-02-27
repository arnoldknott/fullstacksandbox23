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
        return token.provides_current_user()

    async def post(
        self,
        token_payload,
        object,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        current_user = await self.__guards(token_payload, scopes, roles, groups)
        logger.info("POST calls post")
        async with self.crud(current_user) as crud:
            created_object = await crud.create(object)
        return created_object

    async def get(
        self,
        token_payload,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        current_user = self.__guards(token_payload, scopes, roles, groups)
        logger.info("GETs all objects")
        async with self.crud(current_user) as crud:
            objects = await crud.read()
        return objects

    async def get_by_id(
        self,
        token_payload,
        id,
        scopes: List[str] = [],
        roles: List[str] = [],
        groups: List[UUID] = [],
    ):
        current_user = self.__guards(token_payload, scopes, roles, groups)
        logger.info("GET calls get")
        async with self.crud(current_user) as crud:
            object = await crud.read_by_id(id)
        return object


# class BasePOST(BaseView):
#     """Base class for POST views"""

#     def __init__(self, crud):
#         # makes the attributes of the BaseView class available:
#         super().__init__(crud)

#     async def create(self, object):
#         logger.info("POST calls create")
#         async with self.crud() as crud:
#             created_object = await crud.create(object, self.__update_last_access)
#         return created_object
