import logging
from typing import List

from uuid import UUID
from core.security import CurrentAzureTokenHasScope, CurrentAzureTokenHasRole, guards
from crud.user import UserCRUD
from fastapi import APIRouter, Depends, HTTPException
from models.user import User, UserCreate, UserRead, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)
async def post_user(
    user: UserCreate,
    # note: self-sign-up through security - controlled by token content,
    # that means, controlled by group and user membership in azure entra ad!
    # The roles assigned to users and groups decide about sign-up here.
    # This function allows admins to sign up users through API on top of that.
    _1=Depends(CurrentAzureTokenHasScope("api.write")),
    _2=Depends(CurrentAzureTokenHasRole("Admin")),
) -> User:
    """Creates a new user."""
    logger.info("POST user")
    async with UserCRUD() as crud:
        created_user = await crud.create(user)
    return created_user


@router.get("/")
async def get_all_users(
    _=Depends(CurrentAzureTokenHasRole("Admin")),
) -> List[User]:
    """Returns all user."""
    logger.info("GET all user")
    async with UserCRUD() as crud:
        response = await crud.read_all()
    return response


@router.get("/azure/{azure_user_id}")
async def get_user_by_azure_user_id(
    azure_user_id: str,
    current_user: UserRead = Depends(guards.current_azure_user_in_database),
    check_admin_role=Depends(CurrentAzureTokenHasRole("Admin", require=False)),
) -> UserRead:
    """Returns a user based on its azure user id."""
    if (str(current_user.azure_user_id) != str(azure_user_id)) and (
        check_admin_role is False
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    logger.info("GET user")

    update_last_access = True
    if check_admin_role is True:
        update_last_access = False

    try:
        azure_user_id = UUID(azure_user_id)
    except ValueError:
        logger.error("User ID is not an UUID")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        response = await crud.read_by_azure_user_id_with_childs(
            azure_user_id, update_last_access
        )
    return response


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    current_user: UserRead = Depends(guards.current_azure_user_in_database),
    check_admin_role=Depends(CurrentAzureTokenHasRole("Admin", require=False)),
) -> UserRead:
    """Returns a user with a specific user_id."""
    if (str(current_user.user_id) != str(user_id)) and (check_admin_role is False):
        raise HTTPException(status_code=403, detail="Access denied")

    logger.info("GET user")

    update_last_access = True
    if check_admin_role is True:
        update_last_access = False

    try:
        user_id = UUID(user_id)
    except ValueError:
        logger.error("User ID is not an UUID")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        response = await crud.read_by_id_with_childs(user_id, update_last_access)
    return response


# TBD: write tests for this:
@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data_update: UserUpdate,
    current_user: UserUpdate = Depends(guards.current_azure_user_in_database),
    _=Depends(CurrentAzureTokenHasScope("api.write")),
    check_admin_role=Depends(CurrentAzureTokenHasRole("Admin", require=False)),
) -> User:
    """Updates a user."""
    if (str(current_user.user_id) != str(user_id)) and (check_admin_role is False):
        raise HTTPException(status_code=403, detail="Access denied")

    logger.info("GET user")

    update_last_access = True
    if check_admin_role is True:
        update_last_access = False

    try:
        user_id = UUID(user_id)
    except ValueError:
        logger.error("User ID is not an UUID")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        old_user = await crud.read_by_id(user_id)
        updated_user = await crud.update(old_user, user_data_update, update_last_access)
    return updated_user


# TBD: write tests for this:
@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserUpdate = Depends(guards.current_azure_user_in_database),
    _=Depends(CurrentAzureTokenHasScope("api.write")),
    check_admin_role=Depends(CurrentAzureTokenHasRole("Admin", require=False)),
) -> User:
    """Deletes a user."""
    if (str(current_user.user_id) != str(user_id)) and (check_admin_role is False):
        raise HTTPException(status_code=403, detail="Access denied")

    logger.info("DELETE user")

    try:
        user_id = UUID(user_id)
    except ValueError:
        logger.error("User ID is not an UUID")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        result = await crud.delete(user_id)
    return result
