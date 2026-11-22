import asyncio
from uuid import UUID, uuid4

import pytest
from sqlmodel import select

from core.encryption import is_encryption_envelope
from core.types import Action
from models.access import AccessPolicy, ResourceHierarchy
from models.data import Text
from tests.utils import token_admin_read_write, token_user1_read_write


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
)
async def test_recursive_data_parent_labels_and_bounded_collections(
    async_client, app_override_provide_http_token_payload, get_async_test_session
):
    client = async_client
    presentation = await client.post(
        "/api/v1/presentation/", json={"source": "test", "path": None}
    )
    assert presentation.status_code == 201, presentation.text
    parent = presentation.json()["id"]
    text = await client.post(
        f"/api/v1/text?parent-id={parent}&label=heading&inherit=true",
        json={
            "content": "Question?",
            "category": "question",
            "confidential": '{"answer":42}',
        },
    )
    assert text.status_code == 201, text.text
    text_id = text.json()["id"]
    assert text.json()["language"] is None
    number = await client.post(
        f"/api/v1/number?parent-id={parent}&label=heading&inherit=true",
        json={"value": 42, "category": "question"},
    )
    assert number.status_code == 201, number.text
    number_id = number.json()["id"]
    answer = await client.post(
        f"/api/v1/text?parent-id={text_id}&label=answer&inherit=true",
        json={"content": "Answer", "language": "da"},
    )
    assert answer.status_code == 201, answer.text
    comment = await client.post(
        f"/api/v1/number?parent-id={answer.json()['id']}&inherit=true",
        json={"value": 3},
    )
    assert comment.status_code == 201, comment.text
    cross = await client.post(
        f"/api/v1/access/hierarchy/{number_id}/child/{text_id}?label=caption"
    )
    assert cross.status_code == 201, cross.text

    lookup = await client.get(f"/api/v1/text?parent-id={parent}&label=heading")
    assert lookup.status_code == 200, lookup.text
    assert [row["id"] for row in lookup.json()] == [text_id]
    assert "X-Entity-Cursor" in lookup.headers
    assert (await client.get("/api/v1/text?label=heading")).status_code == 422
    for path in (f"/api/v1/presentation/{parent}", "/api/v1/presentation/"):
        response = await client.get(path)
        assert response.status_code == 200, response.text
        data = response.json()
        item = data[0] if isinstance(data, list) else data
        assert item["texts"][0]["confidential"] == '{"answer":42}'
        assert not item["texts"][0].get("texts")
        assert "hierarchies" not in item
    for path in (f"/api/v1/text/{text_id}", "/api/v1/text", "/api/v1/text/snapshot"):
        response = await client.get(path)
        assert response.status_code == 200, response.text
        items = (
            response.json() if isinstance(response.json(), list) else [response.json()]
        )
        for item in items:
            for child in item["texts"] + item["numbers"]:
                assert not child.get("texts")
                assert not child.get("numbers")
    loaded_number = (await client.get(f"/api/v1/number/{number_id}")).json()
    assert loaded_number["texts"][0]["confidential"] == '{"answer":42}'
    assert "hierarchies" not in loaded_number
    collection = (await client.get("/api/v1/text")).json()
    by_id = {item["id"]: item for item in collection}
    assert [child["id"] for child in by_id[text_id]["texts"]] == [answer.json()["id"]]
    assert [child["id"] for child in by_id[answer.json()["id"]]["numbers"]] == [
        comment.json()["id"]
    ]
    stored = await get_async_test_session.get(Text, UUID(text_id))
    assert is_encryption_envelope(stored.confidential)

    duplicate = await client.post(
        f"/api/v1/text?parent-id={parent}&label=heading", json={"content": "duplicate"}
    )
    assert duplicate.status_code == 409, duplicate.text
    rename = await client.put(
        f"/api/v1/access/hierarchy/{parent}/child/{text_id}", json={"label": "title"}
    )
    assert rename.status_code == 200, rename.text
    assert rename.json()["inherit"] is True
    inheritance_only = await client.put(
        f"/api/v1/access/hierarchy/{parent}/child/{text_id}", json={"inherit": False}
    )
    assert inheritance_only.status_code == 200, inheritance_only.text
    assert inheritance_only.json()["inherit"] is False
    assert inheritance_only.json()["label"] == "title"
    cleared = await client.put(
        f"/api/v1/access/hierarchy/{parent}/child/{text_id}", json={"label": None}
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["label"] is None
    assert cleared.json()["inherit"] is False
    assert (
        await client.get(f"/api/v1/text?parent-id={parent}&label=heading")
    ).json() == []
    assert (
        await client.get(f"/api/v1/text?parent-id={number_id}&label=caption")
    ).json()[0]["id"] == text_id
    cycle = await client.post(f"/api/v1/access/hierarchy/{text_id}/child/{number_id}")
    assert cycle.status_code == 409, cycle.text
    deletion = await client.delete(f"/api/v1/number/{number_id}")
    assert deletion.status_code == 200, deletion.text
    assert (await client.get(f"/api/v1/text/{text_id}")).status_code == 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
)
@pytest.mark.parametrize(
    "resource,payload",
    [
        ("text", {"content": "hello", "category": "Bad"}),
        ("text", {"content": "hello", "language": "dan"}),
        ("text", {"content": "hello", "label": "heading"}),
        ("text", {"content": "hello", "access_policies": []}),
        ("number", {"value": "not-a-number"}),
        ("number", {"value": "NaN"}),
        ("number", {"value": 2, "category": ""}),
    ],
)
async def test_data_rejects_invalid_input(
    async_client, app_override_provide_http_token_payload, resource, payload
):
    response = await async_client.post(f"/api/v1/{resource}", json=payload)
    assert response.status_code == 422, response.text


