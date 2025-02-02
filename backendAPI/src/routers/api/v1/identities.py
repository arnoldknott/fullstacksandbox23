import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from core.security import (
    Guards,
    check_token_against_guards,
    get_http_access_token_payload,
)
from core.types import GuardTypes
from crud.access import BaseHierarchyModelRead
from crud.identity import (
    GroupCRUD,
    SubGroupCRUD,
    SubSubGroupCRUD,
    UeberGroupCRUD,
    UserCRUD,
)
from models.identity import (
    Group,
    GroupCreate,
    GroupRead,
    Me,
    SubGroup,
    SubGroupCreate,
    SubGroupRead,
    SubGroupUpdate,
    SubSubGroupCreate,
    UeberGroup,
    UeberGroupCreate,
    UeberGroupRead,
    UeberGroupUpdate,
    User,
    UserCreate,
    UserRead,
    UserUpdate,
)

from .base import BaseView

logger = logging.getLogger(__name__)

user_router = APIRouter()
user_view = BaseView(UserCRUD)


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
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> User:
    """Creates a new user."""
    logger.info("POST user")
    return await user_view.post(
        user,
        token_payload,
        guards,
    )


@user_router.post("/{user_id}/group/{group_id}", status_code=201)
async def post_existing_user_to_group(
    user_id: UUID,
    group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> BaseHierarchyModelRead:
    """Adds a user to an ueber-group, group, sub-group or sub-sub-group."""
    logger.info("POST user to group")
    return await user_view.post_add_child_to_parent(
        user_id,
        group_id,
        token_payload,
        guards,
        inherit,
    )


@user_router.get("/me", status_code=200)
async def get_me(
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> Me:
    """Returns the current user with account and profile."""
    current_user = await check_token_against_guards(token_payload, guards)
    # userInDatabase = await user_view.get_by_id(
    #     current_user.user_id, token_payload, guards
    # )
    async with UserCRUD() as crud:
        me = await crud.read_me(current_user)
    me.azure_token_roles = current_user.azure_token_roles
    me.azure_token_groups = current_user.azure_token_groups
    me = Me.model_validate(me)
    return me


@user_router.get("/", status_code=200)
async def get_all_users(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[UserRead]:
    """Returns all users."""
    return await user_view.get(token_payload, guards)


@user_router.get("/azure/{azure_user_id}", status_code=200)
async def get_user_by_azure_user_id(
    azure_user_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> UserRead:
    """Returns a user based on its azure user id."""
    logger.info("GET user by azure_user_id")
    current_user = await check_token_against_guards(token_payload, guards)
    async with user_view.crud() as crud:
        user = await crud.read_by_azure_user_id(azure_user_id, current_user)
    return user


@user_router.get("/{user_id}", status_code=200)
async def get_user_by_id(
    user_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> UserRead:
    """Returns a user with a specific user_id."""
    return await user_view.get_by_id(
        user_id,
        token_payload,
        guards,
    )


@user_router.put("/me", status_code=200)
async def put_me(
    user: Me,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> Me:
    """Updates the current user with account and profile."""
    current_user = await check_token_against_guards(token_payload, guards)
    if current_user.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    async with UserCRUD() as crud:
        me = await crud.update_me(current_user, user)
    me.azure_token_roles = current_user.azure_token_roles
    me.azure_token_groups = current_user.azure_token_groups
    me = Me.model_validate(me)
    return me


@user_router.put("/{user_id}", status_code=200)
async def put_user(
    user_id: UUID,
    user: UserUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
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
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:  # User:
    """Deletes a user."""
    return await user_view.delete(user_id, token_payload, guards)


@user_router.delete("/{user_id}/group/{group_id}", status_code=200)
async def delete_user_from_group(
    user_id: UUID,
    group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes a user from an ueber-group, group, sub-group or sub-sub-group."""
    logger.info("DELETE user from group")
    return await user_view.remove_child_from_parent(
        user_id,
        group_id,
        token_payload,
        guards,
    )


# endregion User

# region UeberGroup:

ueber_group_router = APIRouter()
ueber_group_view = BaseView(UeberGroupCRUD)


@ueber_group_router.post("/", status_code=201)
async def post_ueber_group(
    ueber_group: UeberGroupCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> UeberGroup:
    """Creates a new ueber_group."""
    logger.info("POST ueber_group")
    return await ueber_group_view.post(
        ueber_group,
        token_payload,
        guards,
    )


@ueber_group_router.post("/{ueber_group_id}/users", status_code=201)
async def post_existing_users_to_uebergroup(
    ueber_group_id: UUID,
    user_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of users to an ueber_group."""
    logger.info("POST users to ueber_group")
    hierarchy_response = []
    for user_id in user_ids:
        response = await user_view.post_add_child_to_parent(
            user_id,
            ueber_group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@ueber_group_router.post("/{ueber_group_id}/group", status_code=201)
async def post_group_to_uebergroup(
    group: GroupCreate,
    ueber_group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> SubGroup:
    """Creates a new group as a child of an ueber_group with ueber_group_id."""
    logger.info("POST group to ueber_group")
    return await group_view.post(
        group, token_payload, guards, ueber_group_id, inherit=inherit
    )


@ueber_group_router.post("/{ueber_group_id}/groups", status_code=201)
async def post_existing_groups_to_uebergroup(
    ueber_group_id: UUID,
    group_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of groups to an ueber_group."""
    logger.info("POST groups to ueber_group")
    hierarchy_response = []
    for group_id in group_ids:
        response = await group_view.post_add_child_to_parent(
            group_id,
            ueber_group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@ueber_group_router.get("/", status_code=200)
async def get_all_ueber_groups(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[UeberGroupRead]:
    """Returns all ueber_groups."""
    return await ueber_group_view.get(token_payload, guards)


@ueber_group_router.get("/{ueber_group_id}", status_code=200)
async def get_ueber_group_by_id(
    ueber_group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes an ueber_group."""
    return await ueber_group_view.delete(ueber_group_id, token_payload, guards)


@ueber_group_router.delete("/{ueber_group_id}/users", status_code=200)
async def remove_users_from_uebergroup(
    ueber_group_id: UUID,
    user_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes users from an ueber_group."""
    logger.info("DELETE users from ueber_group")
    for user_id in user_ids:
        await user_view.remove_child_from_parent(
            user_id,
            ueber_group_id,
            token_payload,
            guards,
        )


@ueber_group_router.delete("/{ueber_group_id}/groups", status_code=200)
async def remove_groups_from_uebergroup(
    ueber_group_id: UUID,
    group_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes groups from an ueber_group."""
    logger.info("DELETE groups from ueber_group")
    for group_id in group_ids:
        await group_view.remove_child_from_parent(
            group_id,
            ueber_group_id,
            token_payload,
            guards,
        )


# endregion UeberGroup

# region Group:


group_router = APIRouter()
group_view = BaseView(GroupCRUD)


@group_router.post("/", status_code=201)
async def post_group(
    group: GroupCreate,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> Group:
    """Creates a new group without a parent ueber-group."""
    logger.info("POST group")
    return await group_view.post(
        group,
        token_payload,
        guards,
    )


@group_router.post("/{group_id}/uebergroup/{ueber_group_id}", status_code=201)
async def post_group_to_existing_uebergroup(
    group_id: UUID,
    ueber_group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> BaseHierarchyModelRead:
    """Adds an existing group to an ueber_group."""
    logger.info("POST group to ueber_group")
    return await group_view.post_add_child_to_parent(
        group_id,
        ueber_group_id,
        token_payload,
        guards,
        inherit,
    )


@group_router.post("/{group_id}/users", status_code=201)
async def post_existing_users_to_group(
    group_id: UUID,
    user_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of existing users to a group."""
    logger.info("POST users to group")
    hierarchy_response = []
    for user_id in user_ids:
        response = await user_view.post_add_child_to_parent(
            user_id,
            group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@group_router.post("/{group_id}/subgroup", status_code=201)
async def post_sub_group_to_group(
    sub_group: SubGroupCreate,
    group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> SubGroup:
    """Creates a new sub_group as a child of group with group_id."""
    logger.info("POST sub_group to group")
    return await sub_group_view.post(
        sub_group, token_payload, guards, group_id, inherit=inherit
    )


@group_router.post("/{group_id}/subgroups", status_code=201)
async def post_existing_subgroups_to_group(
    group_id: UUID,
    sub_group_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of existing sub-groups by their id to a group."""
    logger.info("POST sub-groups to group")
    hierarchy_response = []
    for sub_group_id in sub_group_ids:
        response = await sub_group_view.post_add_child_to_parent(
            sub_group_id,
            group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@group_router.get("/", status_code=200)
async def get_all_groups(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[GroupRead]:
    """Returns all groups."""
    return await group_view.get(token_payload, guards)


@group_router.get("/{group_id}", status_code=200)
async def get_group_by_id(
    group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> GroupRead:
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
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a group."""
    return await group_view.delete(group_id, token_payload, guards)


@group_router.delete("/{group_id}/uebergroup/{ueber_group_id}", status_code=200)
async def remove_group_from_uebergroup(
    group_id: UUID,
    ueber_group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes a group from an ueber_group."""
    logger.info("DELETE group from ueber_group")
    return await group_view.remove_child_from_parent(
        group_id,
        ueber_group_id,
        token_payload,
        guards,
    )


@group_router.delete("/{group_id}/users", status_code=200)
async def remove_users_from_group(
    group_id: UUID,
    user_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes users from a group."""
    logger.info("DELETE users from group")
    for user_id in user_ids:
        await user_view.remove_child_from_parent(
            user_id,
            group_id,
            token_payload,
            guards,
        )


@group_router.delete("/{group_id}/subgroups", status_code=200)
async def remove_subgroups_from_group(
    group_id: UUID,
    sub_group_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes sub-groups from a group."""
    logger.info("DELETE sub-groups from a group")
    for sub_group_id in sub_group_ids:
        await sub_group_view.remove_child_from_parent(
            sub_group_id,
            group_id,
            token_payload,
            guards,
        )


# endregion Group

# region SubGroup:

sub_group_router = APIRouter()
sub_group_view = BaseView(SubGroupCRUD)


# Since stand-alone sub_groups are no longer allowed, this route is not needed anymore.
# Get back in again,if the CRUD for sub_groups initializes
# the super.__init__ with the allow_standalone=True!
# @sub_group_router.post("/", status_code=201)
# async def post_sub_group(
#     sub_group: SubGroupCreate,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
# ) -> SubGroup:
#     """Creates a new sub_group."""
#     logger.info("POST sub_group")
#     return await sub_group_view.post(
#         sub_group,
#         token_payload,
#         guards,
#     )


@sub_group_router.post("/{sub_group_id}/group/{group_id}", status_code=201)
async def post_existing_subgroup_to_group(
    sub_group_id: UUID,
    group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> BaseHierarchyModelRead:
    """Adds an existing sub_group to a group."""
    logger.info("POST sub_group to group")
    return await sub_group_view.post_add_child_to_parent(
        sub_group_id,
        group_id,
        token_payload,
        guards,
        inherit,
    )


@sub_group_router.post("/{sub_group_id}/users", status_code=201)
async def post_existing_users_to_subgroup(
    sub_group_id: UUID,
    user_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of users to a sub_group."""
    logger.info("POST users to sub_group")
    hierarchy_response = []
    for user_id in user_ids:
        response = await user_view.post_add_child_to_parent(
            user_id,
            sub_group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@sub_group_router.post("/{sub_group_id}/subsubgroup", status_code=201)
async def post_sub_sub_group_to_sub_group(
    sub_sub_group: SubSubGroupCreate,
    sub_group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> SubGroup:
    """Creates a new sub_sub_group as a child of sub_group with sub_group_id."""
    logger.info("POST sub_sub_group to sub_group")
    return await sub_sub_group_view.post(
        sub_sub_group, token_payload, guards, sub_group_id, inherit=inherit
    )


@sub_group_router.post("/{sub_group_id}/subsubgroups", status_code=201)
async def post_existing_subsubgroups_to_subgroup(
    sub_group_id: UUID,
    sub_sub_group_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of sub-sub-groups to a sub-group."""
    logger.info("POST sub-sub-groups to sub-group")
    hierarchy_response = []
    for sub_sub_group_id in sub_sub_group_ids:
        response = await sub_sub_group_view.post_add_child_to_parent(
            sub_sub_group_id,
            sub_group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@sub_group_router.get("/", status_code=200)
async def get_all_sub_groups(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[SubGroupRead]:
    """Returns all sub_groups."""
    return await sub_group_view.get(token_payload, guards)


@sub_group_router.get("/{sub_group_id}", status_code=200)
async def get_sub_group_by_id(
    sub_group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
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
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a sub_group."""
    return await sub_group_view.delete(sub_group_id, token_payload, guards)


@sub_group_router.delete("/{sub_group_id}/group/{group_id}", status_code=200)
async def remove_sub_group_from_group(
    sub_group_id: UUID,
    group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes a sub_group from a group."""
    logger.info("DELETE sub_group from group")
    return await sub_group_view.remove_child_from_parent(
        sub_group_id,
        group_id,
        token_payload,
        guards,
    )


@sub_group_router.delete("/{sub_group_id}/users", status_code=200)
async def remove_users_from_subgroup(
    sub_group_id: UUID,
    user_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes users from a sub-group."""
    logger.info("DELETE users from sub-group")
    for user_id in user_ids:
        await user_view.remove_child_from_parent(
            user_id,
            sub_group_id,
            token_payload,
            guards,
        )


@sub_group_router.delete("/{sub_group_id}/subsubgroups", status_code=200)
async def remove_subsubgroups_from_subgroup(
    sub_group_id: UUID,
    sub_sub_group_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes sub-sub-groups from a sub-group."""
    logger.info("DELETE sub-sub-groups from a sub-group")
    for sub_sub_group_id in sub_sub_group_ids:
        await sub_sub_group_view.remove_child_from_parent(
            sub_sub_group_id,
            sub_group_id,
            token_payload,
            guards,
        )


# endregion SubGroup

# region SubSubGroup:

sub_sub_group_router = APIRouter()
sub_sub_group_view = BaseView(SubSubGroupCRUD)


# Since stand-alone sub_sub_groups are no longer allowed, this route is not needed anymore.
# Get back in again,if the CRUD for sub_sub_groups initializes
# the super.__init__ with the allow_standalone=True!
# @sub_sub_group_router.post("/", status_code=201)
# async def post_sub_sub_group(
#     sub_sub_group: SubGroupCreate,
#     token_payload=Depends(get_http_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["Admin"])),
# ) -> SubGroup:
#     """Creates a new sub_sub_group."""
#     logger.info("POST sub_sub_group")
#     return await sub_sub_group_view.post(
#         sub_sub_group,
#         token_payload,
#         guards,
#     )


@sub_sub_group_router.post(
    "/{sub_sub_group_id}/subgroup/{sub_group_id}", status_code=201
)
async def post_existing_subsubgroup_to_subgroup(
    sub_sub_group_id: UUID,
    sub_group_id: UUID,
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> BaseHierarchyModelRead:
    """Adds an existing sub_sub_group to a sub_group."""
    logger.info("POST sub_sub_group to sub_group")
    return await sub_sub_group_view.post_add_child_to_parent(
        sub_sub_group_id,
        sub_group_id,
        token_payload,
        guards,
        inherit,
    )


@sub_sub_group_router.post("/{sub_sub_group_id}/users", status_code=201)
async def post_existing_users_to_subsubgroup(
    sub_sub_group_id: UUID,
    user_ids: list[UUID],
    inherit: Annotated[bool, Query()] = True,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> list[BaseHierarchyModelRead]:
    """Adds bulk of users to a sub_sub_group."""
    logger.info("POST users to sub_sub_group")
    hierarchy_response = []
    for user_id in user_ids:
        response = await user_view.post_add_child_to_parent(
            user_id,
            sub_sub_group_id,
            token_payload,
            guards,
            inherit,
        )
        hierarchy_response.append(response)
    return hierarchy_response


@sub_sub_group_router.get("/", status_code=200)
async def get_all_sub_sub_groups(
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["Admin"])),
) -> list[SubGroupRead]:
    """Returns all sub_sub_groups."""
    return await sub_sub_group_view.get(token_payload, guards)


@sub_sub_group_router.get("/{sub_sub_group_id}", status_code=200)
async def get_sub_sub_group_by_id(
    sub_sub_group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(roles=["User"])),
) -> SubGroupRead:
    """Returns a sub_sub_group with a specific sub_sub_group_id."""
    return await sub_sub_group_view.get_by_id(
        sub_sub_group_id,
        token_payload,
        guards,
    )


@sub_sub_group_router.put("/{sub_sub_group_id}", status_code=200)
async def put_sub_sub_group(
    sub_sub_group_id: UUID,
    sub_sub_group: SubGroupUpdate,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["Admin"])),
) -> SubGroup:
    """Updates a sub_sub_group."""
    return await sub_sub_group_view.put(
        sub_sub_group_id,
        sub_sub_group,
        token_payload,
        guards,
    )


@sub_sub_group_router.delete("/{sub_sub_group_id}", status_code=200)
async def delete_sub_sub_group(
    sub_sub_group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards=Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Deletes a sub_sub_group."""
    return await sub_sub_group_view.delete(sub_sub_group_id, token_payload, guards)


@sub_sub_group_router.delete(
    "/{sub_sub_group_id}/subgroup/{sub_group_id}", status_code=200
)
async def remove_sub_sub_group_from_group(
    sub_sub_group_id: UUID,
    sub_group_id: UUID,
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes a sub_sub_group from a sub_group."""
    logger.info("DELETE sub_sub_group from sub_group")
    return await sub_sub_group_view.remove_child_from_parent(
        sub_sub_group_id,
        sub_group_id,
        token_payload,
        guards,
    )


@sub_sub_group_router.delete("/{sub_sub_group_id}/users", status_code=200)
async def remove_users_from_subsubgroup(
    sub_sub_group_id: UUID,
    user_ids: list[UUID],
    token_payload=Depends(get_http_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:
    """Removes users from a sub-sub-group."""
    logger.info("DELETE users from sub-sub-group")
    for user_id in user_ids:
        await user_view.remove_child_from_parent(
            user_id,
            sub_sub_group_id,
            token_payload,
            guards,
        )


# endregion SubSubGroup
