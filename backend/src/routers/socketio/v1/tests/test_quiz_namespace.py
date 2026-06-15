"""Tests for Quiz SocketIO namespaces (Message, Question, Numerical)."""

from uuid import UUID

import pytest

from models.access import Action
from crud.quiz import MessageCRUD, NumericalCRUD, QuestionCRUD
from models.quiz import Message, Numerical, Question
from tests.utils import (
    session_id_admin_read_write_socketio,
    session_id_user1_read_write_socketio,
    session_id_user2_read_write_socketio
)
from tests.utils_quiz import (
    many_test_messages,
    many_test_numericals,
    many_test_questions,
    message_update_data,
    numerical_update_data,
    one_test_message,
    one_test_numerical,
    one_test_question,
    question_update_data,
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
    async def test_submit_create_public_with_parent_fails(
        self,
        socketio_test_client,
        access_to_one_parent,
    ):
        """Test failing question creation."""
        await super().run_submit_create_fails(
            socketio_test_client,
            access_to_one_parent=access_to_one_parent,
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
        """Test successful question creation."""
        await super().run_submit_create_success(
            socketio_test_client,
            session_ids,
        )

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_fails(
        self,
        socketio_test_client,
    ):
        """Test failing question creation."""
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

    # TBD: move those general functionality tests to protected_resource tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_read_and_get_children(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
        add_one_test_resource,
    ):
        """Test that read returns children of a question."""

        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        await connection.connect(
            query_parameters={
                "request-access-data": True,
            }
        )
        await connection.client.sleep(0.2)
        current_user = await connection.current_user()

        # Create one question
        question = await add_one_test_resource(
            QuestionCRUD,
            one_test_question,
            current_user,
        )

        # Create one message under the question
        messages = []
        for message_data in many_test_messages:
            message = await add_one_test_resource(
                MessageCRUD,
                message_data,
                current_user,
                parent_id=question.id,
            )
            messages.append(message)

        # Read the question
        await connection.client.emit(
            "read",
            str(question.id),
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        # Check transferred events
        transfer_data = connection.responses("transferred", self.namespace_path)

        assert len(transfer_data) == 1
        assert transfer_data[0]["id"] == str(question.id)
        assert (
            "hierarchies" in transfer_data[0]
        ), "Expected inherit flag in transferred data"
        children = transfer_data[0]["hierarchies"]
        assert len(children) == 3, "Expected one child in transferred data"
        for children_data, message, idx in zip(
            children, messages, range(len(messages))
        ):
            assert (
                UUID(children_data["child_id"]) == message.id
            ), "Expected parent_id to match"
            assert (
                "inherit" in children_data
            ), "Expected inherit flag in transferred data"
            assert not children_data[
                "inherit"
            ], "Expected default inherit flag to be False"
            assert (
                children_data["order"] == idx + 1
            ), "Expected default order to match index of creation"

    # TBD: move those general functionality tests to protected_resource tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_link_a_message_to_question(
        self,
        socketio_test_client,
        session_ids,
        access_to_one_parent,
        add_one_test_resource,
    ):
        """Test that read returns children of a question."""

        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        await connection.connect(
            query_parameters={
                "request-access-data": True,
            }
        )
        await connection.client.sleep(0.2)
        current_user = await connection.current_user()

        # Create one question
        question = await add_one_test_resource(
            QuestionCRUD,
            one_test_question,
            current_user,
        )

        # Create one message
        message = one_test_message.copy()
        created_message = await add_one_test_resource(
            MessageCRUD,
            message,
            current_user,
        )

        # Read the question
        await connection.client.emit(
            "link",
            {"parent_id": str(question.id), "child_id": str(created_message.id)},
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        # Check transferred events
        status_data = connection.responses("status", self.namespace_path)

        # It's emitted twice: once in the self.namespace and in the parent namespace,
        # both with the same data, so we can just check one of them and the length.
        assert len(status_data) == 2
        assert status_data[0]["id"] == str(created_message.id)
        assert status_data[0]["parent_id"] == str(question.id)
        assert status_data[0]["inherit"] is False
        assert status_data[0]["order"] == 1
        assert status_data[1]["id"] == str(created_message.id)
        assert status_data[1]["parent_id"] == str(question.id)
        assert status_data[1]["inherit"] is False
        assert status_data[1]["order"] == 1


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

    # TBD: move those general functionality tests to protected_resource tests
    # once implemented for all resource types, and just keep quiz-specific tests here.
    # Read tests:
    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_and_read_returns_read_access_right(
        self,
        socketio_test_client,
    ):
        """Test that an anonymous read of one public message includes read access."""

        connection = await socketio_test_client(client_config=self.client_config())

        await connection.connect(query_parameters={"request-access-data": "true"})
        await connection.client.sleep(0.2)

        await connection.client.emit(
            "submit",
            {
                "payload": {**self._test_data_single},
                "public": True,
            },
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        status_data = connection.responses("status", self.namespace_path)
        created_status = next(
            status for status in status_data if status.get("success") == "created"
        )
        created_id = created_status["id"]

        await connection.client.emit(
            "read",
            created_id,
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        transfer_data = connection.responses("transferred", self.namespace_path)

        assert len(transfer_data) == 1
        assert transfer_data[0]["id"] == created_id
        assert transfer_data[0]["access_right"] == "read"

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_and_write_returns_write_access_right(
        self,
        socketio_test_client,
    ):
        """Test that an anonymous read of one public message includes write access."""

        connection = await socketio_test_client(client_config=self.client_config())

        await connection.connect(query_parameters={"request-access-data": "true"})
        await connection.client.sleep(0.2)

        await connection.client.emit(
            "submit",
            {
                "payload": {**self._test_data_single},
                "public": True,
                "public_action": "write",
            },
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        status_data = connection.responses("status", self.namespace_path)
        created_status = next(
            status for status in status_data if status.get("success") == "created"
        )
        created_id = created_status["id"]

        await connection.client.emit(
            "read",
            created_id,
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        transfer_data = connection.responses("transferred", self.namespace_path)

        assert len(transfer_data) == 1
        assert transfer_data[0]["id"] == created_id
        assert transfer_data[0]["access_right"] == "write"

    @pytest.mark.anyio
    async def test_submit_create_public_without_parent_and_read_returns_connect_access_right(
        self,
        socketio_test_client,
    ):
        """Test that an anonymous read of one public message includes connect access."""

        connection = await socketio_test_client(client_config=self.client_config())

        await connection.connect(query_parameters={"request-access-data": "true"})
        await connection.client.sleep(0.2)

        await connection.client.emit(
            "submit",
            {
                "payload": {**self._test_data_single},
                "public": True,
                "public_action": "connect",
            },
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        status_data = connection.responses("status", self.namespace_path)
        created_status = next(
            status for status in status_data if status.get("success") == "created"
        )
        created_id = created_status["id"]

        await connection.client.emit(
            "read",
            created_id,
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        transfer_data = connection.responses("transferred", self.namespace_path)

        assert len(transfer_data) == 1
        assert transfer_data[0]["id"] == created_id
        assert transfer_data[0]["access_right"] == "connect"

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_submit_with_parent_and_read_returns_default_inherit_flag_false(
        self,
        socketio_test_client,
        access_to_one_parent,
    ):
        """Test that a submitted hierarchy includes the default inherit flag set to False on read with request-access-data."""

        connection = await socketio_test_client(client_config=self.client_config())

        parent_id = await access_to_one_parent(
            self._parent_model, connection.token_payload()
        )

        await connection.connect(
            query_parameters={
                "request-access-data": "true",
                "parent-id": str(parent_id),
            }
        )
        await connection.client.sleep(0.2)

        await connection.client.emit(
            "submit",
            {
                "payload": {**self._test_data_single},
                "parent_id": str(parent_id),
            },
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        status_data = connection.responses("status", self.namespace_path)
        created_status = next(
            status for status in status_data if status.get("success") == "created"
        )
        created_id = created_status["id"]

        await connection.client.emit(
            "read",
            created_id,
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        transfer_data = connection.responses("transferred", self.namespace_path)

        assert len(transfer_data) == 1
        assert transfer_data[0]["id"] == created_id
        assert (
            "hierarchies" in transfer_data[0]
        ), "Expected inherit flag in transferred data"
        assert (
            "hierarchies" in transfer_data[0]
        ), "Expected inherit flag in transferred data"
        parent = transfer_data[0]["hierarchies"][0]
        assert UUID(parent["parent_id"]) == parent_id, "Expected parent_id to match"
        assert "inherit" in parent, "Expected inherit flag in transferred data"
        assert not parent["inherit"], "Expected default inherit flag to be False"
        assert parent["order"] == 1, "Expected default order to be 1"

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_admin_read_write_socketio],
            [session_id_user1_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_submit_with_parent_and_read_returns_inherit_flag_true(
        self,
        socketio_test_client,
        access_to_one_parent,
    ):
        """Test that a submitted hierarchy includes the inherit flag set to True on read with request-access-data."""

        connection = await socketio_test_client(client_config=self.client_config())

        parent_id = await access_to_one_parent(
            self._parent_model, connection.token_payload()
        )

        await connection.connect(
            query_parameters={
                "request-access-data": "true",
                "parent-id": str(parent_id),
            }
        )
        await connection.client.sleep(0.2)

        await connection.client.emit(
            "submit",
            {
                "payload": {**self._test_data_single},
                "parent_id": str(parent_id),
                "inherit": True,
            },
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        status_data = connection.responses("status", self.namespace_path)
        created_status = next(
            status for status in status_data if status.get("success") == "created"
        )
        created_id = created_status["id"]

        await connection.client.emit(
            "read",
            created_id,
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        transfer_data = connection.responses("transferred", self.namespace_path)

        assert len(transfer_data) == 1
        assert transfer_data[0]["id"] == created_id
        assert (
            "hierarchies" in transfer_data[0]
        ), "Expected inherit flag in transferred data"
        assert (
            "hierarchies" in transfer_data[0]
        ), "Expected inherit flag in transferred data"
        parent = transfer_data[0]["hierarchies"][0]
        assert UUID(parent["parent_id"]) == parent_id, "Expected parent_id to match"
        assert "inherit" in parent, "Expected inherit flag in transferred data"
        assert parent["inherit"], "Expected default inherit flag to be False"
        assert parent["order"] == 1, "Expected default order to be 1"

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

    # TBD: move those general functionality tests to protected_resource tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_user1_read_write_socketio, session_id_user2_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_emit_message_to_question_and_other_user_in_message_namespace_and_common_parent_id_room_gets_status_linked(
        self,
        socketio_test_client,
        session_ids,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test that read returns children of a question."""

        connection1 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        connection2 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[1],
        )
        current_user1 = await connection1.current_user()
        current_user2 = await connection2.current_user()

        # Create one question
        question = await add_one_test_resource(
            QuestionCRUD,
            one_test_question,
            current_user1,
        )


        # User 1 shares the question with user 2 with read access.
        await add_one_test_access_policy(
            {
                "resource_id":str(question.id),
                "identity_id":current_user2.user_id,
                "action":Action.read,
            },
            current_user1,
            Question,
        )

        await connection1.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection2.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection1.client.sleep(0.2)

        # Create one message
        message = one_test_message.copy()
        await connection1.client.emit("submit", {"payload": {**message}, "parent_id": str(question.id), "inherit": True}, namespace=self.namespace_path)
        await connection1.client.sleep(0.5)

        # Check transferred events
        status_data1 = connection1.responses("status", self.namespace_path)
        status_data2 = connection2.responses("status", self.namespace_path)


        # It's emitted twice: once in the self.namespace and in the parent namespace,
        # both with the same data, so we can just check one of them and the length.
        assert len(status_data1) == 3
        assert status_data1[0]["success"] == "created"
        created_message_id =  status_data1[0]["id"]
        assert UUID(created_message_id)
        assert status_data1[1]["success"] == "linked"
        assert status_data1[1]["id"] == str(created_message_id)
        assert status_data1[1]["parent_id"] == str(question.id)
        assert status_data1[1]["inherit"]
        assert status_data1[1]["order"] == 1
        assert status_data1[2]["success"] == "shared"
        assert status_data1[2]["id"] == str(created_message_id)

        assert len(status_data2) == 1
        assert status_data2[0]["success"] == "linked"
        assert status_data2[0]["parent_id"] == str(question.id)
        assert status_data2[0]["inherit"]
        assert status_data2[0]["order"] == 1


    # TBD: move those general functionality tests to protected_resource tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_user1_read_write_socketio, session_id_user2_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_emit_message_without_inherit_to_question_and_other_user_in_message_namespace_and_common_parent_id_room_does_not_get_status_linked(
        self,
        socketio_test_client,
        session_ids,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test that read returns children of a question."""

        connection1 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        connection2 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[1],
        )
        current_user1 = await connection1.current_user()
        current_user2 = await connection2.current_user()

        # Create one question
        question = await add_one_test_resource(
            QuestionCRUD,
            one_test_question,
            current_user1,
        )


        # User 1 shares the question with user 2 with read access.
        await add_one_test_access_policy(
            {
                "resource_id":str(question.id),
                "identity_id":current_user2.user_id,
                "action":Action.read,
            },
            current_user1,
            Question,
        )

        await connection1.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection2.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection1.client.sleep(0.2)

        # Create one message
        message = one_test_message.copy()
        await connection1.client.emit("submit", {"payload": {**message}, "parent_id": str(question.id), "inherit": False}, namespace=self.namespace_path)
        await connection1.client.sleep(0.5)

        # Check transferred events
        status_data1 = connection1.responses("status", self.namespace_path)
        status_data2 = connection2.responses("status", self.namespace_path)


        # It's emitted twice: once in the self.namespace and in the parent namespace,
        # both with the same data, so we can just check one of them and the length.
        assert len(status_data1) == 3
        assert status_data1[0]["success"] == "created"
        created_message_id =  status_data1[0]["id"]
        assert UUID(created_message_id)
        assert status_data1[1]["success"] == "linked"
        assert status_data1[1]["id"] == str(created_message_id)
        assert status_data1[1]["parent_id"] == str(question.id)
        assert not status_data1[1]["inherit"]
        assert status_data1[1]["order"] == 1
        assert status_data1[2]["success"] == "shared"
        assert status_data1[2]["id"] == str(created_message_id)

        assert len(status_data2) == 0


    # TBD: move those general functionality tests to protected_resource tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_user1_read_write_socketio, session_id_user2_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_emit_message_to_question_and_other_user_without_access_to_question_in_message_namespace_and_common_parent_id_room_does_not_get_status_linked(
        self,
        socketio_test_client,
        session_ids,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test that read returns children of a question."""

        connection1 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        connection2 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[1],
        )
        current_user1 = await connection1.current_user()
        current_user2 = await connection2.current_user()

        # Create one question
        question = await add_one_test_resource(
            QuestionCRUD,
            one_test_question,
            current_user1,
        )

        await connection1.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection2.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection1.client.sleep(0.2)

        # Create one message
        message = one_test_message.copy()
        await connection1.client.emit("submit", {"payload": {**message}, "parent_id": str(question.id), "inherit": True}, namespace=self.namespace_path)
        await connection1.client.sleep(0.5)

        # Check transferred events
        status_data1 = connection1.responses("status", self.namespace_path)
        status_data2 = connection2.responses("status", self.namespace_path)


        # It's emitted twice: once in the self.namespace and in the parent namespace,
        # both with the same data, so we can just check one of them and the length.
        assert len(status_data1) == 3
        assert status_data1[0]["success"] == "created"
        created_message_id =  status_data1[0]["id"]
        assert UUID(created_message_id)
        assert status_data1[1]["success"] == "linked"
        assert status_data1[1]["id"] == str(created_message_id)
        assert status_data1[1]["parent_id"] == str(question.id)
        assert status_data1[1]["inherit"]
        assert status_data1[1]["order"] == 1
        assert status_data1[2]["success"] == "shared"
        assert status_data1[2]["id"] == str(created_message_id)

        assert len(status_data2) == 0


    # TBD: move those general functionality tests to protected_resource tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids",
        [
            [session_id_user1_read_write_socketio, session_id_user2_read_write_socketio],
        ],
        indirect=True,
    )
    async def test_emit_message_to_question_and_other_user_in_question_namespace_subscribed_to_parent_id_there_gets_status_linked(
        self,
        socketio_test_client,
        session_ids,
        add_one_test_resource,
        add_one_test_access_policy,
    ):
        """Test that read returns children of a question."""

        connection1 = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )
        client_config2 = self.client_config()
        client_config2[0]["namespace"] = "/question"
        connection2 = await socketio_test_client(
            client_config=client_config2,
            session_id=session_ids[1],
        )
        current_user1 = await connection1.current_user()
        current_user2 = await connection2.current_user()

        # Create one question
        question = await add_one_test_resource(
            QuestionCRUD,
            one_test_question,
            current_user1,
        )


        # User 1 shares the question with user 2 with read access.
        await add_one_test_access_policy(
            {
                "resource_id":str(question.id),
                "identity_id":current_user2.user_id,
                "action":Action.read,
            },
            current_user1,
            Question,
        )

        await connection1.connect(
            query_parameters={
                "request-access-data": True,
                "parent-id": str(question.id)
            }
        )
        await connection2.connect(
            query_parameters={
                "request-access-data": True,
                "resource-ids": str(question.id)
            }
        )
        await connection1.client.sleep(0.2)

        # Create one message
        message = one_test_message.copy()
        await connection1.client.emit("submit", {"payload": {**message}, "parent_id": str(question.id), "inherit": True}, namespace=self.namespace_path)
        await connection1.client.sleep(0.5)

        # Check transferred events
        status_data1 = connection1.responses("status", self.namespace_path)
        status_data2 = connection2.responses("status", "/question")


        # It's emitted twice: once in the self.namespace and in the parent namespace,
        # both with the same data, so we can just check one of them and the length.
        assert len(status_data1) == 3
        assert status_data1[0]["success"] == "created"
        created_message_id =  status_data1[0]["id"]
        assert UUID(created_message_id)
        assert status_data1[1]["success"] == "linked"
        assert status_data1[1]["id"] == str(created_message_id)
        assert status_data1[1]["parent_id"] == str(question.id)
        assert status_data1[1]["inherit"]
        assert status_data1[1]["order"] == 1
        assert status_data1[2]["success"] == "shared"
        assert status_data1[2]["id"] == str(created_message_id)

        assert len(status_data2) == 1
        assert status_data2[0]["success"] == "linked"
        assert status_data2[0]["parent_id"] == str(question.id)
        assert status_data2[0]["inherit"]
        assert status_data2[0]["order"] == 1

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
