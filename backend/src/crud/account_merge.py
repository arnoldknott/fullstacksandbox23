import json
from hashlib import sha256
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, update
from sqlmodel import col, delete, select

from core.config import config
from core.types import Action, IdentityProvider
from models.access import (
    AccessLog,
    AccessPolicy,
    IdentifierTypeLink,
    IdentityHierarchy,
    ResourceHierarchy,
)
from models.identity import (
    AccountMergePreview,
    User,
    UserAccount,
    UserProfile,
)

from .identity import UserCRUD


class AccountMergeCRUD(UserCRUD):
    @staticmethod
    def provider_identifier(
        provider: IdentityProvider, claims: dict[str, Any]
    ) -> tuple[str, UUID | str, UUID | None]:
        """Extract only identifiers from an already verified provider identity."""
        if provider == IdentityProvider.microsoft:
            oid = claims.get("oid")
            tid = claims.get("tid")
            try:
                tenant_id = UUID(str(tid))
                identifier = UUID(str(oid))
            except (TypeError, ValueError) as error:
                raise HTTPException(
                    status_code=401, detail="Invalid Microsoft identity."
                ) from error
            if tenant_id != UUID(config.AZURE_TENANT_ID):
                raise HTTPException(status_code=401, detail="Invalid Microsoft tenant.")
            return "azure_user_id", identifier, tenant_id
        if provider == IdentityProvider.linkedin:
            subject = claims.get("sub")
            if not isinstance(subject, str) or not subject:
                raise HTTPException(status_code=401, detail="Invalid LinkedIn subject.")
            return "linkedin_user_id", subject, None
        raise HTTPException(status_code=401, detail="Unsupported identity provider.")

    async def find_provider_user(
        self, provider: IdentityProvider, claims: dict[str, Any], *, lock: bool = False
    ) -> User | None:
        field_name, identifier, _ = self.provider_identifier(provider, claims)
        statement = select(User).where(getattr(User, field_name) == identifier)
        if lock:
            # User.azure_groups is joined eagerly, so an unrestricted FOR UPDATE
            # would also try to lock the nullable side of that outer join.
            statement = statement.with_for_update(of=User)
        return (await self.session.exec(statement)).unique().first()

    async def link_or_preview(
        self,
        survivor_provider: IdentityProvider,
        survivor_claims: dict[str, Any],
        source_provider: IdentityProvider,
        source_claims: dict[str, Any],
    ) -> Literal["linked", "already-linked"] | AccountMergePreview:
        """Attach an unclaimed provider identity or preview an existing-user merge."""
        if survivor_provider == source_provider:
            raise HTTPException(
                status_code=409, detail="A different provider is required."
            )
        survivor = await self.find_provider_user(
            survivor_provider, survivor_claims, lock=True
        )
        if survivor is None or survivor.id is None:
            raise HTTPException(
                status_code=409, detail="Initiating user no longer exists."
            )
        self._require_active_initiator(survivor)
        source = await self.find_provider_user(
            source_provider, source_claims, lock=True
        )
        field_name, identifier, tenant_id = self.provider_identifier(
            source_provider, source_claims
        )
        survivor_value = getattr(survivor, field_name)
        if survivor_value is not None and survivor_value != identifier:
            raise HTTPException(
                status_code=409,
                detail="A different account from this provider is already linked.",
            )
        if source is None:
            setattr(survivor, field_name, identifier)
            if source_provider == IdentityProvider.microsoft:
                survivor.azure_tenant_id = tenant_id
            self.session.add(survivor)
            await self.session.commit()
            return "linked"
        if source.id == survivor.id:
            return "already-linked"
        return await self._build_merge_preview(survivor, source)

    async def _build_merge_preview(
        self, survivor: User, source: User
    ) -> AccountMergePreview:
        survivor_id = survivor.id
        source_id = source.id
        if survivor_id is None or source_id is None:
            raise HTTPException(status_code=409, detail="Merge user is incomplete.")
        survivor_settings = await self._settings(survivor)
        source_settings = await self._settings(source)
        survivor_rank = self._provider_rank(survivor)
        source_rank = self._provider_rank(source)
        defaults: dict[str, Literal["survivor", "source"]] = {
            key: "source" if source_rank < survivor_rank else "survivor"
            for key in survivor_settings
        }
        settings = {
            key: {"survivor": survivor_settings[key], "source": source_settings[key]}
            for key in survivor_settings
            if survivor_settings[key] != source_settings[key]
        }
        defaults = {key: defaults[key] for key in settings}
        return AccountMergePreview(
            preview_hash=self._preview_hash(survivor_id, source_id, settings, defaults),
            settings=settings,
            defaults=defaults,
        )

    async def _settings(self, user: User) -> dict[str, Any]:
        account = await self.session.get(UserAccount, user.user_account_id)
        profile = await self.session.get(UserProfile, user.user_profile_id)
        if account is None or profile is None:
            raise HTTPException(status_code=409, detail="User settings are incomplete.")
        return {
            "ai_enabled": account.ai_enabled,
            "theme_color": profile.theme_color,
            "theme_variant": profile.theme_variant,
            "contrast": profile.contrast,
        }

    @staticmethod
    def _provider_rank(user: User) -> int:
        if user.azure_user_id is not None:
            return 0
        if user.linkedin_user_id is not None:
            return 1
        return 2

    @staticmethod
    def _preview_hash(
        survivor_id: UUID,
        source_id: UUID,
        settings: dict[str, Any],
        defaults: dict[str, Literal["survivor", "source"]],
    ) -> str:
        content = json.dumps(
            {
                "survivor_id": str(survivor_id),
                "source_id": str(source_id),
                "settings": settings,
                "defaults": defaults,
            },
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
        return sha256(content.encode()).hexdigest()

    async def merge_provider_users(
        self,
        survivor_provider: IdentityProvider,
        survivor_claims: dict[str, Any],
        source_provider: IdentityProvider,
        source_claims: dict[str, Any],
        preview_hash: str,
        choices: dict[str, Literal["survivor", "source"]],
    ) -> tuple[UUID, UUID]:
        """Atomically retain the initiating user and remove the other internal user."""
        try:
            return await self._merge_provider_users(
                survivor_provider,
                survivor_claims,
                source_provider,
                source_claims,
                preview_hash,
                choices,
            )
        except BaseException:
            await self.session.rollback()
            raise

    async def _merge_provider_users(
        self,
        survivor_provider: IdentityProvider,
        survivor_claims: dict[str, Any],
        source_provider: IdentityProvider,
        source_claims: dict[str, Any],
        preview_hash: str,
        choices: dict[str, Literal["survivor", "source"]],
    ) -> tuple[UUID, UUID]:
        if survivor_provider == source_provider:
            raise HTTPException(
                status_code=409, detail="A different provider is required."
            )
        users = [
            user
            for user in (
                await self.find_provider_user(survivor_provider, survivor_claims),
                await self.find_provider_user(source_provider, source_claims),
            )
            if user is not None and user.id is not None
        ]
        if len(users) != 2 or users[0].id == users[1].id:
            raise HTTPException(status_code=409, detail="Merge is no longer required.")
        self._require_active_initiator(users[0])
        survivor, source = await self._lock_merge_users(users[0], users[1])
        survivor_field, survivor_identifier, _ = self.provider_identifier(
            survivor_provider, survivor_claims
        )
        source_field, source_identifier, _ = self.provider_identifier(
            source_provider, source_claims
        )
        if (
            getattr(survivor, survivor_field) != survivor_identifier
            or getattr(source, source_field) != source_identifier
        ):
            raise HTTPException(status_code=409, detail="Provider identity changed.")
        preview = await self._build_merge_preview(survivor, source)
        if preview.preview_hash != preview_hash:
            raise HTTPException(status_code=409, detail="Merge preview is stale.")
        unknown = set(choices) - set(preview.settings)
        if unknown:
            raise HTTPException(status_code=422, detail="Unknown settings choice.")
        selected = {
            key: choices.get(key, preview.defaults[key]) for key in preview.settings
        }
        survivor_account = await self.session.get(UserAccount, survivor.user_account_id)
        source_account = await self.session.get(UserAccount, source.user_account_id)
        survivor_profile = await self.session.get(UserProfile, survivor.user_profile_id)
        source_profile = await self.session.get(UserProfile, source.user_profile_id)
        if (
            survivor_account is None
            or source_account is None
            or survivor_profile is None
            or source_profile is None
        ):
            raise HTTPException(status_code=409, detail="User settings are incomplete.")
        for key, winner in selected.items():
            target = survivor_account if key == "ai_enabled" else survivor_profile
            origin = source_account if key == "ai_enabled" else source_profile
            if winner == "source":
                setattr(target, key, getattr(origin, key))
        mapping, survivor_id, source_id, source_account_id, source_profile_id = (
            self._merge_reference_mapping(
                survivor,
                source,
                survivor_account,
                source_account,
                survivor_profile,
                source_profile,
            )
        )
        await self._remap_access_policies(mapping)
        await self._remap_hierarchy(IdentityHierarchy, mapping)
        await self._remap_hierarchy(ResourceHierarchy, mapping)
        for old_id, new_id in mapping.items():
            await self.session.exec(
                update(AccessLog)
                .where(col(AccessLog.identity_id) == old_id)
                .values(identity_id=new_id)
            )
            await self.session.exec(
                update(AccessLog)
                .where(col(AccessLog.resource_id) == old_id)
                .values(resource_id=new_id)
            )
        await self._transfer_provider_identifiers(survivor, source)
        self.session.add(survivor_account)
        self.session.add(survivor_profile)
        self.session.add(survivor)
        await self.session.flush()
        await self.session.exec(delete(User).where(col(User.id) == source_id))
        await self.session.exec(
            delete(UserAccount).where(col(UserAccount.id) == source_account_id)
        )
        await self.session.exec(
            delete(UserProfile).where(col(UserProfile.id) == source_profile_id)
        )
        await self.session.exec(
            delete(IdentifierTypeLink).where(
                col(IdentifierTypeLink.id).in_(list(mapping))
            )
        )
        await self.session.commit()
        return survivor_id, source_id

    @staticmethod
    def _merge_reference_mapping(
        survivor: User,
        source: User,
        survivor_account: UserAccount,
        source_account: UserAccount,
        survivor_profile: UserProfile,
        source_profile: UserProfile,
    ) -> tuple[dict[UUID, UUID], UUID, UUID, UUID, UUID]:
        survivor_id = survivor.id
        source_id = source.id
        survivor_account_id = survivor_account.id
        source_account_id = source_account.id
        survivor_profile_id = survivor_profile.id
        source_profile_id = source_profile.id
        if (
            survivor_id is None
            or source_id is None
            or survivor_account_id is None
            or source_account_id is None
            or survivor_profile_id is None
            or source_profile_id is None
        ):
            raise HTTPException(status_code=409, detail="User settings are incomplete.")
        return (
            {
                source_id: survivor_id,
                source_account_id: survivor_account_id,
                source_profile_id: survivor_profile_id,
            },
            survivor_id,
            source_id,
            source_account_id,
            source_profile_id,
        )

    async def _lock_merge_users(
        self, survivor: User, source: User
    ) -> tuple[User, User]:
        survivor_id = survivor.id
        source_id = source.id
        if survivor_id is None or source_id is None:
            raise HTTPException(status_code=409, detail="Merge user is incomplete.")
        user_ids = sorted((survivor_id, source_id), key=str)
        locked = (
            (
                await self.session.exec(
                    select(User)
                    .where(col(User.id).in_(user_ids))
                    .order_by(col(User.id))
                    .with_for_update(of=User)
                )
            )
            .unique()
            .all()
        )
        if len(locked) != 2:
            raise HTTPException(status_code=409, detail="Merge is no longer required.")
        by_id = {user.id: user for user in locked if user.id is not None}
        try:
            return by_id[survivor_id], by_id[source_id]
        except KeyError as error:
            raise HTTPException(
                status_code=409, detail="Merge is no longer required."
            ) from error

    @staticmethod
    def _require_active_initiator(user: User) -> None:
        if user.is_active is not True:
            raise HTTPException(status_code=403, detail="Initiating user is disabled.")

    async def _transfer_provider_identifiers(
        self, survivor: User, source: User
    ) -> None:
        transfers: dict[str, UUID | str] = {}
        for field_name in ("azure_user_id", "linkedin_user_id"):
            survivor_value = getattr(survivor, field_name)
            source_value = getattr(source, field_name)
            if (
                survivor_value is not None
                and source_value is not None
                and survivor_value != source_value
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Both users have different identities from the same provider.",
                )
            if survivor_value is None and source_value is not None:
                setattr(source, field_name, None)
                transfers[field_name] = source_value
        self.session.add(source)
        await self.session.flush()
        for field_name, source_value in transfers.items():
            setattr(survivor, field_name, source_value)
        if survivor.azure_tenant_id is None:
            survivor.azure_tenant_id = source.azure_tenant_id
        source.azure_tenant_id = None

    async def _remap_access_policies(self, mapping: dict[UUID, UUID]) -> None:
        affected = (
            await self.session.exec(
                select(AccessPolicy).where(
                    or_(
                        col(AccessPolicy.identity_id).in_(list(mapping)),
                        col(AccessPolicy.resource_id).in_(list(mapping)),
                    )
                )
            )
        ).all()
        rank = {Action.read: 0, Action.connect: 1, Action.write: 2, Action.own: 3}
        for policy in affected:
            identity_id = (
                mapping.get(policy.identity_id, policy.identity_id)
                if policy.identity_id is not None
                else None
            )
            resource_id = mapping.get(policy.resource_id, policy.resource_id)
            existing = (
                await self.session.exec(
                    select(AccessPolicy).where(
                        col(AccessPolicy.identity_id) == identity_id,
                        col(AccessPolicy.resource_id) == resource_id,
                        col(AccessPolicy.id) != policy.id,
                    )
                )
            ).first()
            if existing:
                if rank[policy.action] > rank[existing.action]:
                    existing.action = policy.action
                    self.session.add(existing)
                await self.session.delete(policy)
            else:
                policy.identity_id = identity_id
                policy.resource_id = resource_id
                self.session.add(policy)
            await self.session.flush()

    async def _remap_hierarchy(self, model, mapping: dict[UUID, UUID]) -> None:
        affected = (
            await self.session.exec(
                select(model).where(
                    or_(
                        col(model.parent_id).in_(list(mapping)),
                        col(model.child_id).in_(list(mapping)),
                    )
                )
            )
        ).all()
        for relation in affected:
            parent_id = mapping.get(relation.parent_id, relation.parent_id)
            child_id = mapping.get(relation.child_id, relation.child_id)
            if parent_id == child_id:
                await self.session.delete(relation)
                await self.session.flush()
                continue
            existing = (
                await self.session.exec(
                    select(model).where(
                        model.parent_id == parent_id,
                        model.child_id == child_id,
                        or_(
                            model.parent_id != relation.parent_id,
                            model.child_id != relation.child_id,
                        ),
                    )
                )
            ).first()
            if existing:
                existing.inherit = existing.inherit or relation.inherit
                self.session.add(existing)
                await self.session.delete(relation)
            else:
                relation.parent_id = parent_id
                relation.child_id = child_id
                self.session.add(relation)
            await self.session.flush()
