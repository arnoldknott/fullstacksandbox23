import pytest
import uuid
from typing import Annotated, List
from fastapi import Depends, FastAPI
from httpx import AsyncClient

from models.identity import User, UserRead
from core.security import (
    get_azure_jwks,
    CurrentAccessTokenIsValid,
    CurrentAzureUserInDatabase,
    CurrentAccessTokenHasScope,
    CurrentAccessTokenHasRole,
)
from routers.api.v1.user import get_user_by_id


from tests.utils import (
    # token_payload_roles_user,
    # token_payload_scope_api_write,
    token_admin_read,
    token_payload_user_id,
    token_payload_tenant_id,
    token_payload_one_group,
    token_payload_one_random_group,
    token_payload_many_groups,
    token_payload_roles_user_admin,
    token_payload_roles_admin_user,
    token_payload_roles_admin,
    token_payload_roles_user,
    token_payload_scope_api_read,
    token_payload_scope_api_write,
    token_payload_scope_api_read_write,
    many_test_azure_users,
)

# region: Testing token validation:


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


# endregion

# region: Testing user self signup


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
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_write,
            **token_payload_roles_user,
            # **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            # **token_payload_scope_api_write,
            **token_payload_roles_admin,
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
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_azure_user_self_signup",
    )
    assert response.status_code == 200
    current_user = response.json()
    assert current_user["azure_user_id"] == many_test_azure_users[0]["azure_user_id"]
    assert (
        current_user["azure_tenant_id"] == many_test_azure_users[0]["azure_tenant_id"]
    )

    # To verify that the user is in the database, calling the endpoint to get the user by id with admin token:
    db_user = await get_user_by_id(current_user["id"], token_admin_read)
    assert db_user is not None
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[0]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[0]["azure_tenant_id"]
    )
    assert db_user.created_at is not None
    assert db_user.last_accessed_at is not None
    assert db_user.created_at is not None
    assert db_user.last_accessed_at >= db_user.created_at


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
            + token_payload_one_random_group["groups"],
        }
    ],
    indirect=True,
)
async def test_existing_azure_user_has_new_group_in_token(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[User],
):
    """Tests if an user that got added to a new azure group also gets added the new azure group in the database."""
    # preparing the test: adds a user to the database and ensure that this user is member of 3 groups:
    existing_user = await add_one_azure_test_user(0)
    # existing_user = existing_users[0]
    existing_db_user = await get_user_by_id(str(existing_user.id), token_admin_read)

    assert len(existing_db_user.azure_groups) == 3
    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard adn call it:
    @app.get("/test_existing_azure_user_has_new_group_in_token")
    def temp_endpoint(
        current_user: Annotated[str, Depends(CurrentAzureUserInDatabase())]
    ) -> UserRead:
        """Returns the result of the guard."""
        return current_user

    response = await async_client.get(
        "/test_existing_azure_user_has_new_group_in_token",
    )

    updated_user = response.json()

    assert updated_user["azure_user_id"] == many_test_azure_users[0]["azure_user_id"]
    assert (
        updated_user["azure_tenant_id"] == many_test_azure_users[0]["azure_tenant_id"]
    )

    # Verify that the user now has the new group in the database
    db_user = await get_user_by_id(str(existing_user.id), token_admin_read)
    assert db_user is not None
    assert db_user.azure_user_id == uuid.UUID(many_test_azure_users[0]["azure_user_id"])
    assert db_user.azure_tenant_id == uuid.UUID(
        many_test_azure_users[0]["azure_tenant_id"]
    )
    assert len(db_user.azure_groups) == 7

    azure_groups = db_user.azure_groups
    assert any(
        group.id == uuid.UUID(token_payload_one_random_group["groups"][0])
        for group in azure_groups
    )

    # db_user_json_encoded = jsonable_encoder(db_user)
    # print("=== db_user_json_encoded ===")
    # print(db_user_json_encoded)

    # db_user = db_user.model_dump()
    # assert db_user["azure_user_id"] == uuid.UUID(many_test_azure_users[0]["azure_user_id"])
    # assert db_user["azure_tenant_id"] == uuid.UUID(many_test_azure_users[0]["azure_tenant_id"])
    # assert len(db_user["azure_groups"]) == 4
    # assert any(
    #     group["id"] == uuid.UUID(token_payload_one_group["groups"][0])
    #     for group in db_user["azure_groups"]
    # )