@pytest.mark.anyio
async def test_anonymous_data_submission_requires_direct_parent_connect_and_public_policy(
    async_client,
    app_override_provide_http_token_payload,
    add_one_test_access_policy,
    get_async_test_session,
):
    parent_id = uuid4()
    await add_one_test_access_policy(
        {"resource_id": str(parent_id), "action": "read", "public": True}, model=Text
    )
    assert (
        await async_client.post("/api/v1/text", json={"content": "standalone"})
    ).status_code != 201
    path = f"/api/v1/text?parent-id={parent_id}&public=true&public-action=write"
    assert (
        await async_client.post(path, json={"content": "answer"})
    ).status_code == 403
    policy = (
        await get_async_test_session.exec(
            select(AccessPolicy).where(AccessPolicy.resource_id == parent_id)
        )
    ).one()
    policy.action = Action.connect
    await get_async_test_session.commit()
    missing = await async_client.post(
        f"/api/v1/text?parent-id={parent_id}&public=true", json={"content": "answer"}
    )
    assert missing.status_code == 403
    response = await async_client.post(
        path, json={"content": "", "confidential": "secret"}
    )
    assert response.status_code == 201, response.text
    resource_id = response.json()["id"]
    assert (await async_client.get(f"/api/v1/text/{resource_id}")).json()[
        "confidential"
    ] == "secret"
    updated = await async_client.put(
        f"/api/v1/text/{resource_id}", json={"content": "updated"}
    )
    assert updated.status_code == 200, updated.text
    assert (await async_client.delete(f"/api/v1/text/{resource_id}")).status_code != 200


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_user1_read_write], indirect=True
)
@pytest.mark.parametrize(
    "path,payload",
    [
        ("/text", {"content": "parent"}),
        ("/presentation/", {"source": "test", "path": None}),
    ],
    ids=["recursive-text", "presentation"],
)
async def test_parent_data_includes_only_accessible_children_and_labels(
    async_client,
    app_override_provide_http_token_payload,
    add_one_test_access_policy,
    get_async_test_session,
    path,
    payload,
):
    parent = await async_client.post(f"/api/v1{path}", json=payload)
    assert parent.status_code == 201, parent.text
    parent_id = UUID(parent.json()["id"])
    children = {"hidden": uuid4(), "inherited": uuid4()}
    for label, child_id in children.items():
        await add_one_test_access_policy(
            {"resource_id": str(child_id), "public": True, "action": "read"}, model=Text
        )
        policy = (
            await get_async_test_session.exec(
                select(AccessPolicy).where(AccessPolicy.resource_id == child_id)
            )
        ).one()
        await get_async_test_session.delete(policy)
        get_async_test_session.add(
            Text.model_validate({"id": child_id, "content": label})
        )
        get_async_test_session.add(
            ResourceHierarchy(
                parent_id=parent_id,
                child_id=child_id,
                label=label,
                order=1,
                inherit=label == "inherited",
            )
        )
        await get_async_test_session.commit()
    response = await async_client.get(f"/api/v1{path.rstrip('/')}/{parent_id}")
    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()["texts"]] == [
        str(children["inherited"])
    ]
    assert "hierarchies" not in response.json()
    visible = await async_client.get(
        f"/api/v1/text?parent-id={parent_id}&label=inherited"
    )
    assert visible.status_code == 200, visible.text
    assert [row["id"] for row in visible.json()] == [str(children["inherited"])]
    assert (
        await async_client.get(f"/api/v1/text?parent-id={parent_id}&label=hidden")
    ).json() == []
    duplicate = await async_client.post(
        f"/api/v1/text?parent-id={parent_id}&label=hidden",
        json={"content": "duplicate"},
    )
    assert duplicate.status_code == 409, duplicate.text
    assert str(children["hidden"]) not in duplicate.text


