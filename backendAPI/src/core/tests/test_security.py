# from unittest.mock import AsyncMock, patch

import pytest
import uuid
from typing import Annotated
from fastapi import Depends, FastAPI
from models.user import User, UserRead
from crud.user import UserCRUD
from fastapi.encoders import jsonable_encoder
from core.security import (
    get_azure_jwks,
    CurrentAzureUserInDatabase,
    CurrentAzureTokenHasScope,
    CurrentAzureTokenHasRole,
)
from httpx import AsyncClient

from tests.utils import (
    # token_payload_roles_user,
    # token_payload_scope_api_write,
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_one_group,
    token_payload_many_groups,
    token_payload_roles_user_admin,
    token_payload_roles_admin_user,
    token_payload_roles_admin,
    token_payload_roles_user,
    token_payload_scope_api_read,
    token_payload_scope_api_write,
    token_payload_scope_api_read_write,
    one_test_user,
)

# Testing token validation:


@pytest.mark.anyio
async def test_get_azure_jwks_no_cache():
    """Tests the jwks endpoint."""
    jwks = await get_azure_jwks(no_cache=True)

    assert "keys" in jwks
    for key in jwks["keys"]:
        assert "kid" in key
        assert "n" in key
        assert "e" in key
        assert "kty" in key
        assert "use" in key
        assert "x5t" in key
        assert "x5c" in key
        assert "issuer" in key


@pytest.mark.anyio
async def test_get_azure_jwks():
    """Tests the jwks endpoint."""
    jwks = await get_azure_jwks()

    print("=== jwks ===")
    print(jwks)

    assert "keys" in jwks
    for key in jwks["keys"]:
        assert "kid" in key
        assert "n" in key
        assert "e" in key
        assert "kty" in key
        assert "use" in key
        assert "x5t" in key
        assert "x5c" in key
        assert "issuer" in key