# endregion


# region: Testing login (for already sign-up user):


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_roles_user,
        },
        # note: admin is logging in self - so last_accessed_at should change!
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_roles_admin,
        },
    ],
    indirect=True,
)
async def test_existing_user_logs_in(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    add_one_azure_test_user: List[UserRead],
):
    """Test an existing user logs in successfully"""

    # mocks the access token:
    app = app_override_get_azure_payload_dependency
    user_in_database = await add_one_azure_test_user(0)
    # user_in_database = existing_users[0]

    # create a temporary route that uses the guard:
    @app.get("/test_existing_user_logs_in")
    def temp_endpoint(
        current_user: Annotated[str, Depends(CurrentAzureUserInDatabase())]
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_existing_user_logs_in",
    )

    assert response.status_code == 200
    response_user = response.json()
    modelled_response_user = UserRead(**response_user)
    assert "id" in response_user
    assert response_user["azure_user_id"] == str(user_in_database.azure_user_id)
    assert response_user["azure_tenant_id"] == str(user_in_database.azure_tenant_id)
    # TBD: admin access should not change the last_accessed_at!
    assert modelled_response_user.last_accessed_at > user_in_database.last_accessed_at


# endregion

# region: Testing guards:

# TBD: add tests for other implementation of the guards,
#      the way the BaseView uses them
#      might not be necessary, as those are calling the ones tested here.

# region: ## Testing valid token guard:


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        # This allows any user from the tenant to access the route - without scope and roles:
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read,
            **token_payload_roles_user,
            **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_write,
            **token_payload_roles_user,
            **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_scope_api_read_write,
            **token_payload_roles_user,
            **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_roles_admin,
            **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_roles_admin_user,
            **token_payload_one_group,
        },
        {
            **token_payload_user_id,
            **token_payload_tenant_id,
            **token_payload_roles_user,
            **token_payload_many_groups,
        },
    ],
    indirect=True,
)
async def test_valid_azure_token(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests if a valid token is accepted."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_valid_azure_token")
    def temp_endpoint(
        current_user: bool = Depends(CurrentAccessTokenIsValid()),
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_valid_azure_token",
    )

    assert response.status_code == 200
    token_is_valid = response.json()
    assert token_is_valid is True


@pytest.mark.anyio
@pytest.mark.parametrize("mocked_get_azure_token_payload", [{}])
async def test_invalid_azure_token(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests if an invalid token is rejected."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_invalid_azure_token")
    def temp_endpoint(
        current_user: bool = Depends(CurrentAccessTokenIsValid()),
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_invalid_azure_token",
    )

    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token"}'


@pytest.mark.anyio
@pytest.mark.parametrize("mocked_get_azure_token_payload", [{}])
async def test_invalid_azure_token_return_false(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests if an invalid token returns False."""

    app = app_override_get_azure_payload_dependency

    # create a temporary route that uses the guard:
    @app.get("/test_invalid_azure_token_return_false")
    def temp_endpoint(
        current_user: bool = Depends(CurrentAccessTokenIsValid(require=False)),
    ):
        """Returns the result of the guard."""
        return current_user

    # call that temporary route:
    response = await async_client.get(
        "/test_invalid_azure_token_return_false",
    )

    assert response.status_code == 200
    token_is_valid = response.json()
    assert token_is_valid is False


# endregion

# region: ## Testing scope guard:


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
        current_user: bool = Depends(CurrentAccessTokenHasScope("api.read")),
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
        current_user: bool = Depends(CurrentAccessTokenHasScope("api.read")),
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
            CurrentAccessTokenHasScope("api.read", require=False)
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


# endregion

# region: ## Testing role guard:


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
    def temp_endpoint(current_user: bool = Depends(CurrentAccessTokenHasRole("Admin"))):
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
    def temp_endpoint(current_user: bool = Depends(CurrentAccessTokenHasRole("Admin"))):
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
        current_user: bool = Depends(CurrentAccessTokenHasRole("Admin", require=False))
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


# endregion

# TBD: add tests for group guards

# endregion
