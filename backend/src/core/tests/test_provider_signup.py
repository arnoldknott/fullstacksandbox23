"""Provider signup persistence, isolation, concurrency, and input boundaries."""

import asyncio
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from core.config import config
from core.security import CurrentAccessToken
from core.types import Action, CurrentUserData, IdentityType
from crud.access import AccessLoggingCRUD
from crud.identity import UserCRUD
from models.access import AccessLog, AccessPolicy, IdentifierTypeLink
from models.identity import (
    MeUpdate,
    User,
    UserAccount,
    UserCreate,
    UserProfile,
    UserUpdate,
)

pytestmark = pytest.mark.anyio


async def signup(subject):
    async with UserCRUD() as crud:
        return await crud.linkedin_user_self_sign_up(subject)


async def test_linkedin_signup_minimal_identity_and_self_ownership(
    get_async_test_session,
):
    user, status = await signup("Case-Sensitive-sub")
    again, repeat_status = await signup("Case-Sensitive-sub")
    assert status == 201
    assert repeat_status == 200
    assert again.id == user.id
    assert user.linkedin_user_id == "Case-Sensitive-sub"
    assert user.azure_user_id is None
    assert user.azure_tenant_id is None
    session = get_async_test_session
    stored = await session.get(User, user.id)
    assert stored is not None
    assert stored.user_account is not None
    assert stored.user_profile is not None
    for record, expected in [
        (stored, IdentityType.user),
        (stored.user_account, IdentityType.user_account),
        (stored.user_profile, IdentityType.user_profile),
    ]:
        link = await session.get(IdentifierTypeLink, record.id)
        assert link is not None and link.type == expected
    policy = (
        await session.exec(
            select(AccessPolicy).where(
                AccessPolicy.identity_id == user.id, AccessPolicy.resource_id == user.id
            )
        )
    ).one()
    assert policy.action == Action.own


@pytest.mark.parametrize("provider", ["microsoft", "linkedin"])
async def test_concurrent_signup_creates_one_account(provider, get_async_test_session):
    oid = uuid4()

    async def resolve():
        if provider == "linkedin":
            return await signup("same-sub")
        async with UserCRUD() as crud:
            return await crud.azure_user_self_sign_up(
                oid, UUID(config.AZURE_TENANT_ID), []
            )

    results = await asyncio.gather(*(resolve() for _ in range(5)))
    assert len({user.id for user, _ in results}) == 1
    assert sorted(status for _, status in results) == [200, 200, 200, 200, 201]
    for model in (User, UserAccount, UserProfile):
        assert (
            len((await get_async_test_session.exec(select(model))).unique().all()) == 1
        )
    assert (
        len((await get_async_test_session.exec(select(IdentifierTypeLink))).all()) == 3
    )


async def test_signup_rolls_back_even_after_helper_commit(
    monkeypatch, get_async_test_session
):
    original = AccessLoggingCRUD.create

    async def fail_after_commit(self, *args, **kwargs):
        await original(self, *args, **kwargs)
        raise RuntimeError("Injected failure after a committed helper")

    monkeypatch.setattr(AccessLoggingCRUD, "create", fail_after_commit)
    with pytest.raises(RuntimeError):
        await signup("rollback-sub")
    for model in (
        User,
        UserAccount,
        UserProfile,
        AccessPolicy,
        AccessLog,
        IdentifierTypeLink,
    ):
        assert not (await get_async_test_session.exec(select(model))).unique().all()


async def test_subject_case_sensitive_and_database_unique(get_async_test_session):
    first, _ = await signup("Subject")
    second, _ = await signup("subject")
    assert first.id != second.id
    stored = await get_async_test_session.get(User, second.id)
    assert stored is not None
    stored.linkedin_user_id = "Subject"
    with pytest.raises(IntegrityError):
        await get_async_test_session.commit()
    await get_async_test_session.rollback()


