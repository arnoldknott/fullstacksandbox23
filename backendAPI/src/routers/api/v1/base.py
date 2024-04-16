import logging
from core.security import CurrentAccessToken
from core.types import GuardTypes
from core.types import GuardTypes
from typing import List
from uuid import UUID
from fastapi import HTTPException

logger = logging.getLogger(__name__)


# TBD: implement rate limiting
# TBD: implement pagination
# TBD: implement sorting
# TBD: implement filtering
# TBD: implement searching
# TBD: implement CORS
# TBD: implement caching


# class Protectors(BaseModel):
#     """Protectors for the routes"""

#     scopes: Optional[List[str]] = []
#     roles: Optional[List[str]] = []
#     groups: Optional[List[UUID]] = []


class BaseView:
    """Base class for all views"""

    def __init__(self, crud, model):
        self.crud = crud
        self.model = model

    # TBD: In a similar manner
    # - implement rate limiting
    # - implement pagination
    # - implement sorting
    async def _check_token_against_guards(self, token_payload, guards):
        """checks if token fulfills the required guards and returns current user."""
        token = CurrentAccessToken(token_payload)
        # TBD: consider moving this logic to the guards class
        # and only call the verifying method with the token_payload!
        if guards is not None:
            if guards.scopes is not None:
                for scope in guards.scopes:
                    await token.has_scope(scope)
            if guards.roles is not None:
                for role in guards.roles:
                    # TBD: define role overrides here: "Admin" overrides "User"? or should that be taken care of in security?
                    # This would be relevant if a route is protected with both "Admin" and "User" roles.
                    # But still, there could be a sense in having a "User" role, There might be Admins, which are not Users.
                    # But then again - what's the point having an Amin if it can't do everything?
                    await token.has_role(role)
            if guards.groups is not None:
                for group in guards.groups:
                    await token.has_group(group)
        return await token.provides_current_user()
        # current_user = await self._guards(
        #     token_payload, guards.scopes, guards.roles, guards.groups
        # )
        # return current_user

    async def post(
        self,
        object,
        token_payload,
        guards: GuardTypes,
    ):
        logger.info("POST view calls create CRUD")
        current_user = await self._check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            created_object = await crud.create(object, current_user)
        return created_object

    async def post_with_public_access(
        self,
        object,
        token_payload,
        guards: GuardTypes,
    ):
        logger.info("POST view for public access calls create_public CRUD")
        current_user = await self._check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            created_object = await crud.create_public(object, current_user)
        return created_object

    async def get(
        self,
        # get operation does not need a token_payload, if the resource is public
        token_payload=None,
        guards: GuardTypes = None,
    ):
        logger.info("GET view to retrieve all objects from read CRUD")
        current_user = None
        if token_payload:
            current_user = await self._check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            objects = await crud.read(current_user)

        return objects

    async def get_by_id(
        self,
        id,
        token_payload=None,
        guards: GuardTypes = None,
    ):
        logger.info("GET by id view to retrieve specific object from read CRUD")
        try:
            id = UUID(id)
        except ValueError:
            logger.error("ID is not a universal unique identifier (uuid).")
            raise HTTPException(status_code=400, detail="Invalid id.")
        current_user = None
        if token_payload:
            current_user = await self._check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            object = await crud.read_by_id(id, current_user)
        return object

    # TBD: consider moving this to CRUD and don't parts of SQL queries in the views
    # async def get_with_query_options(
    #     self,
    #     select_args: List[str] = None,
    #     filters: List[str] = None,
    #     joins: List[str] = None,
    #     order_by: List[str] = None,
    #     # group_by: List[str] = None,
    #     # having: List[str] = None,
    #     # limit: int = None,
    #     # offset: int = None
    #     token_payload=None,
    #     guards: GuardTypes = None,
    # ):
    #     logger.info("GET with various query options from read CRUD")
    #     # This is more generic than the get_by_id and filter data needs to happen in inheriting classes
    #     current_user = None
    #     if token_payload:
    #         current_user = await self._check_token_against_guards(token_payload, guards)
    #     async with self.crud() as crud:
    #         object = await crud.read(
    #             current_user,
    #             select_args=select_args,
    #             filters=filters,
    #             joins=joins,
    #             order_by=order_by,
    #         )
    #     return object

    async def put(
        self,
        id,
        object,
        token_payload,
        guards: GuardTypes,
    ):
        logger.info("PUT updates a specific object through update CRUD")
        try:
            id = UUID(id)
        except ValueError:
            logger.error("ID is not a universal unique identifier (uuid).")
            raise HTTPException(status_code=400, detail="Invalid id.")
        current_user = await self._check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            updated_object = await crud.update(current_user, id, object)
        return updated_object

    async def delete(
        self,
        id,
        token_payload,
        guards: GuardTypes,
    ):
        logger.info("DELETE removes a specific object through delete CRUD")
        try:
            id = UUID(id)
        except ValueError:
            logger.error("ID is not a universal unique identifier (uuid).")
            raise HTTPException(status_code=400, detail="Invalid id.")
        current_user = await self._check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            deleted_object = await crud.delete(current_user, id)
        return deleted_object
