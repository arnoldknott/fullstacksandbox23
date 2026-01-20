"""Tests for Quiz, Question, Message and Numerical API endpoints."""

import pytest

from crud.quiz import QuestionCRUD, MessageCRUD, NumericalCRUD
from models.quiz import Question, Message, Numerical
from tests.utils import (
    token_admin_read_write,
    token_user1_read_write,
    token_admin_read,
    token_admin_write,
    token_user1_read,
    token_user1_write,
    token_admin,
)
from tests.utils_quiz import (
    one_test_question,
    many_test_questions,
    wrong_test_questions,
    question_update_data,
    one_test_message,
    many_test_messages,
    wrong_test_messages,
    message_update_data,
    one_test_numerical,
    many_test_numericals,
    wrong_test_numericals,
    numerical_update_data,
)
from routers.api.v1.tests.base import BaseTest


class TestQuestionEndpoints(BaseTest):
    """Test suite for Question CRUD endpoints."""

    crud = QuestionCRUD
    model = Question
    router_path = "/api/v1/quiz/question/"
    _test_data_single = one_test_question
    _test_data_wrong = wrong_test_questions
    _test_data_many = many_test_questions
    _test_data_update = question_update_data

    # POST tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read_write, token_user1_read_write],
        indirect=True,
    )
    async def test_post_success(
        self, test_data_single, mocked_provide_http_token_payload
    ):
        """Test POST question success."""
        await super().run_post_success(
            test_data_single, mocked_provide_http_token_payload
        )

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
        """Test POST question fails without proper authorization."""
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
        """Test POST question with invalid data fails."""
        await super().run_post_invalid_data(
            test_data_wrong, mocked_provide_http_token_payload
        )

    # GET tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read, token_user1_read],
        indirect=True,
    )
    async def test_get_all_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all questions success."""
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
        """Test GET question by ID success."""
        await super().run_get_by_id_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_not_found(self, mocked_provide_http_token_payload):
        """Test GET by ID returns 404 for non-existent question."""
        await super().run_get_by_id_not_found(mocked_provide_http_token_payload)

    @pytest.mark.anyio
    async def test_get_by_id_missing_auth(self, added_resources):
        """Test GET by ID fails without authentication."""
        await super().run_get_by_id_missing_auth(added_resources)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_admin_write, token_user1_write],
        indirect=True,
    )
    async def test_get_by_id_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET question by ID fails without proper authorization."""
        await super().run_get_by_id_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    async def test_get_public_by_id_success(
        self, add_one_test_access_policy, added_resources
    ):
        """Test public GET question by ID success (no auth)."""
        await super().run_get_public_by_id_success(
            add_one_test_access_policy, added_resources
        )

    # PUT tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_success(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT question success."""
        await super().run_put_success(
            added_resources, update_data, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_not_found(self, update_data, mocked_provide_http_token_payload):
        """Test PUT returns 404 for non-existent question."""
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
        """Test PUT question fails without proper authorization."""
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
        """Test PUT question with invalid data fails."""
        await super().run_put_fails_invalid_data(
            added_resources, test_data_wrong, mocked_provide_http_token_payload
        )

    # DELETE tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE question success."""
        await super().run_delete_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_not_found(self, mocked_provide_http_token_payload):
        """Test DELETE returns 404 for non-existent question."""
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
        """Test DELETE question fails without proper authorization."""
        await super().run_delete_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )


# ============================================================================
# Message (Answer) Tests
# ============================================================================