# TBD: investigate if it ever can happen that a child is loaded already
# before any filters_allowed in the read operations.
# In that case a non-permitted child might get included in the response inadvertently.
# @pytest.mark.anyio
# @pytest.mark.parametrize(
#     "mocked_provide_http_token_payload", [token_user1_read_write], indirect=True
# )
# @pytest.mark.parametrize(
#     "path,payload,parent_model,crud_type",
#     [
#         ("/text", {"content": "parent"}, Text, TextCRUD),
#         ("/number", {"value": 0}, Number, NumberCRUD),
#     ],
#     ids=["text-parent", "number-parent"],
# )
# async def test_preloaded_relationship_is_filtered_for_current_user(
#     async_client,
#     app_override_provide_http_token_payload,
#     current_test_user,
#     add_one_test_access_policy,
#     get_async_test_session,
#     path,
#     payload,
#     parent_model,
#     crud_type,
# ):
#     response = await async_client.post(f"/api/v1{path}", json=payload)
#     assert response.status_code == 201, response.text
#     parent_id = UUID(response.json()["id"])
#     children = {"hidden": uuid4(), "inherited": uuid4()}
#     for label, child_id in children.items():
#         await add_one_test_access_policy(
#             {"resource_id": str(child_id), "public": True, "action": "read"},
#             model=Number,
#         )
#         policy = (
#             await get_async_test_session.exec(
#                 select(AccessPolicy).where(AccessPolicy.resource_id == child_id)
#             )
#         ).one()
#         await get_async_test_session.delete(policy)
#         get_async_test_session.add(Number.model_validate({"id": child_id, "value": 1}))
#         get_async_test_session.add(
#             ResourceHierarchy(
#                 parent_id=parent_id,
#                 child_id=child_id,
#                 order=1 if label == "inherited" else 2,
#                 inherit=label == "inherited",
#             )
#         )
#     await get_async_test_session.commit()

#     fresh_response = await async_client.get(f"/api/v1{path}/{parent_id}")
#     assert fresh_response.status_code == 200, fresh_response.text
#     assert [row["id"] for row in fresh_response.json()["numbers"]] == [
#         str(children["inherited"])
#     ]

