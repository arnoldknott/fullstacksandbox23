import logging
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Query

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
    UeberGroupCreate,
    UeberGroupRead,
    UeberGroupUpdate,
    Group,
    GroupCreate,
    GroupRead,
    GroupUpdate,
    SubGroup,
    SubGroupCreate,
    SubGroupRead,
    SubGroupUpdate,
    SubSubGroup,
    SubSubGroupCreate,
    SubSubGroupRead,
    SubSubGroupUpdate,
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


# region User:


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


# TBD: add tests!
@user_router.post("/{user_id}/group/{group_id}", status_code=201)
async def post_add_user_to_group(
    user_id: UUID,
    group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> User:
    """Adds a user to a group."""
    logger.info("POST user to group")
    return await user_view.post_add_child_to_parent(
        group_id,
        user_id,
        token_payload,
        guards,
        inherit,
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


# endregion User

# TBD: add an endpoint to add a user to a ueber_group, group, sub_group, sub_sub_group

# region UeberGroup:

ueber_group_router = APIRouter()
ueber_group_view = BaseView(UeberGroupCRUD, UeberGroup)


@ueber_group_router.post("/", status_code=201)
async def post_ueber_group(
    ueber_group: UeberGroupCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> UeberGroup:
    """Creates a new ueber_group."""
    logger.info("POST ueber_group")
    return await ueber_group_view.post(
        ueber_group,
        token_payload,
        guards,
    )


@ueber_group_router.get("/", status_code=200)
async def get_all_ueber_groups(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[UeberGroupRead]:
    """Returns all ueber_groups."""
    return await ueber_group_view.get(token_payload, guards)


@ueber_group_router.get("/{ueber_group_id}", status_code=200)
async def get_ueber_group_by_id(
    ueber_group_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> UeberGroupRead:
    """Returns an ueber_group with a specific ueber_group_id."""
    return await ueber_group_view.get_by_id(
        ueber_group_id,
        token_payload,
        guards,
    )


@ueber_group_router.put("/{ueber_group_id}", status_code=200)
async def put_ueber_group(
    ueber_group_id: UUID,
    ueber_group: UeberGroupUpdate,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> UeberGroup:
    """Updates an ueber_group."""
    return await ueber_group_view.put(
        ueber_group_id,
        ueber_group,
        token_payload,
        guards,
    )


@ueber_group_router.delete("/{ueber_group_id}", status_code=200)
async def delete_ueber_group(
    ueber_group_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes an ueber_group."""
    return await ueber_group_view.delete(ueber_group_id, token_payload, guards)


# endregion UeberGroup

# region Group:


group_router = APIRouter()
group_view = BaseView(GroupCRUD, Group)


@group_router.post("/", status_code=201)
async def post_group(
    group: GroupCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> Group:
    """Creates a new group."""
    logger.info("POST group")
    return await group_view.post(
        group,
        token_payload,
        guards,
    )


@group_router.get("/", status_code=200)
async def get_all_groups(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[GroupRead]:
    """Returns all groups."""
    return await group_view.get(token_payload, guards)


@group_router.get("/{group_id}", status_code=200)
async def getgroup_by_id(
    group_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> UeberGroupRead:
    """Returns a group with a specific group_id."""
    return await group_view.get_by_id(
        group_id,
        token_payload,
        guards,
    )


@group_router.put("/{group_id}", status_code=200)
async def put_group(
    group_id: UUID,
    group: UeberGroupUpdate,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> Group:
    """Updates a group."""
    return await group_view.put(
        group_id,
        group,
        token_payload,
        guards,
    )


@group_router.delete("/{group_id}", status_code=200)
async def delete_group(
    group_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a group."""
    return await group_view.delete(group_id, token_payload, guards)


# endregion Group

# region SubGroup:

sub_group_router = APIRouter()
sub_group_view = BaseView(SubGroupCRUD, SubGroup)


@sub_group_router.post("/", status_code=201)
async def post_sub_group(
    sub_group: SubGroupCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> SubGroup:
    """Creates a new sub_group."""
    logger.info("POST sub_group")
    return await sub_group_view.post(
        sub_group,
        token_payload,
        guards,
    )


@sub_group_router.get("/", status_code=200)
async def get_all_sub_groups(
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[SubGroupRead]:
    """Returns all sub_groups."""
    return await sub_group_view.get(token_payload, guards)


@sub_group_router.get("/{sub_group_id}", status_code=200)
async def get_sub_group_by_id(
    sub_group_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> SubGroupRead:
    """Returns a sub_group with a specific sub_group_id."""
    return await sub_group_view.get_by_id(
        sub_group_id,
        token_payload,
        guards,
    )


@sub_group_router.put("/{sub_group_id}", status_code=200)
async def put_sub_group(
    sub_group_id: UUID,
    sub_group: SubGroupUpdate,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> SubGroup:
    """Updates a sub_group."""
    return await sub_group_view.put(
        sub_group_id,
        sub_group,
        token_payload,
        guards,
    )


@sub_group_router.delete("/{sub_group_id}", status_code=200)
async def delete_sub_group(
    sub_group_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a sub_group."""
    return await sub_group_view.delete(sub_group_id, token_payload, guards)


# TBD: implement endpoints for sub_group
# TBD: implement one test to call all endpoints for sub_group

# endregion SubGroup

# region SubSubGroup:

sub_sub_group_router = APIRouter()
sub_sub_group_view = BaseView(SubSubGroupCRUD, SubSubGroup)

# TBD: implement endpoints for sub_sub_group
# TBD: implement one test to call all endpoints for sub_sub_group

# endregion SubSubGroup
