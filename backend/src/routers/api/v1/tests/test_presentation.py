"""Tests for presentation API endpoints."""

import pytest

from core.types import CurrentUserData
from crud.presentation import PresentationCRUD
from models.presentation import Presentation
from routers.api.v1.tests.base import BaseTest
from tests.utils import (
    current_user_data_admin,
    token_admin,
    token_admin_read,
    token_admin_read_write,
    token_admin_write,
    token_user1_read,
    token_user1_read_write,
    token_user1_write,
)
from tests.utils_presentations import (
    many_test_presentations,
    one_test_presentation,
    one_test_presentation_multi_segment_path,
    one_test_presentation_uuid_like_path,
    one_test_presentation_without_path,
    presentation_update_data,
    wrong_test_presentations,
)


class TestPresentation(BaseTest):
    """Test suite for presentation API endpoints."""

    # Class attributes for BaseTest
    crud = PresentationCRUD
    model = Presentation
    router_path = "/api/v1/presentation/"
    _test_data_single = one_test_presentation
    _test_data_wrong = wrong_test_presentations
    _test_data_many = many_test_presentations
    _test_data_update = presentation_update_data

    # Test methods - just declare them, BaseTest handles implementation
    ## POST tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read_write, token_user1_read_write],
        indirect=True,
    )
    async def test_post_success(
        self, test_data_single, mocked_provide_http_token_payload
    ):
        """Test POST presentation success."""
        await super().run_post_success(
            test_data_single, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_post_success_with_query_and_fragment(
        self, mocked_provide_http_token_payload
    ):
        """Test POST presentation accepts endpoint paths with query and fragment."""
        presentation_with_query_fragment = {
            "source": "https://example.com/presentation-with-metadata",
            "path": "/presentations/intro-to-fullstack-sandbox23?slide=2&mode=share#overview",
        }

        response = await self.async_client.post(
            self.router_path, json=presentation_with_query_fragment
        )

        assert response.status_code == 201
        assert response.json()["path"] == presentation_with_query_fragment["path"]

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_post_duplicate_path_fails(
        self, test_data_single, mocked_provide_http_token_payload
    ):
        """Test POST presentation rejects a duplicate path."""
        response = await self.async_client.post(self.router_path, json=test_data_single)
        assert response.status_code == 201

        duplicate_response = await self.async_client.post(
            self.router_path, json=test_data_single
        )

        assert duplicate_response.status_code == 403
        assert duplicate_response.json()["detail"] == "Presentation - Forbidden."

    @pytest.mark.anyio
    async def test_post_missing_auth(self, test_data_single):
        """Test POST fails without authentication."""
        await super().run_post_missing_auth(test_data_single)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read, token_admin_write, token_user1_read, token_user1_write],
        indirect=True,
    )
    async def test_post_fails_authorization(
        self, test_data_single, mocked_provide_http_token_payload
    ):
        """Test POST presentation success."""
        await super().run_post_fails_authorization(
            test_data_single, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_post_invalid_data(
        self, test_data_wrong, mocked_provide_http_token_payload
    ):
        """Test POST presentation with invalid data fails."""
        await super().run_post_invalid_data(
            test_data_wrong, mocked_provide_http_token_payload
        )

    ## GET tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read, token_user1_read],
        indirect=True,
    )
    async def test_get_all_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all presentations success."""
        await super().run_get_all_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    async def test_get_all_missing_auth(self, added_resources):
        """Test GET all fails without authentication."""
        await super().run_get_all_missing_auth(added_resources)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin], indirect=True
    )
    @pytest.mark.anyio
    async def test_get_all_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all fails without proper authorization."""
        await super().run_get_all_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read_write, token_user1_read_write],
        indirect=True,
    )
    async def test_get_by_id_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET presentation by ID success."""
        await super().run_get_by_id_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_not_found(self, mocked_provide_http_token_payload):
        """Test GET by ID returns 404 for non-existent presentation."""
        await super().run_get_by_id_not_found(mocked_provide_http_token_payload)

    # @pytest.mark.anyio
    # async def test_get_by_id_missing_auth(self, added_resources):
    #     """Test GET by ID fails without authentication."""
    #     await super().run_get_by_id_missing_auth(added_resources)

    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload",
    #     [token_admin, token_admin_write, token_user1_write],
    #     indirect=True,
    # )
    # async def test_get_by_id_fails_authorization(
    #     self, added_resources, mocked_provide_http_token_payload
    # ):
    #     """Test GET presentation by ID fails without proper authorization."""
    #     await super().run_get_by_id_fails_authorization(
    #         added_resources, mocked_provide_http_token_payload
    #     )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_admin_write, token_user1_write],
        indirect=True,
    )
    async def test_get_by_id_with_auth_and_public_policy_success(
        self,
        register_current_user,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test optional-auth GET by ID succeeds with auth and public policy."""
        await super().run_get_by_id_with_auth_and_public_policy_success(
            register_current_user,
            add_one_test_resource,
            add_one_test_access_policy,
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_user1_write], indirect=True
    )
    async def test_get_by_id_with_auth_and_without_public_policy_fails(
        self, register_current_user, add_one_test_resource
    ):
        """Test optional-auth GET by ID returns 404 with auth and no public policy."""
        await super().run_get_by_id_with_auth_and_without_public_policy_fails(
            register_current_user,
            add_one_test_resource,
        )

    @pytest.mark.anyio
    async def test_get_by_id_without_auth_and_public_policy_success(
        self,
        register_current_user,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test optional-auth GET by ID succeeds without auth when public policy exists."""
        await super().run_get_by_id_without_auth_and_public_policy_success(
            register_current_user,
            add_one_test_resource,
            add_one_test_access_policy,
        )

    @pytest.mark.anyio
    async def test_get_by_id_without_auth_and_without_public_policy_fails(
        self, register_current_user, add_one_test_resource
    ):
        """Test optional-auth GET by ID returns 404 without auth and no public policy."""
        await super().run_get_by_id_without_auth_and_without_public_policy_fails(
            register_current_user,
            add_one_test_resource,
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_admin_write, token_user1_write],
        indirect=True,
    )
    async def test_get_by_path_with_auth(
        self,
        register_current_user,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test GET presentation by path success with authentication."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation,
            CurrentUserData(**current_user_data_admin),
        )
        await add_one_test_access_policy(
            {
                "resource_id": str(presentation.id),
                "action": "read",
                "public": True,
            },
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path{presentation.path}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(presentation.id)
        assert data["source"] == presentation.source
        assert data["path"] == presentation.path

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_user1_write], indirect=True
    )
    async def test_get_by_path_with_auth_and_without_public_access_policy_fails(
        self, register_current_user, add_one_test_resource
    ):
        """Test GET presentation by path fails without public access policy."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation,
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path{presentation.path}"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Presentation not found."

    @pytest.mark.anyio
    async def test_get_by_path_without_auth(
        self,
        register_current_user,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test GET presentation by path success without authentication."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation,
            CurrentUserData(**current_user_data_admin),
        )
        await add_one_test_access_policy(
            {
                "resource_id": str(presentation.id),
                "action": "read",
                "public": True,
            },
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path{presentation.path}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(presentation.id)
        assert data["source"] == presentation.source
        assert data["path"] == presentation.path

    @pytest.mark.anyio
    async def test_get_by_path_without_auth_and_without_public_access_policy_fails(
        self, register_current_user, add_one_test_resource
    ):
        """Test GET presentation by path fails without auth and policy."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation,
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path{presentation.path}"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Presentation not found."

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_path_multi_segment_success(
        self, register_current_user, add_one_test_resource
    ):
        """Test GET presentation by multi-segment path success."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation_multi_segment_path,
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path{presentation.path}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(presentation.id)
        assert data["path"] == presentation.path

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_path_without_leading_slash_resolves(
        self, register_current_user, add_one_test_resource
    ):
        """Test GET presentation by path resolves even when request omits leading slash."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation_multi_segment_path,
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path/{presentation.path.lstrip('/')}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(presentation.id)
        assert data["path"] == presentation.path

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_path_with_uuid_like_string_success(
        self, register_current_user, add_one_test_resource
    ):
        """Test GET presentation by UUID-like path string success."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation_uuid_like_path,
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(
            f"{self.router_path}path{presentation.path}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(presentation.id)
        assert data["path"] == presentation.path

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_path_not_found(self, mocked_provide_http_token_payload):
        """Test GET presentation by path returns 404 for non-existent path."""
        response = await self.async_client.get(
            f"{self.router_path}path/presentation/this-path-does-not-exist"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Presentation not found."

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_success_when_presentation_path_is_none(
        self, register_current_user, add_one_test_resource
    ):
        """Test GET presentation by id works when presentation path is None."""
        await register_current_user(current_user_data_admin)
        presentation = await add_one_test_resource(
            PresentationCRUD,
            one_test_presentation_without_path,
            CurrentUserData(**current_user_data_admin),
        )

        response = await self.async_client.get(f"{self.router_path}{presentation.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(presentation.id)
        assert data["source"] == presentation.source
        assert data["path"] is None

    ## PUT tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_success(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT presentation success."""
        await super().run_put_success(
            added_resources, update_data, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_not_found(self, update_data, mocked_provide_http_token_payload):
        """Test PUT returns 404 for non-existent presentation."""
        await super().run_put_not_found(update_data, mocked_provide_http_token_payload)

    @pytest.mark.anyio
    async def test_put_missing_auth(self, added_resources, update_data):
        """Test PUT fails without authentication."""
        await super().run_put_missing_auth(added_resources, update_data)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_user1_read, token_user1_write],
        indirect=True,
    )
    async def test_put_fails_authorization(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT presentation fails without proper authorization."""
        await super().run_put_fails_authorization(
            added_resources, update_data, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_fails_invalid_data(
        self, added_resources, test_data_wrong, mocked_provide_http_token_payload
    ):
        """Test PUT presentation with invalid data fails."""
        await super().run_put_fails_invalid_data(
            added_resources, test_data_wrong, mocked_provide_http_token_payload
        )

    ## DELETE tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE presentation success."""
        await super().run_delete_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_not_found(self, mocked_provide_http_token_payload):
        """Test DELETE returns 404 for non-existent presentation."""
        await super().run_delete_not_found(mocked_provide_http_token_payload)

    @pytest.mark.anyio
    async def test_delete_missing_auth(self, added_resources):
        """Test DELETE fails without authentication."""
        await super().run_delete_missing_auth(added_resources)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_user1_read, token_user1_write],
        indirect=True,
    )
    async def test_delete_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE presentation fails without proper authorization."""
        await super().run_delete_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )
