import asyncio
import uuid

import pytest
from fastapi import HTTPException
from sqlmodel import col, select

from core.config import config
from core.types import Action, IdentityProvider, IdentityType, ResourceType
from crud.account_merge import AccountMergeCRUD
from models.access import AccessLog, AccessPolicy, IdentifierTypeLink, IdentityHierarchy
from models.identity import User, UserAccount, UserProfile


def microsoft_claims() -> dict[str, str]:
    tenant_id = config.AZURE_TENANT_ID
    assert tenant_id is not None
    return {"oid": str(uuid.uuid4()), "tid": tenant_id}


@pytest.mark.anyio
async def test_unclaimed_provider_identity_attaches_without_creating_user():
    azure = microsoft_claims()
    linkedin = {"sub": f"linkedin-{uuid.uuid4()}"}
    async with AccountMergeCRUD() as crud:
        survivor, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(azure["oid"]), uuid.UUID(azure["tid"]), []
        )

    async with AccountMergeCRUD() as crud:
        result = await crud.link_or_preview(
            IdentityProvider.microsoft,
            azure,
            IdentityProvider.linkedin,
            linkedin,
        )
        users = (await crud.session.exec(select(User))).unique().all()

    assert result == "linked"
    assert len(users) == 1
    assert users[0].id == survivor.id
    assert users[0].linkedin_user_id == linkedin["sub"]


@pytest.mark.anyio
async def test_merge_keeps_initiator_applies_choices_and_removes_old_references():
    azure = microsoft_claims()
    linkedin = {"sub": f"linkedin-{uuid.uuid4()}"}
    async with AccountMergeCRUD() as crud:
        survivor, _ = await crud.linkedin_user_self_sign_up(linkedin["sub"])
        source, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(azure["oid"]), uuid.UUID(azure["tid"]), []
        )
        survivor_user = await crud.session.get(User, survivor.id)
        source_user = await crud.session.get(User, source.id)
        assert survivor_user and source_user
        assert survivor_user.id and source_user.id
        source_ids = {
            source_user.id,
            source_user.user_account_id,
            source_user.user_profile_id,
        }
        survivor_account = await crud.session.get(
            UserAccount, survivor_user.user_account_id
        )
        source_account = await crud.session.get(
            UserAccount, source_user.user_account_id
        )
        survivor_profile = await crud.session.get(
            UserProfile, survivor_user.user_profile_id
        )
        source_profile = await crud.session.get(
            UserProfile, source_user.user_profile_id
        )
        assert (
            survivor_account and source_account and survivor_profile and source_profile
        )
        survivor_account.ai_enabled = False
        source_account.ai_enabled = True
        survivor_profile.theme_color = "#111111"
        source_profile.theme_color = "#222222"
        group_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        crud.session.add_all(
            [
                IdentifierTypeLink(id=group_id, type=IdentityType.group),
                IdentifierTypeLink(id=resource_id, type=ResourceType.public_resource),
            ]
        )
        await crud.session.flush()
        crud.session.add_all(
            [
                survivor_account,
                source_account,
                survivor_profile,
                source_profile,
                IdentityHierarchy(
                    parent_id=group_id, child_id=survivor_user.id, inherit=False
                ),
                IdentityHierarchy(
                    parent_id=group_id, child_id=source_user.id, inherit=True
                ),
                AccessPolicy(
                    identity_id=survivor_user.id,
                    resource_id=resource_id,
                    action=Action.read,
                ),
                AccessPolicy(
                    identity_id=source_user.id,
                    resource_id=resource_id,
                    action=Action.write,
                ),
            ]
        )
        await crud.session.commit()

        preview = await crud.link_or_preview(
            IdentityProvider.linkedin,
            linkedin,
            IdentityProvider.microsoft,
            azure,
        )
        assert not isinstance(preview, str)
        # Microsoft has precedence by default, but an explicit choice wins.
        assert preview.defaults["ai_enabled"] == "source"
        await crud.merge_provider_users(
            IdentityProvider.linkedin,
            linkedin,
            IdentityProvider.microsoft,
            azure,
            preview.preview_hash,
            {"theme_color": "survivor"},
        )

        merged = await crud.session.get(User, survivor.id)
        assert merged is not None
        assert merged.azure_user_id == uuid.UUID(azure["oid"])
        assert merged.linkedin_user_id == linkedin["sub"]
        assert await crud.session.get(User, source.id) is None
        merged_account = await crud.session.get(UserAccount, merged.user_account_id)
        merged_profile = await crud.session.get(UserProfile, merged.user_profile_id)
        assert merged_account and merged_profile
        assert merged_account.ai_enabled is True
        assert merged_profile.theme_color == "#111111"
        merged_memberships = (
            await crud.session.exec(
                select(IdentityHierarchy).where(
                    IdentityHierarchy.parent_id == group_id,
                    IdentityHierarchy.child_id == survivor.id,
                )
            )
        ).all()
        assert len(merged_memberships) == 1
        assert merged_memberships[0].inherit is True
        merged_policy = (
            await crud.session.exec(
                select(AccessPolicy).where(
                    AccessPolicy.identity_id == survivor.id,
                    AccessPolicy.resource_id == resource_id,
                )
            )
        ).one()
        assert merged_policy.action == Action.write

        old_ids = [value for value in source_ids if value is not None]
        assert not (
            await crud.session.exec(
                select(IdentifierTypeLink).where(
                    col(IdentifierTypeLink.id).in_(old_ids)
                )
            )
        ).all()
        assert not (
            await crud.session.exec(
                select(AccessPolicy).where(
                    col(AccessPolicy.identity_id).in_(old_ids)
                    | col(AccessPolicy.resource_id).in_(old_ids)
                )
            )
        ).all()
        assert not (
            await crud.session.exec(
                select(IdentityHierarchy).where(
                    col(IdentityHierarchy.parent_id).in_(old_ids)
                    | col(IdentityHierarchy.child_id).in_(old_ids)
                )
            )
        ).all()
        assert not (
            await crud.session.exec(
                select(AccessLog).where(
                    col(AccessLog.identity_id).in_(old_ids)
                    | col(AccessLog.resource_id).in_(old_ids)
                )
            )
        ).all()