class TestMessageEndpoints(BaseTest):
    """Test suite for Message CRUD endpoints."""

    crud = MessageCRUD
    model = Message
    router_path = "/api/v1/quiz/message/"
    _test_data_single = one_test_message
    _test_data_wrong = wrong_test_messages
    _test_data_many = many_test_messages
    _test_data_update = message_update_data

    # Hierarchical routing (Message requires parent Question)
    _hierarchical_router_path = "/api/v1/quiz/question/{parent_id}/message/"
    _parent_model = Question

    # POST tests
    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload",
    #     [token_admin_read_write, token_user1_read_write],
    #     indirect=True,
    # )
    # async def test_post_success(
    #     self, test_data_single, mocked_provide_http_token_payload
    # ):
    #     """Test POST message success."""
    #     await super().run_post_success(
    #         test_data_single, mocked_provide_http_token_payload
    #     )

    # @pytest.mark.anyio
    # async def test_post_missing_auth(self, test_data_single):
    #     """Test POST fails without authentication."""
    #     await super().run_post_missing_auth(test_data_single)

    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload",
    #     [token_admin_read, token_admin_write, token_user1_read, token_user1_write],
    #     indirect=True,
    # )
    # async def test_post_fails_authorization(
    #     self, test_data_single, mocked_provide_http_token_payload
    # ):
    #     """Test POST message fails without proper authorization."""
    #     await super().run_post_fails_authorization(
    #         test_data_single, mocked_provide_http_token_payload
    #     )

    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    # )
    # async def test_post_invalid_data(
    #     self, test_data_wrong, mocked_provide_http_token_payload
    # ):
    #     """Test POST message with invalid data fails."""
    #     await super().run_post_invalid_data(
    #         test_data_wrong, mocked_provide_http_token_payload
    #     )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read_write, token_user1_read_write],
        indirect=True,
    )
    async def test_post_with_parent_success(
        self, test_data_single, access_to_one_parent, mocked_provide_http_token_payload
    ):
        """Test POST message with parent question success."""
        await super().run_post_with_parent_success(
            test_data_single, access_to_one_parent, mocked_provide_http_token_payload
        )

    # GET tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read, token_user1_read],
        indirect=True,
    )
    async def test_get_all_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all messages success."""
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
        """Test GET message by ID success."""
        await super().run_get_by_id_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_not_found(self, mocked_provide_http_token_payload):
        """Test GET by ID returns 404 for non-existent message."""
        await super().run_get_by_id_not_found(mocked_provide_http_token_payload)

    @pytest.mark.anyio
    async def test_get_by_id_missing_auth(self, added_resources):
        """Test GET by ID fails without authentication."""
        await super().run_get_by_id_missing_auth(added_resources)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_admin_write, token_user1_write],
        indirect=True,
    )
    async def test_get_by_id_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET message by ID fails without proper authorization."""
        await super().run_get_by_id_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    async def test_get_public_by_id_success(
        self, add_one_test_access_policy, added_resources
    ):
        """Test public GET message by ID success (no auth)."""
        await super().run_get_public_by_id_success(
            add_one_test_access_policy, added_resources
        )

    # PUT tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_success(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT message success."""
        await super().run_put_success(
            added_resources, update_data, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_not_found(self, update_data, mocked_provide_http_token_payload):
        """Test PUT returns 404 for non-existent message."""
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
        """Test PUT message fails without proper authorization."""
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
        """Test PUT message with invalid data fails."""
        await super().run_put_fails_invalid_data(
            added_resources, test_data_wrong, mocked_provide_http_token_payload
        )

    # DELETE tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE message success."""
        await super().run_delete_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_not_found(self, mocked_provide_http_token_payload):
        """Test DELETE returns 404 for non-existent message."""
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
        """Test DELETE message fails without proper authorization."""
        await super().run_delete_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )


# ============================================================================
# Numerical (Answer) Tests
# ============================================================================


