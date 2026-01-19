"""Tests for presentation API endpoints."""

import pytest

from crud.presentation import PresentationCRUD
from models.presentation import Presentation
from tests.utils import (
    token_admin_read_write,
    token_user1_read_write,
    token_admin_read,
    token_admin_write,
    token_user1_read,
    token_user1_write,
)
from tests.utils_presentations import (
    one_test_presentation,
    many_test_presentations,
    presentation_update_data,
)
from routers.api.v1.tests.base import BaseTest


class TestPresentationEndpoints(BaseTest):
    """Test suite for presentation API endpoints."""

    # Class attributes for BaseTest
    crud = PresentationCRUD
    model = Presentation
    router_path = "/api/v1/presentation/"
    _test_data_single = one_test_presentation
    _test_data_many = many_test_presentations
    _test_data_update = presentation_update_data

    # Test methods - just declare them, BaseTest handles implementation

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
        await super().test_post_success(
            test_data_single, mocked_provide_http_token_payload
        )

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
        await super().test_post_fails_authorization(
            test_data_single, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_all_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all presentations success."""
        await super().test_get_all_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET presentation by ID success."""
        await super().test_get_by_id_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    async def test_get_public_by_id_success(
        self, add_one_test_access_policy, added_resources
    ):
        """Test public GET presentation by ID success (no auth)."""
        await super().test_get_public_by_id_success(
            add_one_test_access_policy, added_resources
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_success(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT presentation success."""
        await super().test_put_success(
            added_resources, update_data, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE presentation success."""
        await super().test_delete_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    async def test_post_missing_auth(self, test_data_single):
        """Test POST fails without authentication."""
        await super().test_post_missing_auth(test_data_single)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_not_found(self, mocked_provide_http_token_payload):
        """Test GET by ID returns 404 for non-existent presentation."""
        await super().test_get_by_id_not_found(mocked_provide_http_token_payload)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_not_found(self, update_data, mocked_provide_http_token_payload):
        """Test PUT returns 404 for non-existent presentation."""
        await super().test_put_not_found(update_data, mocked_provide_http_token_payload)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_not_found(self, mocked_provide_http_token_payload):
        """Test DELETE returns 404 for non-existent presentation."""
        await super().test_delete_not_found(mocked_provide_http_token_payload)