@pytest.mark.anyio
async def test_stale_preview_rolls_back_without_merging_users():
    azure = microsoft_claims()
    linkedin = {"sub": f"linkedin-{uuid.uuid4()}"}
    async with AccountMergeCRUD() as crud:
        survivor, _ = await crud.linkedin_user_self_sign_up(linkedin["sub"])
        source, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(azure["oid"]), uuid.UUID(azure["tid"]), []
        )
        preview = await crud.link_or_preview(
            IdentityProvider.linkedin,
            linkedin,
            IdentityProvider.microsoft,
            azure,
        )
        assert not isinstance(preview, str)
        survivor_user = await crud.session.get(User, survivor.id)
        assert survivor_user
        profile = await crud.session.get(UserProfile, survivor_user.user_profile_id)
        assert profile
        profile.contrast = 0.5
        crud.session.add(profile)
        await crud.session.commit()

        with pytest.raises(HTTPException, match="Merge preview is stale"):
            await crud.merge_provider_users(
                IdentityProvider.linkedin,
                linkedin,
                IdentityProvider.microsoft,
                azure,
                preview.preview_hash,
                {},
            )

        assert await crud.session.get(User, survivor.id) is not None
        assert await crud.session.get(User, source.id) is not None


@pytest.mark.anyio
async def test_conflicting_provider_identifiers_roll_back_every_change():
    azure = microsoft_claims()
    linkedin = {"sub": f"linkedin-{uuid.uuid4()}"}
    conflicting_linkedin_id = f"linkedin-{uuid.uuid4()}"
    async with AccountMergeCRUD() as crud:
        survivor, _ = await crud.linkedin_user_self_sign_up(linkedin["sub"])
        source, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(azure["oid"]), uuid.UUID(azure["tid"]), []
        )
        source_user = await crud.session.get(User, source.id)
        assert source_user
        source_user.linkedin_user_id = conflicting_linkedin_id
        crud.session.add(source_user)
        await crud.session.commit()

        preview = await crud.link_or_preview(
            IdentityProvider.linkedin,
            linkedin,
            IdentityProvider.microsoft,
            azure,
        )
        assert not isinstance(preview, str)
        with pytest.raises(
            HTTPException,
            match="Both users have different identities from the same provider",
        ):
            await crud.merge_provider_users(
                IdentityProvider.linkedin,
                linkedin,
                IdentityProvider.microsoft,
                azure,
                preview.preview_hash,
                {},
            )

    async with AccountMergeCRUD() as crud:
        survivor_after = await crud.session.get(User, survivor.id)
        source_after = await crud.session.get(User, source.id)
        assert survivor_after and source_after
        assert survivor_after.linkedin_user_id == linkedin["sub"]
        assert survivor_after.azure_user_id is None
        assert source_after.azure_user_id == uuid.UUID(azure["oid"])
        assert source_after.linkedin_user_id == conflicting_linkedin_id


