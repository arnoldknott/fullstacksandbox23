import logging
from typing import List

from uuid import UUID
from core.security import get_access_token_payload, Guards
from core.types import GuardTypes
from crud.identity import UserCRUD
from fastapi import APIRouter, Depends, HTTPException
from models.identity import User, UserCreate, UserRead, UserUpdate
from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

# user_view = BaseView(UserCRUD, User)


class UserView(BaseView):
    def __init__(self):
        super().__init__(UserCRUD, User)

    async def get_by_azure_user_id(
        self,
        azure_user_id: UUID,
        token_payload=None,
        guards: GuardTypes = Depends(Guards(scopes=["api.read"], roles=["User"])),
        # scopes: List[str] = [],
        # roles: List[str] = [],
        # groups: List[UUID] = [],
    ) -> UserRead:
        """GET view to retrieve user by azure_user_id."""
        logger.info("GET user by azure_user_id")
        current_user = await self._check_token_against_guards(token_payload, guards)
        # current_user = await self._guards(token_payload, scopes, roles, groups)
        async with self.crud() as crud:
            user = await crud.read_by_azure_user_id(azure_user_id, current_user)
        return user


user_view = UserView()

# this filter definition needs to move to the specific CRUD:
# filters = [User.azure_user_id == azure_user_id]
# return await self.(filters=filters, token_payload=token_payload, roles=roles)


# note: self-sign-up through security - controlled by token content,
# that means, controlled by group and user membership from Azure Identity Provider!
# The roles assigned to users and groups decide about sign-up here.
# This function allows admins to sign up users through API on top of that.
# TBD: make sure this route or anything else, that is checking if the user exists get's hit by the frontend when the user logs in!
# That is solved now with the base view class!
# @router.post("/", status_code=201)
# async def post_user(
#     user: UserCreate,
#     _1=Depends(CurrentAccessTokenHasScope("api.write")),
#     _2=Depends(CurrentAccessTokenHasRole("Admin")),
# ) -> User:
#     """Creates a new user."""
#     logger.info("POST user")
#     async with UserCRUD() as crud:
#         created_user = await crud.create(user)
#     return created_user


# TBD: Refactor with AccessControl:
@router.post("/", status_code=201)
async def post_user(
    user: UserCreate,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> User:
    """Creates a new user."""
    logger.info("POST user")
    return await user_view.post(
        user,
        token_payload,
        guards,
        # scopes=["api.write"],
        # roles=["Admin"],
    )


# First experiment to work with BasePOST class inherited from BaseView
# # TBD: using the BasePOST view class should replace the above implementation!
# @router.post("/", status_code=201)
# async def post_user(
#     user: UserCreate,
#     _1=Depends(CurrentAccessTokenHasScope("api.write")),
#     _2=Depends(CurrentAccessTokenHasRole("Admin")),
# ) -> User:
#     """Creates a new user."""
#     # uses the default for updated_last_access:
#     return BasePOST(UserCRUD).create(user)


# # this is an example on how to utilize the methods from the BaseView class through BasePOST instance
# # note: that's not relevant for the POST method above, but for GET and PUT below
# @router.post("/admin_prevents_updated_last_access", status_code=201)
# async def post_user(
#     user: UserCreate,
#     _1=Depends(CurrentAccessTokenHasScope("api.write")),
#     check_admin_role=Depends(CurrentAccessTokenHasRole("Admin")),
# ) -> User:
#     """Creates a new user."""
#     pass an instance of guards and the CRUD to the BasePOST instance:
#     post_view = BasePOST(guards, UserCRUD)
#     # executes the logic for determining the updated_last_access:
#     # post_view.updates_last_access(check_admin_role, current_user, user.user_id)
#     return post_view.create(user)


# # TBD: delete old version after refactoring with BaseView:
# @router.get("/")
# async def get_all_users(
#     _=Depends(CurrentAccessTokenHasRole("Admin")),
# ) -> List[User]:
#     """Returns all user."""
#     logger.info("GET all user")
#     async with UserCRUD() as crud:
#         response = await crud.read_all()
#     return response


@router.get("/", status_code=200)
async def get_all_users(
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["Admin"])),
) -> list[UserRead]:
    """Returns all users."""
    return await user_view.get(
        token_payload,
        guards,
        # roles=["Admin"],
    )


# # TBD: Delete old version after refactoring with BaseView:
# @router.get("/azure/{azure_user_id}")
# async def get_user_by_azure_user_id(
#     azure_user_id: str,
#     current_user: UserRead = Depends(CurrentAzureUserInDatabase()),
#     check_admin_role=Depends(CurrentAccessTokenHasRole("Admin", require=False)),
# ) -> UserRead:
#     """Returns a user based on its azure user id."""
#     if (str(current_user.azure_user_id) != str(azure_user_id)) and (
#         check_admin_role is False
#     ):
#         raise HTTPException(status_code=403, detail="Access denied")

#     logger.info("GET user")

#     # TBD: Refactor into access control
#     # update_last_access = True
#     # if (check_admin_role is True) and (
#     #     str(current_user.azure_user_id) != str(azure_user_id)
#     # ):
#     #     update_last_access = False