class TestNumericalEndpoints(BaseTest):
    """Test suite for Numerical CRUD endpoints."""

    crud = NumericalCRUD
    model = Numerical
    router_path = "/api/v1/quiz/numerical/"
    _test_data_single = one_test_numerical
    _test_data_wrong = wrong_test_numericals
    _test_data_many = many_test_numericals
    _test_data_update = numerical_update_data

    # Hierarchical routing (Numerical requires parent Question)
    _hierarchical_router_path = "/api/v1/quiz/question/{parent_id}/numerical/"
    _parent_model = Question

    # POST tests
    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload",
    #     [token_admin_read_write, token_user1_read_write],
    #     indirect=True,
    # )
    # async def test_post_success(
    #     self, test_data_single, mocked_provide_http_token_payload
    # ):
    #     """Test POST numerical success."""
    #     await super().run_post_success(
    #         test_data_single, mocked_provide_http_token_payload
    #     )

    # @pytest.mark.anyio
    # async def test_post_missing_auth(self, test_data_single):
    #     """Test POST fails without authentication."""
    #     await super().run_post_missing_auth(test_data_single)

    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload",
    #     [token_admin_read, token_admin_write, token_user1_read, token_user1_write],
    #     indirect=True,
    # )
    # async def test_post_fails_authorization(
    #     self, test_data_single, mocked_provide_http_token_payload
    # ):
    #     """Test POST numerical fails without proper authorization."""
    #     await super().run_post_fails_authorization(
    #         test_data_single, mocked_provide_http_token_payload
    #     )
    # @pytest.mark.anyio
    # @pytest.mark.parametrize(
    #     "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    # )
    # async def test_post_invalid_data(
    #     self, test_data_wrong, mocked_provide_http_token_payload
    # ):
    #     """Test POST numerical with invalid data fails."""
    #     await super().run_post_invalid_data(
    #         test_data_wrong, mocked_provide_http_token_payload
    #     )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read_write, token_user1_read_write],
        indirect=True,
    )
    async def test_post_with_parent_success(
        self, test_data_single, access_to_one_parent, mocked_provide_http_token_payload
    ):
        """Test POST numerical with parent question success."""
        await super().run_post_with_parent_success(
            test_data_single, access_to_one_parent, mocked_provide_http_token_payload
        )

    # GET tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin_read, token_user1_read],
        indirect=True,
    )
    async def test_get_all_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all numericals success."""
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
        """Test GET numerical by ID success."""
        await super().run_get_by_id_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_get_by_id_not_found(self, mocked_provide_http_token_payload):
        """Test GET by ID returns 404 for non-existent numerical."""
        await super().run_get_by_id_not_found(mocked_provide_http_token_payload)

    @pytest.mark.anyio
    async def test_get_by_id_missing_auth(self, added_resources):
        """Test GET by ID fails without authentication."""
        await super().run_get_by_id_missing_auth(added_resources)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload",
        [token_admin, token_admin_write, token_user1_write],
        indirect=True,
    )
    async def test_get_by_id_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET numerical by ID fails without proper authorization."""
        await super().run_get_by_id_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    async def test_get_public_by_id_success(
        self, add_one_test_access_policy, added_resources
    ):
        """Test public GET numerical by ID success (no auth)."""
        await super().run_get_public_by_id_success(
            add_one_test_access_policy, added_resources
        )

    # PUT tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_success(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT numerical success."""
        await super().run_put_success(
            added_resources, update_data, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_put_not_found(self, update_data, mocked_provide_http_token_payload):
        """Test PUT returns 404 for non-existent numerical."""
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
        """Test PUT numerical fails without proper authorization."""
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
        """Test PUT numerical with invalid data fails."""
        await super().run_put_fails_invalid_data(
            added_resources, test_data_wrong, mocked_provide_http_token_payload
        )

    # DELETE tests
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE numerical success."""
        await super().run_delete_success(
            added_resources, mocked_provide_http_token_payload
        )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
    )
    async def test_delete_not_found(self, mocked_provide_http_token_payload):
        """Test DELETE returns 404 for non-existent numerical."""
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
        """Test DELETE numerical fails without proper authorization."""
        await super().run_delete_fails_authorization(
            added_resources, mocked_provide_http_token_payload
        )


# ============================================================================
# COMMENTED OUT: Parent-Child Relationship Tests
# ============================================================================
# TODO: Implement these once basic CRUD tests pass
# These will be moved to BaseTest to make them reusable
#
# ============================================================================
# 1. Tests for POST with parent_id (Message and Numerical)
# ============================================================================
#
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write],
#     indirect=True,
# )
# async def test_post_with_parent_id_success(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     add_one_test_resource,
#     mocked_provide_http_token_payload,
# ):
#     """Test successful POST of a message/numerical with parent question."""
#     app_override_provide_http_token_payload
#
#     # Create a parent question first
#     parent_question = await add_one_test_resource(
#         QuestionCRUD, one_test_question, mocked_provide_http_token_payload
#     )
#
#     # Create child with parent_id
#     child_data = {**self._test_data_single, "questions": [str(parent_question.id)]}
#     response = await async_client.post(self.router_path, json=child_data)
#
#     assert response.status_code == 201
#     content = response.json()
#     # Verify the relationship was created
#     assert len(content["questions"]) == 1
#     assert content["questions"][0]["id"] == str(parent_question.id)
#
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write],
#     indirect=True,
# )
# async def test_post_without_parent_id_fails(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     mocked_provide_http_token_payload,
# ):
#     """Test POST without parent_id fails (for resources requiring parent)."""
#     app_override_provide_http_token_payload
#
#     # Try to create child without parent_id
#     response = await async_client.post(self.router_path, json=self._test_data_single)
#
#     # Should fail because resource is not allow_standalone
#     assert response.status_code == 403
#     content = response.json()
#     assert "Forbidden" in content["detail"]
#
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write],
#     indirect=True,
# )
# async def test_post_with_nonexistent_parent_id_fails(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     mocked_provide_http_token_payload,
# ):
#     """Test POST with non-existent parent_id fails."""
#     app_override_provide_http_token_payload
#
#     # Create child with non-existent parent_id
#     fake_parent_id = str(uuid.uuid4())
#     child_data = {**self._test_data_single, "questions": [fake_parent_id]}
#     response = await async_client.post(self.router_path, json=child_data)
#
#     # Should fail because parent doesn't exist
#     assert response.status_code == 403
#     content = response.json()
#     assert "Forbidden" in content["detail"]
#
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write],
#     indirect=True,
# )
# async def test_post_with_multiple_parents_success(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     add_many_test_resources,
#     mocked_provide_http_token_payload,
# ):
#     """Test POST child linked to multiple parents."""
#     app_override_provide_http_token_payload
#
#     # Create multiple parent questions
#     parent_questions = await add_many_test_resources(
#         QuestionCRUD,
#         many_test_questions[:2],
#         mocked_provide_http_token_payload,
#     )
#
#     # Create child linked to both parents
#     child_data = {
#         **self._test_data_single,
#         "questions": [str(q.id) for q in parent_questions],
#     }
#     response = await async_client.post(self.router_path, json=child_data)
#
#     assert response.status_code == 201
#     content = response.json()
#     assert len(content["questions"]) == 2
#     question_ids = [q["id"] for q in content["questions"]]
#     assert str(parent_questions[0].id) in question_ids
#     assert str(parent_questions[1].id) in question_ids
#
# ============================================================================
# 2. Tests for GET parent with children (Question with Message/Numerical)
# ============================================================================
#
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write],
#     indirect=True,
# )
# async def test_get_parent_with_children(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     add_one_test_resource,
#     mocked_provide_http_token_payload,
# ):
#     """Test GET parent by ID includes children."""
#     app_override_provide_http_token_payload
#
#     # Create a parent (e.g., question)
#     parent = await add_one_test_resource(
#         QuestionCRUD, one_test_question, mocked_provide_http_token_payload
#     )
#
#     # Create multiple children for this parent
#     for child_data in many_test_messages[:2]:  # or many_test_numericals
#         child_with_parent = {**child_data, "questions": [str(parent.id)]}
#         await async_client.post("/api/v1/quiz/message/", json=child_with_parent)
#
#     # GET the parent and verify children are included
#     response = await async_client.get(f"/api/v1/quiz/question/{parent.id}")
#
#     assert response.status_code == 200
#     content = response.json()
#     assert content["id"] == str(parent.id)
#     assert "messages" in content  # or "numericals"
#     assert len(content["messages"]) == 2
#
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload",
#     [token_admin_read_write],
#     indirect=True,
# )
# async def test_get_parent_with_multiple_child_types(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     add_one_test_resource,
#     mocked_provide_http_token_payload,
# ):
#     """Test GET parent includes both child types (Message + Numerical)."""
#     app_override_provide_http_token_payload
#
#     # Create a question
#     question = await add_one_test_resource(
#         QuestionCRUD, one_test_question, mocked_provide_http_token_payload
#     )
#
#     # Create a message child
#     message_with_parent = {**one_test_message, "questions": [str(question.id)]}
#     await async_client.post("/api/v1/quiz/message/", json=message_with_parent)
#
#     # Create a numerical child
#     numerical_with_parent = {**one_test_numerical, "questions": [str(question.id)]}
#     await async_client.post("/api/v1/quiz/numerical/", json=numerical_with_parent)
#
#     # GET the question and verify both children are included
#     response = await async_client.get(f"/api/v1/quiz/question/{question.id}")
#
#     assert response.status_code == 200
#     content = response.json()
#     assert "messages" in content
#     assert "numericals" in content
#     assert len(content["messages"]) == 1
#     assert len(content["numericals"]) == 1
#
# @pytest.mark.anyio
# async def test_get_public_parent_with_children(
#     self,
#     async_client,
#     app_override_provide_http_token_payload,
#     add_one_test_resource,
#     add_test_policy_for_resource,
# ):
#     """Test GET public parent includes children without authentication."""
#     app_override_provide_http_token_payload
#
#     # Create a public parent
#     parent = await add_one_test_resource(
#         QuestionCRUD, one_test_question, token_admin_read_write
#     )
#
#     # Make it public
#     policy = {
#         "resource_id": parent.id,
#         "action": "read",
#         "public": True,
#     }
#     await add_test_policy_for_resource(policy)
#
#     # Create a child for this parent
#     child_with_parent = {**one_test_message, "questions": [str(parent.id)]}
#     await async_client.post("/api/v1/quiz/message/", json=child_with_parent)
#
#     # GET the public parent endpoint
#     response = await async_client.get(f"/api/v1/quiz/question/public/{parent.id}")
#
#     assert response.status_code == 200
#     content = response.json()
#     assert "messages" in content
#     assert len(content["messages"]) == 1
#
# ============================================================================
# How to make these generic in BaseTest:
# ============================================================================
#
# In BaseTest, add class attributes:
#   - _parent_crud: Optional[Type[BaseCRUD]] = None
#   - _parent_test_data: Optional[dict] = None
#   - _parent_relationship_field: Optional[str] = None  # e.g., "questions"
#   - _child_relationship_field: Optional[str] = None  # e.g., "messages" or "numericals"
#
# Then test classes would set:
#   class TestMessageEndpoints(BaseTest):
#       _parent_crud = QuestionCRUD
#       _parent_test_data = one_test_question
#       _parent_relationship_field = "questions"
#
#   class TestQuestionEndpoints(BaseTest):
#       _child_cruds = [MessageCRUD, NumericalCRUD]
#       _child_test_data = [one_test_message, one_test_numerical]
#       _child_relationship_fields = ["messages", "numericals"]
#
# BaseTest would check these attributes and skip parent/child tests if None.
# ============================================================================