@pytest.mark.anyio
async def test_concurrent_merge_confirmation_has_one_winner():
    azure = microsoft_claims()
    linkedin = {"sub": f"linkedin-{uuid.uuid4()}"}
    async with AccountMergeCRUD() as crud:
        survivor, _ = await crud.linkedin_user_self_sign_up(linkedin["sub"])
        source, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(azure["oid"]), uuid.UUID(azure["tid"]), []
        )
        preview = await crud.link_or_preview(
            IdentityProvider.linkedin,
            linkedin,
            IdentityProvider.microsoft,
            azure,
        )
        assert not isinstance(preview, str)

    async def confirm():
        async with AccountMergeCRUD() as crud:
            return await crud.merge_provider_users(
                IdentityProvider.linkedin,
                linkedin,
                IdentityProvider.microsoft,
                azure,
                preview.preview_hash,
                {},
            )

    results = await asyncio.gather(confirm(), confirm(), return_exceptions=True)

    successes = [result for result in results if isinstance(result, tuple)]
    conflicts = [
        result
        for result in results
        if isinstance(result, HTTPException) and result.status_code == 409
    ]
    assert successes == [(survivor.id, source.id)]
    assert len(conflicts) == 1


@pytest.mark.anyio
async def test_microsoft_initiated_merge_keeps_microsoft_user():
    azure = microsoft_claims()
    linkedin = {"sub": f"linkedin-{uuid.uuid4()}"}
    async with AccountMergeCRUD() as crud:
        survivor, _ = await crud.azure_user_self_sign_up(
            uuid.UUID(azure["oid"]), uuid.UUID(azure["tid"]), []
        )
        source, _ = await crud.linkedin_user_self_sign_up(linkedin["sub"])
        source_user = await crud.session.get(User, source.id)
        assert source_user
        source_profile = await crud.session.get(
            UserProfile, source_user.user_profile_id
        )
        assert source_profile
        source_profile.contrast = 0.5
        crud.session.add(source_profile)
        await crud.session.commit()

        preview = await crud.link_or_preview(
            IdentityProvider.microsoft,
            azure,
            IdentityProvider.linkedin,
            linkedin,
        )
        assert not isinstance(preview, str)
        assert preview.defaults["contrast"] == "survivor"
        await crud.merge_provider_users(
            IdentityProvider.microsoft,
            azure,
            IdentityProvider.linkedin,
            linkedin,
            preview.preview_hash,
            {},
        )

        merged = await crud.session.get(User, survivor.id)
        assert merged
        assert merged.linkedin_user_id == linkedin["sub"]
        assert merged.azure_user_id == uuid.UUID(azure["oid"])
        assert await crud.session.get(User, source.id) is None
        merged_profile = await crud.session.get(UserProfile, merged.user_profile_id)
        assert merged_profile
        assert merged_profile.contrast == 0.0
