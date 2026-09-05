from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call
from uuid import uuid4

import pytest

from core.types import Action, ResourceType
from models.demo_resource import DemoResource, DemoResourceExtended, DemoResourceRead
from routers.socketio.v1.base import BaseNamespace
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from routers.socketio.v1.presentation_namespace import PresentationNamespace
from routers.socketio.v1.quiz_namespace import QuestionNamespace


class FakeResult:
    def __init__(self, entity_ids):
        self.entity_ids = entity_ids

    def all(self):
        return self.entity_ids


class FakeCRUD:
    authorized_ids = []
    policy_crud = SimpleNamespace(
        filters_allowed=Mock(side_effect=lambda statement, **_: statement)
    )
    session = SimpleNamespace()
    model = DemoResource

    async def __aenter__(self):
        self.session.exec = AsyncMock(return_value=FakeResult(self.authorized_ids))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


def test_demo_resource_namespace_has_no_connect_time_collection_replay():
    namespace = DemoResourceNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


def test_presentation_namespace_has_no_connect_time_collection_replay():
    namespace = PresentationNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


def test_question_namespace_has_no_connect_time_collection_replay():
    namespace = QuestionNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


@pytest.mark.anyio
async def test_subscribe_enters_only_access_controlled_entity_rooms():
    authorized_id = uuid4()
    rejected_id = uuid4()
    FakeCRUD.authorized_ids = [authorized_id]
    server = SimpleNamespace(
        enter_room=AsyncMock(),
        get_session=AsyncMock(return_value={}),
        save_session=AsyncMock(),
    )
    namespace = BaseNamespace(server=server, namespace="/test")
    namespace.crud = FakeCRUD
    namespace._get_current_user_and_check_guard = AsyncMock(return_value=None)

    result = await namespace.on_subscribe(
        "sid", {"entity_ids": [str(authorized_id), str(rejected_id)]}
    )

    assert result == {
        "subscribed": [str(authorized_id)],
        "rejected": [str(rejected_id)],
    }
    FakeCRUD.policy_crud.filters_allowed.assert_called_once()
    assert (
        FakeCRUD.policy_crud.filters_allowed.call_args.kwargs["action"] == Action.read
    )
    server.enter_room.assert_awaited_once_with(
        "sid", f"resource:{authorized_id}", namespace="/test"
    )


@pytest.mark.anyio
async def test_subscribe_rejects_oversized_batch_before_authorization():
    server = SimpleNamespace(enter_room=AsyncMock())
    namespace = BaseNamespace(server=server, namespace="/test")
    namespace.crud = FakeCRUD
    namespace._get_current_user_and_check_guard = AsyncMock(return_value=None)

    result = await namespace.on_subscribe(
        "sid",
        {"entity_ids": [str(uuid4()) for _ in range(501)]},
    )

    assert result == {"error": "entity_ids exceeds the maximum batch size of 500."}
    namespace._get_current_user_and_check_guard.assert_not_awaited()
    server.enter_room.assert_not_awaited()


@pytest.mark.anyio
async def test_subscribe_replays_cursor_after_accumulating_snapshot_batches():
    first_id = uuid4()
    final_id = uuid4()
    FakeCRUD.authorized_ids = [final_id]
    server = SimpleNamespace(
        enter_room=AsyncMock(),
        get_session=AsyncMock(return_value={"snapshot_entity_ids": [str(first_id)]}),
        save_session=AsyncMock(),
    )
    namespace = BaseNamespace(server=server, namespace="/test")
    namespace.crud = FakeCRUD
    namespace._get_current_user_and_check_guard = AsyncMock(return_value=None)
    namespace._replay_entity_mutations = AsyncMock()

    result = await namespace.on_subscribe(
        "sid",
        {"entity_ids": [str(final_id)], "cursor": 42},
    )

    assert result == {"subscribed": [str(final_id)], "rejected": []}
    namespace._replay_entity_mutations.assert_awaited_once_with(
        sid="sid",
        current_user=None,
        cursor=42,
        snapshot_entity_ids={str(first_id), str(final_id)},
    )


@pytest.mark.anyio
async def test_replay_emits_extended_upserts_and_snapshot_deletes():
    updated_id = uuid4()
    deleted_id = uuid4()
    created_at = datetime(2026, 9, 5, 12, 0)
    logging_crud = SimpleNamespace(
        read_entity_mutations_after=AsyncMock(
            return_value=[
                {"cursor": 11, "entity_id": updated_id, "kind": "updated"},
                {"cursor": 12, "entity_id": deleted_id, "kind": "deleted"},
            ]
        ),
        read_entity_metadata=AsyncMock(
            return_value={
                updated_id: {
                    "creation_date": created_at,
                    "last_modified_date": created_at,
                }
            }
        ),
    )
    policy_crud = SimpleNamespace(
        read_access_rights=AsyncMock(return_value={updated_id: Action.write})
    )
    crud = SimpleNamespace(
        entity_type=ResourceType.demo_resource,
        logging_crud=logging_crud,
        policy_crud=policy_crud,
        model=DemoResource,
        read=AsyncMock(return_value=[DemoResourceRead(id=updated_id, name="updated")]),
    )

    class CRUDContext:
        async def __aenter__(self):
            return crud

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    server = SimpleNamespace(enter_room=AsyncMock(), emit=AsyncMock())
    namespace = BaseNamespace(
        server=server,
        namespace="/test",
        read_extended_model=DemoResourceExtended,
    )
    namespace.crud = CRUDContext

    await namespace._replay_entity_mutations(
        sid="sid",
        current_user=None,
        cursor=10,
        snapshot_entity_ids={str(updated_id), str(deleted_id)},
    )

    server.enter_room.assert_awaited_once_with(
        "sid", f"resource:{updated_id}", namespace="/test"
    )
    transferred_call, deleted_call = server.emit.await_args_list
    assert transferred_call.args[0] == "transferred"
    assert transferred_call.args[1]["id"] == str(updated_id)
    assert transferred_call.args[1]["access_right"] == "write"
    assert transferred_call.args[1]["creation_date"] == created_at.isoformat()
    assert transferred_call.kwargs == {"namespace": "/test", "to": "sid"}
    assert deleted_call == call("deleted", str(deleted_id), namespace="/test", to="sid")
