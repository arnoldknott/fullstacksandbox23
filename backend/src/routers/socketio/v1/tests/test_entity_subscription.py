from datetime import datetime
from types import SimpleNamespace
from typing import Any, cast
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


@pytest.mark.anyio
async def test_demo_resource_namespace_has_no_connect_time_collection_replay():
    namespace = DemoResourceNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


@pytest.mark.anyio
async def test_presentation_namespace_has_no_connect_time_collection_replay():
    namespace = PresentationNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


@pytest.mark.anyio
async def test_question_namespace_has_no_connect_time_collection_replay():
    namespace = QuestionNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


@pytest.mark.anyio
async def test_subscribe_enters_only_access_controlled_entity_rooms():
    authorized_id = uuid4()
    rejected_id = uuid4()
    FakeCRUD.authorized_ids = [authorized_id]
    server: Any = SimpleNamespace(
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
    server: Any = SimpleNamespace(enter_room=AsyncMock())
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
    server: Any = SimpleNamespace(
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
@pytest.mark.parametrize("parent_scoped", [False, True])
async def test_replay_emits_extended_upserts_and_snapshot_deletes(parent_scoped):
    updated_id = uuid4()
    deleted_id = uuid4()
    unrelated_id = uuid4()
    parent_id = uuid4()
    created_at = datetime(2026, 9, 5, 12, 0)
    logging_crud = SimpleNamespace(
        read_entity_mutations_after=AsyncMock(
            return_value=[
                {"cursor": 11, "entity_id": updated_id, "kind": "updated"},
                {"cursor": 12, "entity_id": deleted_id, "kind": "deleted"},
                {"cursor": 13, "entity_id": unrelated_id, "kind": "created"},
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
    hierarchy_crud = SimpleNamespace(
        read=AsyncMock(return_value=[SimpleNamespace(child_id=updated_id)])
    )

    async def read_entities(*, current_user, filters):
        entities = [
            DemoResourceRead(id=updated_id, name="updated"),
            DemoResourceRead(id=unrelated_id, name="another question's answer"),
        ]
        return [
            entity
            for entity in entities
            if all(entity.id in criterion.right.value for criterion in filters)
        ]

    crud = SimpleNamespace(
        entity_type=ResourceType.demo_resource,
        logging_crud=logging_crud,
        policy_crud=policy_crud,
        hierarchy_CRUD=Mock(return_value=hierarchy_crud),
        session=SimpleNamespace(),
        model=DemoResource,
        read=AsyncMock(side_effect=read_entities),
    )

    class CRUDContext:
        async def __aenter__(self):
            return crud

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    server: Any = SimpleNamespace(
        enter_room=AsyncMock(),
        emit=AsyncMock(),
        get_session=AsyncMock(
            return_value={
                "query_strings": {"parent_id": str(parent_id)} if parent_scoped else {}
            }
        ),
    )
    namespace = BaseNamespace(
        server=server,
        namespace="/test",
        read_extended_model=cast(Any, DemoResourceExtended),
    )
    namespace.crud = CRUDContext

    await namespace._replay_entity_mutations(
        sid="sid",
        current_user=None,
        cursor=10,
        snapshot_entity_ids={str(updated_id), str(deleted_id)},
    )

    expected_rooms = [call("sid", f"resource:{updated_id}", namespace="/test")]
    if parent_scoped:
        hierarchy_crud.read.assert_awaited_once_with(
            current_user=None, parent_id=parent_id
        )
    else:
        hierarchy_crud.read.assert_not_awaited()
        expected_rooms.append(
            call("sid", f"resource:{unrelated_id}", namespace="/test")
        )
    assert server.enter_room.await_args_list == expected_rooms
    transferred_call, deleted_call, *remaining_calls = server.emit.await_args_list
    assert transferred_call.args[0] == "transferred"
    assert transferred_call.args[1]["id"] == str(updated_id)
    assert transferred_call.args[1]["access_right"] == "write"
    assert transferred_call.args[1]["creation_date"] == created_at.isoformat()
    assert transferred_call.kwargs == {"namespace": "/test", "to": "sid"}
    assert deleted_call == call("deleted", str(deleted_id), namespace="/test", to="sid")
    if parent_scoped:
        assert remaining_calls == []
    else:
        assert remaining_calls[0].args[0] == "transferred"
        assert remaining_calls[0].args[1]["id"] == str(unrelated_id)