#     parent = (
#         await get_async_test_session.exec(
#             select(parent_model)
#             .where(parent_model.id == parent_id)
#             .options(selectinload(parent_model.numbers))
#         )
#     ).one()
#     assert {child.id for child in parent.numbers} == set(children.values())

#     crud = crud_type()
#     crud.bind_session(get_async_test_session)
#     result = await crud.read_by_id(parent_id, current_test_user)
#     assert {child.id for child in result.numbers} == {children["inherited"]}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
)
async def test_concurrent_labeled_creation_is_atomic(
    async_client, app_override_provide_http_token_payload, get_async_test_session
):
    parent = await async_client.post("/api/v1/text", json={"content": "parent"})
    parent_id = parent.json()["id"]
    responses = await asyncio.gather(
        *[
            async_client.post(
                f"/api/v1/text?parent-id={parent_id}&label=answer",
                json={"content": f"answer-{index}"},
            )
            for index in range(2)
        ]
    )
    assert sorted(response.status_code for response in responses) == [201, 409]
    rows = (await get_async_test_session.exec(select(Text))).all()
    assert len(rows) == 2  # Failed submissions must not leave orphan content.
    edges = (await get_async_test_session.exec(select(ResourceHierarchy))).all()
    assert len(edges) == 1
    assert edges[0].label == "answer"
    standalone = await async_client.post(
        "/api/v1/text?label=orphan", json={"content": "invalid"}
    )
    assert standalone.status_code == 422
    assert len((await get_async_test_session.exec(select(Text))).all()) == 2


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_user1_read_write], indirect=True
)
async def test_number_updates_metadata_and_parent_local_ordering(
    async_client, app_override_provide_http_token_payload
):
    parent = await async_client.post("/api/v1/number", json={"value": 1})
    parent_id = parent.json()["id"]
    first = await async_client.post(
        f"/api/v1/number?parent-id={parent_id}&label=first", json={"value": 2}
    )
    second = await async_client.post(
        f"/api/v1/number?parent-id={parent_id}&label=second", json={"value": 3}
    )
    first_id, second_id = first.json()["id"], second.json()["id"]
    update = await async_client.put(
        f"/api/v1/number/{first_id}", json={"value": 2.5, "category": "score"}
    )
    assert update.status_code == 200, update.text
    assert update.json()["value"] == 2.5
    assert update.json()["category"] == "score"
    for payload in (
        {"value": None},
        {"value": "NaN"},
        {"label": "not-content"},
        {"id": str(uuid4())},
    ):
        response = await async_client.put(f"/api/v1/number/{first_id}", json=payload)
        assert response.status_code == 422, response.text
    move = await async_client.post(
        f"/api/v1/access/hierarchy/{parent_id}/move/{second_id}/start"
    )
    assert move.status_code == 201, move.text
    snapshot = await async_client.get(f"/api/v1/number/snapshot?parent-id={parent_id}")
    assert snapshot.status_code == 200, snapshot.text
    assert {row["id"] for row in snapshot.json()} == {second_id, first_id}
    loaded_parent = await async_client.get(f"/api/v1/number/{parent_id}")
    assert [row["id"] for row in loaded_parent.json()["numbers"]] == [
        second_id,
        first_id,
    ]
    duplicate = await async_client.put(
        f"/api/v1/access/hierarchy/{parent_id}/child/{first_id}",
        json={"label": "second"},
    )
    assert duplicate.status_code == 409, duplicate.text
    clear = await async_client.put(
        f"/api/v1/access/hierarchy/{parent_id}/child/{first_id}",
        json={"label": None},
    )
    assert clear.status_code == 200, clear.text
    assert clear.json()["label"] is None
    bulk = await async_client.post(
        "/api/v1/access/hierarchies",
        json=[{"parent_id": second_id, "child_id": first_id, "label": "shared"}],
    )
    assert bulk.status_code == 201, bulk.text
    assert bulk.json()[0]["label"] == "shared"
