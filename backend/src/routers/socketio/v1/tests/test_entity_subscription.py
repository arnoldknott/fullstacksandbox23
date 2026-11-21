from datetime import datetime
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, Mock, call
from uuid import uuid4

import pytest

from core.types import Action, IdentityType, ResourceType
from models.access import IdentityHierarchy, ResourceHierarchy
from models.demo_resource import DemoResource, DemoResourceExtended, DemoResourceRead
from models.identity import Group
from routers.socketio.v1.base import BaseNamespace
from routers.socketio.v1.demo_resource import DemoResourceNamespace
from routers.socketio.v1.data import NumberNamespace, TextNamespace
from crud.data import NumberCRUD, TextCRUD
from models.data import Number, Text
from routers.socketio.v1.identities import GroupNamespace
from routers.socketio.v1.presentation_namespace import PresentationNamespace
from routers.socketio.v1.quiz_namespace import MessageNamespace, QuestionNamespace


@pytest.mark.anyio
@pytest.mark.parametrize(
    "namespace_type, crud_type, model, content, updated",
    [
        (
            TextNamespace,
            TextCRUD,
            Text,
            {"content": "child", "confidential": "secret"},
            {"content": "updated"},
        ),
        (NumberNamespace, NumberCRUD, Number, {"value": 2}, {"value": 3.5}),
    ],
)
async def test_data_socket_mutations_and_parent_scoped_transfers(
    namespace_type, crud_type, model, content, updated, register_current_user
):
    user = await register_current_user()
    async with TextCRUD() as crud:
        parent = await crud.create(Text.Create(content="parent"), user)
        other_parent = await crud.create(Text.Create(content="other"), user)
    server = SimpleNamespace(
        emit=AsyncMock(),
        rooms=Mock(return_value=[]),
        enter_room=AsyncMock(),
        close_room=AsyncMock(),
        get_session=AsyncMock(return_value={}),
        save_session=AsyncMock(),
    )
    namespace = namespace_type(server=server)
    namespace._get_current_user_and_check_guard = AsyncMock(return_value=user)
    namespace._get_session_query_string = AsyncMock(return_value=None)
    assert namespace.callback_on_connect is None
    await namespace.on_submit(
        "sid",
        {
            "payload": content,
            "parent_id": str(parent.id),
            "label": "answer",
            "inherit": True,
        },
    )
    statuses = [
        call.args[1] for call in server.emit.await_args_list if call.args[0] == "status"
    ]
    assert not [status for status in statuses if "error" in status], statuses
    created = next(status for status in statuses if status.get("success") == "created")
    child_id = created["id"]
    linked = [status for status in statuses if status.get("success") == "linked"]
    assert linked and all("label" not in status for status in linked)
    server.emit.reset_mock()
    await namespace.on_submit(
        "sid", {"payload": content, "parent_id": str(parent.id), "label": "answer"}
    )
    assert server.emit.await_count == 1
    assert "409" in server.emit.await_args.args[1]["detail"]
    server.emit.reset_mock()
    await namespace.on_link(
        "sid",
        {"parent_id": str(other_parent.id), "child_id": child_id, "label": "other"},
    )
    assert all("label" not in call.args[1] for call in server.emit.await_args_list)
    server.emit.reset_mock()
    async with TextCRUD() as crud:
        cursor = await crud.logging_crud.read_cursor()
    await namespace.on_changelink(
        "sid", {"parent_id": str(parent.id), "child_id": child_id, "label": "renamed"}
    )
    assert all("label" not in call.args[1] for call in server.emit.await_args_list)
    await namespace.on_submit("sid", {"payload": {"id": child_id, **updated}})
    async with crud_type() as crud:
        child = await crud.read_by_id(child_id, user)
        assert all(getattr(child, key) == value for key, value in updated.items())
    parent_namespace = TextNamespace(server=server)
    parent_namespace._get_current_user_and_check_guard = AsyncMock(return_value=user)
    parent_namespace._get_session_query_string = AsyncMock(return_value=None)
    server.emit.reset_mock()
    await parent_namespace.on_read("sid", parent.id)
    plain = next(
        call.args[1]
        for call in server.emit.await_args_list
        if call.args[0] == "transferred"
    )
    assert "hierarchies" not in plain
    # Metadata enrichment must not disclose the child's binding under other_parent.
    parent_namespace._get_session_query_string = AsyncMock(
        side_effect=lambda sid, name: True if name == "request_access_data" else None
    )
    server.emit.reset_mock()
    await parent_namespace.on_read("sid", parent.id)
    transferred = next(
        call.args[1]
        for call in server.emit.await_args_list
        if call.args[0] == "transferred"
    )
    assert len(transferred["hierarchies"]) == 1
    assert transferred["hierarchies"][0]["label"] == "renamed"
    assert transferred["hierarchies"][0]["parent_id"] == str(parent.id)
    children = transferred["texts"] if model is Text else transferred["numbers"]
    assert children[0]["id"] == child_id
    if model is Text:
        assert children[0]["confidential"] == "secret"
    server.emit.reset_mock()
    parent_namespace._get_session_query_string = AsyncMock(return_value=None)
    subscribed = await parent_namespace.on_subscribe(
        "sid", {"entity_ids": [str(parent.id)], "cursor": cursor}
    )
    assert subscribed.get("subscribed") == [str(parent.id)]
    replay = [
        call.args[1]
        for call in server.emit.await_args_list
        if call.args[0] == "transferred" and call.args[1]["id"] == str(parent.id)
    ]
    assert len(replay) == 1
    assert not replay[0]["hierarchies"]
    await namespace.on_changelink(
        "sid",
        {"parent_id": str(parent.id), "child_id": child_id, "inherit": False},
    )
    async with crud_type() as crud:
        edges = await crud.hierarchy_CRUD(session=crud.session).read(
            user, parent.id, child.id
        )
        assert edges[0].inherit is False
        assert edges[0].label == "renamed"
    await namespace.on_changelink(
        "sid",
        {"parent_id": str(parent.id), "child_id": child_id, "label": None},
    )
    async with crud_type() as crud:
        edges = await crud.hierarchy_CRUD(session=crud.session).read(
            user, parent.id, child.id
        )
        assert edges[0].inherit is False
        assert edges[0].label is None
    await namespace.on_changelink(
        "sid",
        {
            "parent_id": str(parent.id),
            "child_id": child_id,
            "inherit": True,
            "label": "restored",
        },
    )
    await namespace.on_changelink(
        "sid",
        {"parent_id": str(parent.id), "child_id": child_id, "inherit": None},
    )
    async with crud_type() as crud:
        edges = await crud.hierarchy_CRUD(session=crud.session).read(
            user, parent.id, child.id
        )
        assert edges[0].inherit is True
        assert edges[0].label == "restored"
    server.emit.reset_mock()
    await namespace.on_changelink(
        "sid",
        {"parent_id": str(parent.id), "child_id": child_id, "label": "Invalid label"},
    )
    assert server.emit.await_count == 1
    assert server.emit.await_args.args[1]["error"]
    async with crud_type() as crud:
        edges = await crud.hierarchy_CRUD(session=crud.session).read(
            user, parent.id, child.id
        )
        assert edges[0].inherit is True
        assert edges[0].label == "restored"
    await namespace.on_unlink(
        "sid", {"parent_id": str(parent.id), "child_id": child_id}
    )
    async with crud_type() as crud:
        assert (await crud.read_by_id(child_id, user)).id
    await namespace.on_delete("sid", child_id)
    assert any(call.args[0] == "deleted" for call in server.emit.await_args_list)


