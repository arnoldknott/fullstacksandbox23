"""Tests for Presentation SocketIO namespace."""

import pytest

from crud.presentation import PresentationCRUD
from models.presentation import Presentation
from tests.utils import (
    session_id_admin_read_write_socketio,
    session_id_user1_read_write_socketio,
)
from tests.utils_presentations import (
    many_test_presentations,
    one_test_presentation,
    presentation_update_data,
)

from .base import BaseSocketIOTest


class TestPresentation(BaseSocketIOTest):
    """Test suite for Presentation SocketIO namespace."""

    namespace_path = "/presentation"
    crud = PresentationCRUD
    model = Presentation
    _test_data_single = one_test_presentation
    _test_data_many = many_test_presentations
    _test_data_update = presentation_update_data
    _parent_model = None  # Presentation is standalone

    # Submit Create Tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_submit_create_with_parent_success(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful presentation creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            session_ids,
            access_to_one_parent,
        )

    @pytest.mark.anyio
    async def test_submit_create_public_with_parent_fails(
        self,
        socketio_test_client,
    ):
        """Test failing presentation creation."""
        await super().run_submit_create_fails(
            socketio_test_client,
            expected_error="No session id.",
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    @pytest.mark.anyio
    async def test_submit_create_without_parent_success(
        self,
        socketio_test_client,
        session_ids,
    ):
        """Test successful presentation creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            session_ids,
        )

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_fails(
        self,
        socketio_test_client,
    ):
        """Test failing presentation creation."""
        await super().run_submit_create_fails(
            socketio_test_client,
            expected_error="No session id.",
        )

    # Submit Update Tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_submit_update_success(
        self,
        socketio_test_client,
        add_one_test_resource,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful presentation update."""
        await super().run_submit_update_success(
            socketio_test_client,
            add_one_test_resource,
            session_ids,
            access_to_one_parent,
        )

    # Delete Tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_delete_success(
        self,
        socketio_test_client,
        add_one_test_resource,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful presentation deletion."""
        await super().run_delete_success(
            socketio_test_client,
            add_one_test_resource,
            session_ids,
            access_to_one_parent,
        )

    # Share Tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_share_success(
        self,
        socketio_test_client,
        add_one_test_resource,
        add_one_test_group,
        register_one_identity,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful presentation sharing."""
        await super().run_share_success(
            socketio_test_client,
            add_one_test_resource,
            add_one_test_group,
            register_one_identity,
            session_ids,
            access_to_one_parent,
        )
