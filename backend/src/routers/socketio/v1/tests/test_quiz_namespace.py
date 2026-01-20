"""Tests for Quiz SocketIO namespaces (Message, Question, Numerical)."""

import pytest

from crud.quiz import MessageCRUD, QuestionCRUD, NumericalCRUD
from models.quiz import Message, Question, Numerical
from tests.utils import (
    session_id_admin_read_write_socketio,
    session_id_user1_read_write_socketio,
)
from tests.utils_quiz import (
    one_test_message,
    many_test_messages,
    message_update_data,
    one_test_question,
    many_test_questions,
    question_update_data,
    one_test_numerical,
    many_test_numericals,
    numerical_update_data,
)
from .base import BaseSocketIOTest


class TestQuestionNamespace(BaseSocketIOTest):
    """Test suite for Question SocketIO namespace."""

    namespace_path = "/question"
    crud = QuestionCRUD
    model = Question
    _test_data_single = one_test_question
    _test_data_many = many_test_questions
    _test_data_update = question_update_data
    _parent_model = None  # Question is standalone

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
    async def test_submit_create_success(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            session_ids,
            access_to_one_parent,
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
        """Test successful question update."""
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
        """Test successful question deletion."""
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
        """Test successful question sharing."""
        await super().run_share_success(
            socketio_test_client,
            add_one_test_resource,
            add_one_test_group,
            register_one_identity,
            session_ids,
            access_to_one_parent,
        )


class TestMessageNamespace(BaseSocketIOTest):
    """Test suite for Message SocketIO namespace."""

    namespace_path = "/message"
    crud = MessageCRUD
    model = Message
    _test_data_single = one_test_message
    _test_data_many = many_test_messages
    _test_data_update = message_update_data
    _parent_model = Question

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
    async def test_submit_create_success(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful message creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            session_ids,
            access_to_one_parent,
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
        """Test successful message update."""
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
        """Test successful message deletion."""
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
        """Test successful message sharing."""
        await super().run_share_success(
            socketio_test_client,
            add_one_test_resource,
            add_one_test_group,
            register_one_identity,
            session_ids,
            access_to_one_parent,
        )


class TestNumericalNamespace(BaseSocketIOTest):
    """Test suite for Numerical SocketIO namespace."""

    namespace_path = "/numerical"
    crud = NumericalCRUD
    model = Numerical
    _test_data_single = one_test_numerical
    _test_data_many = many_test_numericals
    _test_data_update = numerical_update_data
    _parent_model = Question

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
    async def test_submit_create_success(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
    ):
        """Test successful numerical creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            session_ids,
            access_to_one_parent,
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
        """Test successful numerical update."""
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
        """Test successful numerical deletion."""
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
        """Test successful numerical sharing."""
        await super().run_share_success(
            socketio_test_client,
            add_one_test_resource,
            add_one_test_group,
            register_one_identity,
            session_ids,
            access_to_one_parent,
        )