@pytest.mark.anyio
@pytest.mark.parametrize("namespace_type", [TextNamespace, NumberNamespace])
async def test_anonymous_data_socket_cannot_create_standalone(namespace_type):
    server = SimpleNamespace(emit=AsyncMock())
    namespace = namespace_type(server=server)
    namespace._get_current_user_and_check_guard = AsyncMock(return_value=None)
    content = {"content": "text"} if namespace_type is TextNamespace else {"value": 2}
    await namespace.on_submit("sid", {"payload": content})
    assert server.emit.await_count == 1
    assert server.emit.await_args.args[1]["error"]


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
@pytest.mark.parametrize(
    "namespace_type, hierarchy, model, entity_type",
    [
        (
            DemoResourceNamespace,
            ResourceHierarchy,
            DemoResource,
            ResourceType.demo_resource,
        ),
        (GroupNamespace, IdentityHierarchy, Group, IdentityType.group),
    ],
    ids=["resource", "identity"],
)
async def test_link_emits_cycle_conflict_without_success(
    namespace_type,
    hierarchy,
    model,
    entity_type,
    register_current_user,
    register_one_resource,
    get_async_test_session,
    monkeypatch,
):
    monkeypatch.setitem(hierarchy.relations, entity_type, [entity_type])
    current_user = await register_current_user()
    parent_id, child_id = uuid4(), uuid4()
    for node_id in (parent_id, child_id):
        await register_one_resource(node_id, model)
    session = get_async_test_session
    session.add(hierarchy(parent_id=child_id, child_id=parent_id, inherit=False))
    await session.commit()
    server = SimpleNamespace(emit=AsyncMock())
    namespace = namespace_type(server=server)
    namespace._get_current_user_and_check_guard = AsyncMock(return_value=current_user)

    await namespace.on_link(
        "sid", {"parent_id": str(parent_id), "child_id": str(child_id)}
    )

    server.emit.assert_awaited_once_with(
        "status",
        {"error": "other", "detail": "409: Hierarchy cycle detected."},
        namespace=namespace.namespace,
        to=["sid", "role:Admin"],
    )
    assert await session.get(hierarchy, (parent_id, child_id)) is None


@pytest.mark.anyio
async def test_demo_resource_namespace_has_no_connect_time_collection_replay():
    namespace = DemoResourceNamespace(server=SimpleNamespace())

    assert namespace.callback_on_connect is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_string, data_on_connect",
    [
        ("", True),
        ("data-on-connect=true", True),
        ("data-on-connect=false", False),
        ("data-on-connect=False", False),
    ],
)
async def test_data_on_connect_controls_initial_message_collection_transfer(
    query_string, data_on_connect
):
    server: Any = SimpleNamespace(enter_room=AsyncMock(), save_session=AsyncMock())
    namespace = MessageNamespace(server=server)
    namespace._get_event_guards = Mock(
        return_value=SimpleNamespace(allows_anonymous=True)
    )
    namespace._get_all = AsyncMock()

    await namespace.on_connect("sid", {"QUERY_STRING": query_string})

    session_data = server.save_session.call_args.args[1]
    assert session_data["query_strings"]["data_on_connect"] is data_on_connect
    if data_on_connect:
        namespace._get_all.assert_awaited_once_with("sid", None, False, parent_id=None)
    else:
        namespace._get_all.assert_not_awaited()


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
