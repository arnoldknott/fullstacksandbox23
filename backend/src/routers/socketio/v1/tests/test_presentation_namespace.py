"""Tests for Presentation SocketIO namespace."""

import pytest

from crud.presentation import PresentationCRUD
from models.presentation import Presentation
from tests.utils import (
    session_id_admin_read_write_socketio,
    session_id_linkedin_socketio,
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

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids", [[session_id_linkedin_socketio]], indirect=True
    )
    async def test_linkedin_connects_but_cannot_create_presentation(
        self, socketio_test_client, session_ids
    ):
        """LinkedIn can join the read channel but writes stay Microsoft-only."""
        connection = await socketio_test_client(
            client_config=self.client_config(), session_id=session_ids[0]
        )
        await connection.connect()
        await connection.client.emit(
            "submit",
            {"payload": {**self._test_data_single}},
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        assert {
            "error": "access",
            "code": "authorization-failed",
        } in connection.responses("status", self.namespace_path)
        await connection.client.disconnect()

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

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "session_ids", [[session_id_user1_read_write_socketio]], indirect=True
    )
    @pytest.mark.parametrize("public", [False, True])
    async def test_share_changes_notify_another_snapshot_subscriber(
        self,
        socketio_test_client,
        add_one_test_resource,
        add_one_test_group,
        register_one_identity,
        session_ids,
        public,
    ):
        """Another page receives policy changes and can read the updated policies."""
        from models.identity import Group

        sender = await socketio_test_client(
            client_config=self.client_config(), session_id=session_ids[0]
        )
        observer = await socketio_test_client(
            client_config=self.client_config(), session_id=session_ids[0]
        )
        unsubscribed = await socketio_test_client(
            client_config=self.client_config(), session_id=session_ids[0]
        )
        current_user = await sender.current_user()
        resource = await add_one_test_resource(
            self.crud, self._test_data_single, current_user
        )
        group = await add_one_test_group(
            {"name": "Share notification group", "description": "Test"}, current_user
        )
        await register_one_identity(group.id, Group)
        resource_id = str(resource.id)
        identity_id = str(group.id)
        query = {"data-on-connect": "false", "request-access-data": "true"}
        await sender.connect(query_parameters=query)
        await observer.connect(query_parameters=query)
        await unsubscribed.connect(query_parameters=query)
        result = await observer.client.call(
            "subscribe", {"entity_ids": [resource_id]}, namespace=self.namespace_path
        )
        assert result == {"subscribed": [resource_id], "rejected": []}

        for change, success, expected_action in [
            ({"action": "read"}, "shared", "read"),
            ({"action": "read", "new_action": "write"}, "shared", "write"),
            ({}, "unshared", None),
        ]:
            observer.responses("status", self.namespace_path).clear()
            observer.responses("transferred", self.namespace_path).clear()
            await sender.client.emit(
                "share",
                {
                    "resource_id": resource_id,
                    **({"identity_id": identity_id} if not public else {}),
                    "public": public,
                    **change,
                },
                namespace=self.namespace_path,
            )
            await observer.client.sleep(0.5)
            assert {"success": success, "id": resource_id} in observer.responses(
                "status", self.namespace_path
            )
            if not public:
                assert unsubscribed.responses("status", self.namespace_path) == []
            await observer.client.emit(
                "read", resource_id, namespace=self.namespace_path
            )
            await observer.client.sleep(0.5)
            transferred = observer.responses("transferred", self.namespace_path)
            assert transferred
            policies = [
                policy
                for policy in transferred[-1]["access_policies"]
                if policy.get("public") == public
                and (public or policy.get("identity_id") == identity_id)
            ]
            if expected_action is None:
                assert policies == []
            else:
                assert any(policy["action"] == expected_action for policy in policies)

        await sender.client.disconnect()
        await observer.client.disconnect()
        await unsubscribed.client.disconnect()
