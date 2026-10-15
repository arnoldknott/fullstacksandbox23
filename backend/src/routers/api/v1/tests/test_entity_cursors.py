"""Cursor handoff contract across replay-capable entity endpoints."""

from uuid import uuid4

import pytest

from crud.access import AccessLoggingCRUD
from crud.demo_resource import DemoResourceCRUD
from crud.identity import GroupCRUD, SubGroupCRUD, SubSubGroupCRUD, UeberGroupCRUD
from crud.presentation import PresentationCRUD
from crud.protected_resource import (
    ProtectedChildCRUD,
    ProtectedGrandChildCRUD,
    ProtectedResourceCRUD,
)
from crud.quiz import MessageCRUD, NumericalCRUD, QuestionCRUD
from tests.utils import token_admin_read_write
from tests.utils_presentations import one_test_presentation
from tests.utils_quiz import one_test_message, one_test_numerical, one_test_question

ENTITY_READS = [
    ("/presentation", PresentationCRUD, one_test_presentation),
    ("/demoresource", DemoResourceCRUD, {"name": "Cursor resource"}),
    ("/protected/resource", ProtectedResourceCRUD, {"name": "Cursor resource"}),
    ("/protected/child", ProtectedChildCRUD, {"title": "Cursor child"}),
    ("/protected/grandchild", ProtectedGrandChildCRUD, {"text": "Cursor grandchild"}),
    ("/quiz/question", QuestionCRUD, one_test_question),
    ("/quiz/message", MessageCRUD, one_test_message),
    ("/quiz/numerical", NumericalCRUD, one_test_numerical),
    ("/uebergroup", UeberGroupCRUD, {"name": "Cursor identity"}),
    ("/group", GroupCRUD, {"name": "Cursor identity"}),
    ("/subgroup", SubGroupCRUD, {"name": "Cursor identity"}),
    ("/subsubgroup", SubSubGroupCRUD, {"name": "Cursor identity"}),
    ("/user", None, None),
]


async def create_entity(crud_type, data, current_test_user, add_one_test_resource):
    if crud_type is None:
        entity_id = current_test_user.user_id
    else:
        parent_id = None
        if crud_type in (ProtectedChildCRUD, ProtectedGrandChildCRUD):
            parent = await add_one_test_resource(
                ProtectedResourceCRUD, {"name": "Parent"}, current_test_user
            )
            if crud_type is ProtectedGrandChildCRUD:
                parent = await add_one_test_resource(
                    ProtectedChildCRUD,
                    {"title": "Parent"},
                    current_test_user,
                    parent.id,
                )
            parent_id = parent.id
        elif crud_type is NumericalCRUD:
            parent = await add_one_test_resource(
                QuestionCRUD, one_test_question, current_test_user
            )
            parent_id = parent.id
        elif crud_type in (SubGroupCRUD, SubSubGroupCRUD):
            parent = await add_one_test_resource(
                GroupCRUD, {"name": "Parent"}, current_test_user
            )
            if crud_type is SubSubGroupCRUD:
                parent = await add_one_test_resource(
                    SubGroupCRUD, {"name": "Parent"}, current_test_user, parent.id
                )
            parent_id = parent.id
        entity = await add_one_test_resource(
            crud_type, data, current_test_user, parent_id
        )
        entity_id = entity.id

    return entity_id


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
)
@pytest.mark.parametrize("path,crud_type,data", ENTITY_READS)
async def test_entity_reads_capture_exactly_one_cursor(
    path,
    crud_type,
    data,
    async_client,
    app_override_provide_http_token_payload,
    mocked_provide_http_token_payload,
    current_test_user,
    add_one_test_resource,
    monkeypatch,
):
    entity_id = await create_entity(
        crud_type, data, current_test_user, add_one_test_resource
    )

    captured = []
    original = AccessLoggingCRUD.read_cursor

    async def read_cursor(self):
        cursor = await original(self)
        captured.append(cursor)
        return cursor

    monkeypatch.setattr(AccessLoggingCRUD, "read_cursor", read_cursor)
    paths = [path + "/", path + "/" + str(entity_id)]
    if path != "/user":
        paths.append(path + "/snapshot")
    if path == "/presentation":
        paths.append(path + "/path/" + data["path"].lstrip("/"))

    for endpoint in paths:
        captured.clear()
        response = await async_client.get("/api/v1" + endpoint)
        assert response.status_code == 200, response.text
        assert captured == [int(response.headers["X-Entity-Cursor"])]
        body = response.json()
        if isinstance(body, list):
            assert str(entity_id) in [item["id"] for item in body]
        else:
            assert body["id"] == str(entity_id)
            if path == "/user":
                captured.clear()
                azure_response = await async_client.get(
                    "/api/v1/user/azure/" + body["azure_user_id"]
                )
                assert azure_response.status_code == 200, azure_response.text
                assert captured == [int(azure_response.headers["X-Entity-Cursor"])]

    missing = await async_client.get("/api/v1" + path + "/" + str(uuid4()))
    assert missing.status_code == 404
    assert "X-Entity-Cursor" not in missing.headers


@pytest.mark.anyio
@pytest.mark.parametrize("mocked_provide_http_token_payload", [None], indirect=True)
@pytest.mark.parametrize("path,crud_type,data", ENTITY_READS)
async def test_unauthorized_entity_reads_do_not_advertise_a_cursor(
    path,
    crud_type,
    data,
    async_client,
    app_override_provide_http_token_payload,
    mocked_provide_http_token_payload,
):
    response = await async_client.get("/api/v1" + path + "/" + str(uuid4()))
    assert response.status_code in (401, 403, 404)
    assert "X-Entity-Cursor" not in response.headers


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload", [token_admin_read_write], indirect=True
)
@pytest.mark.parametrize(
    "path",
    [
        "/access/policies",
        "/category/",
        "/tag/",
        "/publicresource/",
        "/user/me",
        "/core/health",
    ],
)
async def test_non_replay_reads_do_not_query_cursor(
    path,
    async_client,
    app_override_provide_http_token_payload,
    mocked_provide_http_token_payload,
    monkeypatch,
):
    async def unexpected_cursor(self):
        pytest.fail("Excluded endpoint queried a replay cursor")

    monkeypatch.setattr(AccessLoggingCRUD, "read_cursor", unexpected_cursor)
    response = await async_client.get("/api/v1" + path)
    assert response.status_code in (200, 201), response.text
    assert "X-Entity-Cursor" not in response.headers
