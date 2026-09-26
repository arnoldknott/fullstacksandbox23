import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx2 import AsyncClient

from core.authentication.base import VerifiedIdentity
from core.cache import encryption, redis_session_client
from core.config import config
from core.security import provide_http_token_payload
from core.types import IdentityProvider
from crud.identity import UserCRUD
from models.identity import User
from routers.api.v1.account_linking import (
    _complete_merge_cleanup,
    _invalidate_merged_user_sessions,
)


def microsoft_identity() -> VerifiedIdentity:
    return VerifiedIdentity(
        IdentityProvider.microsoft,
        {"oid": str(uuid.uuid4()), "tid": config.AZURE_TENANT_ID},
    )


@pytest.mark.anyio
async def test_link_endpoint_attaches_an_unclaimed_provider_identity(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
):
    linkedin = VerifiedIdentity(
        IdentityProvider.linkedin, {"sub": f"linkedin-{uuid.uuid4()}"}
    )
    microsoft = microsoft_identity()
    async with UserCRUD() as crud:
        survivor, _ = await crud.linkedin_user_self_sign_up(linkedin.claims["sub"])

    app_override_provide_http_token_payload.dependency_overrides[
        provide_http_token_payload
    ] = lambda: linkedin
    verify = AsyncMock(return_value=microsoft)
    monkeypatch.setattr("routers.api.v1.account_linking.verify_access_token", verify)

    response = await async_client.post(
        "/api/v1/user/me/link/preview",
        headers={"X-Account-Link-Authorization": "Bearer linked-proof"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "linked"}
    verify.assert_awaited_once_with("linked-proof")
    async with UserCRUD() as crud:
        linked = await crud.session.get(User, survivor.id)
        assert linked
        assert linked.azure_user_id == uuid.UUID(microsoft.claims["oid"])


@pytest.mark.anyio
async def test_link_endpoint_previews_and_confirms_existing_user_merge(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
):
    linkedin = VerifiedIdentity(
        IdentityProvider.linkedin, {"sub": f"linkedin-{uuid.uuid4()}"}
    )
    microsoft = microsoft_identity()
    async with UserCRUD() as crud:
        survivor, _ = await crud.linkedin_user_self_sign_up(linkedin.claims["sub"])
        source, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(microsoft.claims["oid"]),
            uuid.UUID(microsoft.claims["tid"]),
            [],
        )

    app_override_provide_http_token_payload.dependency_overrides[
        provide_http_token_payload
    ] = lambda: linkedin
    monkeypatch.setattr(
        "routers.api.v1.account_linking.verify_access_token",
        AsyncMock(return_value=microsoft),
    )
    invalidate = AsyncMock()
    monkeypatch.setattr(
        "routers.api.v1.identities._invalidate_merged_user_sessions", invalidate
    )
    headers = {"X-Account-Link-Authorization": "Bearer linked-proof"}

    preview = await async_client.post("/api/v1/user/me/link/preview", headers=headers)
    assert preview.status_code == 200
    assert preview.json()["result"] == "merge-required"

    confirmed = await async_client.post(
        "/api/v1/user/me/link/confirm",
        headers=headers,
        json={"preview_hash": preview.json()["preview_hash"], "choices": {}},
    )

    assert confirmed.status_code == 200
    assert confirmed.json() == {"result": "merged"}
    invalidate.assert_awaited_once_with(
        {survivor.id, source.id}, preview.json()["preview_hash"]
    )
    async with UserCRUD() as crud:
        assert await crud.session.get(User, survivor.id) is not None
        assert await crud.session.get(User, source.id) is None


@pytest.mark.anyio
async def test_link_endpoint_rejects_a_second_proof_from_the_same_provider(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
):
    linkedin = VerifiedIdentity(
        IdentityProvider.linkedin, {"sub": f"linkedin-{uuid.uuid4()}"}
    )
    app_override_provide_http_token_payload.dependency_overrides[
        provide_http_token_payload
    ] = lambda: linkedin
    monkeypatch.setattr(
        "routers.api.v1.account_linking.verify_access_token",
        AsyncMock(return_value=linkedin),
    )

    response = await async_client.post(
        "/api/v1/user/me/link/preview",
        headers={"X-Account-Link-Authorization": "Bearer same-provider-proof"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "A different provider is required."


@pytest.mark.anyio
async def test_merge_invalidation_disconnects_and_deletes_only_affected_sessions(
    monkeypatch: pytest.MonkeyPatch,
):
    survivor_id = uuid.uuid4()
    source_id = uuid.uuid4()
    unrelated_id = uuid.uuid4()
    session_ids = {
        "survivor": str(uuid.uuid4()),
        "source": str(uuid.uuid4()),
        "unrelated": str(uuid.uuid4()),
    }
    try:
        for name, user_id in (
            ("survivor", survivor_id),
            ("source", source_id),
            ("unrelated", unrelated_id),
        ):
            redis_key = f"session:{session_ids[name]}"
            redis_session_client.json().set(
                redis_key,
                ".",
                {
                    "currentUser": {
                        "id": encryption.encrypt(
                            redis_key, "$.currentUser.id", str(user_id)
                        )
                    }
                },
            )
        disconnect = AsyncMock()
        monkeypatch.setattr(
            "routers.api.v1.account_linking.disconnect_auth_sessions", disconnect
        )

        await _invalidate_merged_user_sessions(
            {survivor_id, source_id}, "successful-cleanup"
        )

        disconnect.assert_awaited_once_with(
            {session_ids["survivor"], session_ids["source"]}
        )
        assert not redis_session_client.exists(f"session:{session_ids['survivor']}")
        assert not redis_session_client.exists(f"session:{session_ids['source']}")
        assert redis_session_client.exists(f"session:{session_ids['unrelated']}")
    finally:
        redis_session_client.delete(
            *(f"session:{session_id}" for session_id in session_ids.values())
        )


@pytest.mark.anyio
async def test_merge_cleanup_can_retry_after_socket_disconnect_failure(
    monkeypatch: pytest.MonkeyPatch,
):
    user_id = uuid.uuid4()
    session_id = str(uuid.uuid4())
    cleanup_id = f"cleanup-{uuid.uuid4()}"
    session_key = f"session:{session_id}"
    cleanup_key = f"session:merge-cleanup:{cleanup_id}"
    try:
        redis_session_client.json().set(
            session_key,
            ".",
            {
                "currentUser": {
                    "id": encryption.encrypt(
                        session_key, "$.currentUser.id", str(user_id)
                    )
                }
            },
        )
        monkeypatch.setattr(
            "routers.api.v1.account_linking.disconnect_auth_sessions",
            AsyncMock(side_effect=RuntimeError("temporary Socket.IO failure")),
        )

        with pytest.raises(RuntimeError, match="temporary Socket.IO failure"):
            await _invalidate_merged_user_sessions({user_id}, cleanup_id)

        assert redis_session_client.exists(session_key)
        assert redis_session_client.exists(cleanup_key)
        disconnect = AsyncMock()
        monkeypatch.setattr(
            "routers.api.v1.account_linking.disconnect_auth_sessions", disconnect
        )

        assert await _complete_merge_cleanup(cleanup_id) is True
        disconnect.assert_awaited_once_with({session_id})
        assert not redis_session_client.exists(session_key)
        assert not redis_session_client.exists(cleanup_key)
    finally:
        redis_session_client.delete(session_key, cleanup_key)