# Testing user self signup


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_write,
            # **token_payload_roles_user,
            **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_write,
            # **token_payload_roles_user,
            # **token_payload_one_group,
        },
    ],
    indirect=True,
)
async def test_azure_user_self_signup(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests if a new user can sign up by themselves."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_azure_user_self_signup")
    def temp_endpoint(
        current_user: Annotated[str, Depends(CurrentAzureUserInDatabase())]
    ):
        """Returns the result of the guard."""
        print("=== current_user ===")
        print(current_user)
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_azure_user_self_signup",
    )

    assert response.status_code == 200
    current_user = response.json()

    assert current_user["azure_user_id"] == one_test_user["azure_user_id"]
    assert current_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]

    # Verify that the user was created in the database
    async with UserCRUD() as crud:
        db_user = await crud.read_by_azure_user_id(one_test_user["azure_user_id"])
    assert db_user is not None
    db_user_json = jsonable_encoder(db_user)
    assert db_user_json["azure_user_id"] == one_test_user["azure_user_id"]
    assert db_user_json["azure_tenant_id"] == one_test_user["azure_tenant_id"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {},
        {
            # **token_payload_user_id,
            **token_payload_tenant_id,
        },
        {
            **token_payload_user_id,
            # **token_payload_tenant_id,
        },
    ],
    indirect=True,
)
async def test_azure_user_self_signup_invalid_token(
    async_client: AsyncClient, app_override_get_azure_payload_dependency: FastAPI
):
    """Tests that a new user cannot sign itself up without access token."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_azure_user_self_signup_missing_token")
    def temp_endpoint(
        current_user: Annotated[str, Depends(CurrentAzureUserInDatabase())]
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_azure_user_self_signup_missing_token",
    )

    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            # **token_payload_roles_user,
            "groups": token_payload_many_groups["groups"]
            + token_payload_one_group["groups"],
        }
    ],
    indirect=True,
)
async def test_existing_azure_user_has_new_group_in_token(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_test_user_with_groups: User,
):
    """Tests if a new user can sign up by themselves."""
    # preparing the test: adds a user to the database and ensure that this user is member of 3 groups:
    existing_user = add_one_test_user_with_groups
    async with UserCRUD() as crud:
        existing_db_user = await crud.read_by_id_with_childs(existing_user.user_id)

    print("=== existing_db_user ===")
    print(existing_db_user)
    print("=== existing_db_user.azure_groups ===")
    print(existing_db_user.azure_groups)
    print("=== existing_db_user.model_dump() ===")
    print(existing_db_user.model_dump())

    # existing_db_user_read = UserRead(**jsonable_encoder(existing_db_user))

    # print("=== existing_db_user_read ===")
    # print(existing_db_user_read)

    assert len(existing_db_user.azure_groups) == 3
    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard adn call it:
    @app.get("/test_existing_azure_user_has_new_group_in_token")
    def temp_endpoint(
        current_user: Annotated[str, Depends(CurrentAzureUserInDatabase())]
    ):
        """Returns the result of the guard."""
        return current_user

    response = await async_client.get(
        "/test_existing_azure_user_has_new_group_in_token",
    )

    updated_user = response.json()

    assert updated_user["azure_user_id"] == one_test_user["azure_user_id"]
    assert updated_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]

    # Verify that the user now has the new group in the database
    async with UserCRUD() as crud:
        db_user = await crud.read_by_id_with_childs(existing_user.user_id)
    assert db_user is not None
    # db_user_json = jsonable_encoder(db_user)
    # TBD: this is unit tests for the crud: checking the models are correct.
    # assert db_user.azure_user_id == uuid.UUID(one_test_user["azure_user_id"])
    print("=== db_user ===")
    print(db_user)
    print("=== db_user.azure_groups ===")
    print(db_user.azure_groups)

    # db_user = dict(db_user)
    # print("=== dict(db_user) ===")
    # print(db_user)
    # print("=== type(db_user) after dict() ===")
    # print(type(db_user))
    # print("=== db_user['azure_groups'] ===")
    # print(db_user["azure_groups"])
    # print("=== type(db_user['azure_groups']) ===")
    # print(type(db_user["azure_groups"]))

    print("=== db_user.model_dump() ===")
    print(db_user.model_dump())
    db_user = db_user.model_dump()
    print("=== db_user.model_dump() ===")
    print(db_user)
    print("=== type(db_user) ===")
    print(type(db_user))
    print("=== db_user['azure_groups'] ===")
    print(db_user["azure_groups"])
    print("=== type(db_user['azure_groups']) ===")
    print(type(db_user["azure_groups"]))

    # assert db_user["azure_user_id"] == one_test_user["azure_user_id"]
    # assert db_user["azure_tenant_id"] == one_test_user["azure_tenant_id"]
    assert db_user["azure_user_id"] == uuid.UUID(one_test_user["azure_user_id"])
    assert db_user["azure_tenant_id"] == uuid.UUID(one_test_user["azure_tenant_id"])
    assert len(db_user["azure_groups"]) == 4
    assert any(
        group["azure_group_id"] == uuid.UUID(token_payload_one_group["groups"][0])
        for group in db_user["azure_groups"]
    )


# Testing guards:

## Testing admin guard:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_roles_admin,
        },
        {
            **token_payload_roles_user_admin,
        },
        {
            **token_payload_roles_admin_user,
        },
    ],
    indirect=True,
)
async def test_admin_guard_with_admin_role_in_azure_mocked_token_payload(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_admin_guard_with_admin_role_in_azure_mocked_token_payload")
    def temp_endpoint(current_user: bool = Depends(CurrentAzureTokenHasRole("Admin"))):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_admin_guard_with_admin_role_in_azure_mocked_token_payload",
    )

    assert response.status_code == 200
    token_contains_role_admin = response.json()
    assert token_contains_role_admin is True


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_roles_user,
        },
        {},
    ],
    indirect=True,
)
async def test_admin_guard_without_admin_role_in_azure_mocked_token_payload(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_admin_guard_without_admin_role_in_azure_mocked_token_payload")
    def temp_endpoint(current_user: bool = Depends(CurrentAzureTokenHasRole("Admin"))):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_admin_guard_without_admin_role_in_azure_mocked_token_payload",
    )

    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_roles_user,
        },
        {},
    ],
    indirect=True,
)
async def test_admin_guard_without_admin_role_in_azure_mocked_token_payload_return_false(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get(
        "/test_admin_guard_without_admin_role_in_azure_mocked_token_payload_return_false"
    )
    def temp_endpoint(
        current_user: bool = Depends(CurrentAzureTokenHasRole("Admin", require=False))
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_admin_guard_without_admin_role_in_azure_mocked_token_payload_return_false",
    )

    assert response.status_code == 200
    token_contains_role_admin = response.json()
    assert token_contains_role_admin is False


## Testing scope guard:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_scope_api_read,
        },
        {
            **token_payload_scope_api_read_write,
        },
    ],
    indirect=True,
)
async def test_current_azure_token_has_scope_api_read(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_current_azure_token_has_scope_api_read")
    def temp_endpoint(
        current_user: bool = Depends(CurrentAzureTokenHasScope("api.read")),
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_current_azure_token_has_scope_api_read",
    )

    assert response.status_code == 200
    token_contains_scope_api_read = response.json()
    assert token_contains_scope_api_read is True


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_scope_api_write,
        },
        {},
    ],
    indirect=True,
)
async def test_current_azure_token_missing_scope_api_read(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_current_azure_token_missing_scope_api_read")
    def temp_endpoint(
        current_user: bool = Depends(CurrentAzureTokenHasScope("api.read")),
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_current_azure_token_missing_scope_api_read",
    )

    assert response.status_code == 403
    assert response.text == '{"detail":"Access denied"}'


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_scope_api_write,
        },
        {},
    ],
    indirect=True,
)
async def test_current_azure_token_missing_scope_api_read_return_false(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests admin guard for tokens that contain the role Admin."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_current_azure_token_missing_scope_api_read_return_false")
    def temp_endpoint(
        current_user: bool = Depends(
            CurrentAzureTokenHasScope("api.read", require=False)
        ),
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_current_azure_token_missing_scope_api_read_return_false",
    )

    assert response.status_code == 200
    token_contains_scope_api_read = response.json()
    assert token_contains_scope_api_read is False


## Testing valid token guard:
