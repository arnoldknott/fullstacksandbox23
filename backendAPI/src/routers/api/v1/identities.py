import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from core.security import Guards, get_access_token_payload
from core.types import GuardTypes
from crud.identity import (
    UserCRUD,
    UeberGroupCRUD,
    GroupCRUD,
    SubGroupCRUD,
    SubSubGroupCRUD,
)
from models.identity import (
    User,
    UserCreate,
    UserRead,
    UserUpdate,
    UeberGroup,
    Group,
    SubGroup,
    SubSubGroup,
)

from .base import BaseView

logger = logging.getLogger(__name__)

user_router = APIRouter()
user_view = BaseView(UserCRUD, User)


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


@user_router.post("/", status_code=201)
async def post_user(
    user: UserCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> User:
    """Creates a new user."""
    logger.info("POST user")
    return await user_view.post(
        user,
        token_payload,
        guards,
    )


@user_router.get("/", status_code=200)
async def get_all_users(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[UserRead]:
    """Returns all users."""
    return await user_view.get(token_payload, guards)


@user_router.get("/azure/{azure_user_id}", status_code=200)
async def get_user_by_azure_user_id(
    azure_user_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> UserRead:
    """Returns a user based on its azure user id."""
    logger.info("GET user by azure_user_id")
    current_user = await user_view._check_token_against_guards(token_payload, guards)
    async with user_view.crud() as crud:
        user = await crud.read_by_azure_user_id(azure_user_id, current_user)
    return user


@user_router.get("/{user_id}", status_code=200)
async def get_user_by_id(
    user_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> UserRead:
    """Returns a user with a specific user_id."""
    return await user_view.get_by_id(
        user_id,
        token_payload,
        guards,
    )


@user_router.put("/{user_id}", status_code=200)
async def put_user(
    user_id: UUID,
    user: UserUpdate,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> User:
    """Updates a user."""
    return await user_view.put(
        user_id,
        user,
        token_payload,
        guards,
    )


@user_router.delete("/{user_id}", status_code=200)
async def delete_user(
    user_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:  # User:
    """Deletes a user."""
    return await user_view.delete(user_id, token_payload, guards)


ueber_group_router = APIRouter()
ueber_group_view = BaseView(UeberGroupCRUD, UeberGroup)

# TBD: implement endpoints for ueber_group
# TBD: implement one test to call all endpoints for ueber_group

groups_router = APIRouter()
groups_view = BaseView(GroupCRUD, Group)

# TBD: implement endpoints for group
# TBD: implement one test to call all endpoints for group

sub_group_router = APIRouter()
sub_group_router = BaseView(SubGroupCRUD, SubGroup)

# TBD: implement endpoints for sub_group
# TBD: implement one test to call all endpoints for sub_group

sub_sub_group_router = APIRouter()
sub_sub_group_router = BaseView(SubSubGroupCRUD, SubSubGroup)

# TBD: implement endpoints for sub_sub_group
# TBD: implement one test to call all endpoints for sub_sub_group
