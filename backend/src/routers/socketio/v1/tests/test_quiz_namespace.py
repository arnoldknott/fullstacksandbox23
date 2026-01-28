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


class TestQuestion(BaseSocketIOTest):
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
    async def test_submit_create_with_parent_success(
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

    @pytest.mark.anyio
    async def test_submit_create_public_with_parent_success(
        self,
        socketio_test_client,
        access_to_one_parent,
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            access_to_one_parent=access_to_one_parent,
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
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
        )

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_success(
        self,
        socketio_test_client,
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
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


class TestMessage(BaseSocketIOTest):
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
    async def test_submit_create_with_parent_success(
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

    @pytest.mark.anyio
    async def test_submit_create_public_with_parent_success(
        self,
        socketio_test_client,
        access_to_one_parent,
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            access_to_one_parent=access_to_one_parent,
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
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
        )

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_success(
        self,
        socketio_test_client,
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
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

    # Connection with parent_id filter test
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_connect_with_parent_id_filter(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
        add_one_test_resource,
    ):
        """Test that connecting with parent-id only returns children of that parent."""

        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        current_user = await connection.current_user()

        # Create two parent questions
        parent1_id = await access_to_one_parent(Question, connection.token_payload())
        parent2_id = await access_to_one_parent(Question, connection.token_payload())

        # Create one message under parent1
        message1 = await add_one_test_resource(
            MessageCRUD,
            one_test_message,
            current_user,
            parent_id=parent1_id,
        )

        # Create one message under parent2
        message2_data = {**one_test_message, "content": "Message for parent 2"}
        message2 = await add_one_test_resource(
            MessageCRUD,
            message2_data,
            current_user,
            parent_id=parent2_id,
        )

        # Connect with parent_id filter for parent1
        query_params = {"parent-id": str(parent1_id)}
        await connection.connect(query_parameters=query_params)
        await connection.client.sleep(0.3)

        # Check transferred events
        transferred_data = connection.responses("transferred", self.namespace_path)

        # Should only receive message1, not message2
        assert (
            len(transferred_data) == 1
        ), f"Expected 1 message for parent1, got {len(transferred_data)}"

        # Verify it's message1
        assert transferred_data[0]["id"] == str(message1.id)
        assert transferred_data[0]["content"] == one_test_message["content"]

        # Verify message2 was NOT received
        received_ids = [msg["id"] for msg in transferred_data]
        assert (
            str(message2.id) not in received_ids
        ), "Message2 should not be received when filtering for parent1"

        await connection.client.disconnect()


class TestNumerical(BaseSocketIOTest):
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
    async def test_submit_create_with_parent_success(
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

    @pytest.mark.anyio
    async def test_submit_create_public_with_parent_success(
        self,
        socketio_test_client,
        access_to_one_parent,
    ):
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            access_to_one_parent=access_to_one_parent,
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
    async def test_submit_create_without_parent_fails(
        self,
        socketio_test_client,
    ):
        """Test successful question creation."""
        await super().run_submit_create_fails(
            socketio_test_client,
        )

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_fails(
        self,
        socketio_test_client,
    ):
        """Test successful question creation."""
        await super().run_submit_create_fails(
            socketio_test_client,
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