@pytest.mark.parametrize("provider", ["microsoft", "linkedin"])
async def test_disabled_initialized_user_stays_disabled(
    provider, get_async_test_session
):
    oid = uuid4()
    tenant = UUID(config.AZURE_TENANT_ID)

    async def resolve():
        async with UserCRUD() as crud:
            if provider == "microsoft":
                return await crud.azure_user_self_sign_up(oid, tenant, [])
            return await crud.linkedin_user_self_sign_up("disabled-sub")

    user, _ = await resolve()
    stored = await get_async_test_session.get(User, user.id)
    assert stored is not None
    stored.is_active = False
    await get_async_test_session.commit()
    with pytest.raises(HTTPException) as error:
        await resolve()
    assert error.value.status_code == 403
    await get_async_test_session.refresh(stored)
    assert stored.is_active is False


async def test_invitation_activates_and_wrong_tenant_cannot_claim_it():
    owner, _ = await signup("inviter")
    current = CurrentUserData(
        user_id=owner.id, azure_token_roles=["Admin"], azure_token_groups=[]
    )
    oid = uuid4()
    tenant = UUID(config.AZURE_TENANT_ID)
    async with UserCRUD() as crud:
        invitation = await crud.create_invited_azure_user(current, oid)
        with pytest.raises(HTTPException):
            await crud.azure_user_self_sign_up(oid, uuid4(), [])
        activated, status = await crud.azure_user_self_sign_up(oid, tenant, [])
    assert status == 201
    assert activated.id == invitation.id
    assert activated.is_active is True


async def test_foreign_tenant_rejected_before_signup(get_async_test_session):
    with pytest.raises(HTTPException) as error:
        await CurrentAccessToken(
            {"oid": str(uuid4()), "tid": str(uuid4())}
        ).provides_current_user()
    assert error.value.status_code == 401
    assert not (await get_async_test_session.exec(select(User))).unique().all()


@pytest.mark.parametrize(
    "field", ["azure_user_id", "azure_tenant_id", "linkedin_user_id"]
)
async def test_admin_create_accepts_provider_identifiers(field):
    value = str(uuid4())
    created = UserCreate.model_validate({field: value})
    assert str(getattr(created, field)) == value


@pytest.mark.parametrize(
    "field", ["azure_user_id", "azure_tenant_id", "linkedin_user_id"]
)
async def test_user_update_cannot_write_provider_identifiers(field):
    updated = UserUpdate.model_validate({field: str(uuid4()), "is_active": False})
    assert field not in updated.model_dump(exclude_unset=True)
    with pytest.raises(ValidationError):
        MeUpdate.model_validate({"id": str(uuid4()), field: str(uuid4())})


@pytest.mark.parametrize(
    "settings",
    [
        {"user_account": {"user_id": str(uuid4())}},
        {"user_profile": {"id": str(uuid4())}},
        {"user_profile": {"theme_color": "invalid"}},
        {"user_profile": {"contrast": 2}},
    ],
)
async def test_profile_settings_input_boundary(settings):
    with pytest.raises(ValidationError):
        MeUpdate.model_validate({"id": str(uuid4()), **settings})


async def test_linkedin_does_not_sync_linked_microsoft_groups(monkeypatch):
    async def unexpected_sync(*args, **kwargs):
        pytest.fail("LinkedIn must never synchronize Azure groups")

    monkeypatch.setattr(UserCRUD, "_sync_azure_groups", unexpected_sync)
    await signup("no-azure-sync")


async def test_multiple_microsoft_users_have_null_linkedin_ids():
    async with UserCRUD() as crud:
        first, _ = await crud.azure_user_self_sign_up(
            uuid4(), UUID(config.AZURE_TENANT_ID), []
        )
        second, _ = await crud.azure_user_self_sign_up(
            uuid4(), UUID(config.AZURE_TENANT_ID), []
        )
    assert first.id != second.id
    assert first.linkedin_user_id is None and second.linkedin_user_id is None


async def test_linkedin_can_edit_own_settings_without_azure_claims():
    user, _ = await signup("settings-sub")
    current = CurrentUserData(
        user_id=user.id, azure_token_roles=[], azure_token_groups=[]
    )
    async with UserCRUD() as crud:
        updated = await crud.update_me(
            current,
            MeUpdate.model_validate(
                {
                    "id": str(user.id),
                    "user_account": {"ai_enabled": True},
                    "user_profile": {"contrast": 0.5},
                }
            ),
        )
        assert updated.user_account is not None and updated.user_account.ai_enabled
        assert updated.user_profile is not None and updated.user_profile.contrast == 0.5
        assert updated.user_profile.theme_color == "#353c6e"