#     try:
#         azure_user_id = UUID(azure_user_id)
#     except ValueError:
#         logger.error("User ID is not an UUID")
#         raise HTTPException(status_code=400, detail="Invalid user id")
#     async with UserCRUD() as crud:
#         response = await crud.read_by_azure_user_id_with_childs(
#             azure_user_id
#             # TBD; Refactor into access control
#             # , update_last_access
#         )
#     return response


### TBD: Should be ready to go:
@router.get("/azure/{azure_user_id}", status_code=200)
async def get_user_by_azure_user_id(
    azure_user_id: str,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> UserRead:
    """Returns a user based on its azure user id."""
    try:
        azure_user_id = UUID(azure_user_id)
    except ValueError:
        logger.error("User ID is not an UUID")
        raise HTTPException(status_code=400, detail="Invalid user id")
    return await user_view.get_by_azure_user_id(
        azure_user_id, token_payload, guards  # , roles=["User"]
    )
    # filters = [User.azure_user_id == azure_user_id]
    # user = await user_view.get_with_query_options(
    #     filters=filters,
    #     token_payload=token_payload,
    #     roles=["User"],
    # )
    # return user[0]


# # TBD: Delete old version after refactoring with BaseView:
# @router.get("/{user_id}")
# async def get_user_by_id(
#     user_id: str,
#     current_user: UserRead = Depends(CurrentAzureUserInDatabase()),
#     check_admin_role=Depends(CurrentAccessTokenHasRole("Admin", require=False)),
# ) -> UserRead:
#     """Returns a user with a specific user_id."""
#     if (str(current_user.id) != str(user_id)) and (check_admin_role is False):
#         raise HTTPException(status_code=403, detail="Access denied")

#     logger.info("GET user")

#     # TBD: Refactor into access control
#     # update_last_access = True
#     # if (check_admin_role is True) and (str(current_user.id) != str(user_id)):
#     #     update_last_access = False

#     try:
#         user_id = UUID(user_id)
#     except ValueError:
#         logger.error("User ID is not an UUID")
#         raise HTTPException(status_code=400, detail="Invalid user id")
#     async with UserCRUD() as crud:
#         response = await crud.read_by_id_with_childs(user_id)  # , update_last_access)
#     return response


@router.get("/{user_id}", status_code=200)
async def get_user_by_id(
    user_id: str,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> UserRead:
    """Returns a user with a specific user_id."""
    # token = CurrentAccessToken(token_payload)
    # await token.self_or_admin(user_id)
    return await user_view.get_by_id(
        user_id,
        token_payload,
        guards,
        # roles=["User"],
    )


# # TBD: Delete old version after refactoring with BaseView:
# @router.put("/{user_id}")
# async def update_user(
#     user_id: str,
#     user_data_update: UserUpdate,
#     current_user: UserRead = Depends(CurrentAzureUserInDatabase()),
#     _=Depends(CurrentAccessTokenHasScope("api.write")),
#     check_admin_role=Depends(CurrentAccessTokenHasRole("Admin", require=False)),
# ) -> User:
#     """Updates a user."""
#     if (str(current_user.id) != str(user_id)) and (check_admin_role is False):
#         raise HTTPException(status_code=403, detail="Access denied")

#     logger.info("PUT user")

#     # TBD: Refactor into access control
#     # update_last_access = True
#     # if check_admin_role is True:
#     #     update_last_access = False

#     try:
#         user_id = UUID(user_id)
#     except ValueError:
#         logger.error("User ID is not an UUID")
#         raise HTTPException(status_code=400, detail="Invalid user id")
#     async with UserCRUD() as crud:
#         old_user = await crud.read_by_id(user_id)
#         updated_user = await crud.update(
#             old_user, user_data_update
#         )  # , update_last_access)
#     return updated_user


@router.put("/{user_id}", status_code=200)
async def put_user(
    user_id: str,
    user: UserUpdate,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> User:
    """Updates a user."""
    # token = CurrentAccessToken(token_payload)
    # await token.azure_self_or_admin(user_id)
    return await user_view.put(
        user_id,
        user,
        token_payload,
        guards,
        # roles=["Admin"],
        # scopes=["api.write"],
    )


# # TBD: Delete old version after refactoring with BaseView:
# @router.delete("/{user_id}")
# async def delete_user(
#     user_id: str,
#     current_user: UserRead = Depends(CurrentAzureUserInDatabase()),
#     _=Depends(CurrentAccessTokenHasScope("api.write")),
#     check_admin_role=Depends(CurrentAccessTokenHasRole("Admin", require=False)),
# ) -> User:
#     """Deletes a user."""
#     if (str(current_user.id) != str(user_id)) and (check_admin_role is False):
#         raise HTTPException(status_code=403, detail="Access denied")

#     logger.info("DELETE user")

#     try:
#         user_id = UUID(user_id)
#     except ValueError:
#         logger.error("User ID is not an UUID")
#         raise HTTPException(status_code=400, detail="Invalid user id")
#     async with UserCRUD() as crud:
#         result = await crud.delete(user_id)
#     return result


@router.delete("/{user_id}", status_code=200)
async def delete_user(
    user_id: str,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> User:
    """Deletes a user."""
    # token = CurrentAccessToken(token_payload)
    # await token.self_or_admin(user_id)
    return await user_view.delete(
        user_id, token_payload, guards  # roles=["User"], scopes=["api.write"]
    )
