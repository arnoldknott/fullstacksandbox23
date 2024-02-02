import logging
from typing import List

from core.security import guards
from crud.user import UserCRUD
from fastapi import APIRouter, Depends, HTTPException
from models.user import User, UserCreate, UserRead, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter()

# TBD: basically I don't need the user endpoints in the API currently,
# as everything is handled through the tokens issued by Azure.


@router.post("/", status_code=201)
async def post_user(
    user: UserCreate,
    # note: self-sign-up through security - controlled by token content,
    # that means, controlled by group and user membership in azure entra ad!
    # The roles assigned to users and groups decide about sign-up here.
    # This function allows admins to sign up users through API on top of that.
    # TBD: add admin guard!
    _=Depends(guards.current_azure_user_is_admin),
) -> User:
    """Creates a new user."""
    logger.info("POST user")
    print("=== user ===")
    print(user)
    async with UserCRUD() as crud:
        created_user = await crud.create(user)
    return created_user


@router.get("/")
async def get_all_users(
    _=Depends(guards.current_azure_user_is_admin),
) -> List[User]:
    """Returns all user."""
    logger.info("GET all user")
    async with UserCRUD() as crud:
        response = await crud.read_all()
    # crud = UserCRUD()
    # response = await crud.read_all()
    return response


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    calling_user: User = Depends(guards.current_azure_user_in_database),
    calling_user_is_admin: User = Depends(guards.current_azure_user_is_admin),
) -> UserRead:
    """Returns a user."""
    if calling_user.azure_user_id != user_id:
        if calling_user_is_admin is True:
            raise HTTPException(status_code=403, detail="Forbidden")
    logger.info("GET user")
    # crud = UserCRUD()
    try:
        user_id = int(user_id)
    except ValueError:
        logger.error("User ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        response = await crud.read_by_id_with_childs(user_id)
    return response


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user: UserUpdate = Depends(guards.current_azure_user_in_database),
) -> User:
    """Updates a user."""
    logger.info("PUT user")
    try:
        user_id = int(user_id)
    except ValueError:
        logger.error("User ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        old_user = await crud.read_by_id(user_id)
        updated_user = await crud.update(old_user, user)
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str = Depends(guards.current_azure_user_in_database),
) -> User:
    """Deletes a user."""
    logger.info("DELETE user")
    try:
        user_id = int(user_id)
    except ValueError:
        logger.error("User ID is not an integer")
        raise HTTPException(status_code=400, detail="Invalid user id")
    async with UserCRUD() as crud:
        result = await crud.delete(user_id)
    # print("=== result ===")
    # print(result)
    return result
