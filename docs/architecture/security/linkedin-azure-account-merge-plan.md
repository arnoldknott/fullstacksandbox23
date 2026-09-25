# Account linking and merge across identity providers

Status: implemented on 2026-09-25 with automated backend and frontend validation complete. Live two-provider acceptance remains a staging rollout check.

This is the follow-up to the [LinkedIn authentication and encryption plan](./linkedin-account-linking-plan.md). It was extracted so that login, access, and encryption (Stages A–D and F of the main plan) can ship first. It specifies first-time attachment and existing-user merge across identity providers.

Write this provider-generically: Microsoft and LinkedIn are the first two providers, but the same merge operation must serve additional providers without rework. This is the account-merge exception defined by the [security change boundary](../../../AGENTS.md#security-layers-and-change-boundaries).

## Dependencies

- Stage B of the main plan: the minimal per-provider identity columns on `User` and provider signup handlers.
- Stage C of the main plan: the proof-of-identity interface (verified callback state and provider-supported nonce bound to provider, intent, initiating user, and return destination).

## Two distinct flows

1. **First-time attachment:** bind a link transaction to the signed-in user and authenticate the other provider. Attach an unclaimed identifier directly without creating another user/account/profile. An identifier already attached to the same user is an idempotent success.
2. **Existing-user merge:** if the verified identifier belongs to another user, require proof of control of both identities, show a settings preview, and require explicit confirmation. Never silently transfer an identifier or use email matching as proof.

Provider handlers supply verified identities; one common merge operation handles internal users. Proposed retention convention: keep the initiating user's internal identifier, independently of which provider wins unresolved settings.

## Settings and conflicts

- Present conflicting `theme_color`, `theme_variant`, `contrast`, `ai_enabled`, and other differing settings as per-field choices.
- Explicit choices win. Unresolved settings use configured provider precedence: Microsoft before LinkedIn initially. Equal precedence retains the surviving user's value. A user with multiple linked providers has the highest-ranked configured provider for this fallback.
- Show defaults in the preview. Abandoning the dialog never commits a merge; defaults apply only to a confirmed operation.
- Preserve combined memberships/grants. Duplicate policies keep the strongest existing action using existing action ordering; duplicate hierarchy edges keep `inherit=True` if either enables it.
- Reject different identifiers for the same provider rather than discarding a login. One column per provider supports one account from each provider per user.

## Transactional reassignment

| Record | Handling |
| --- | --- |
| `User` provider fields | Transfer verified identifiers with safe unique-constraint ordering and concurrent-operation control |
| `UserAccount`, `UserProfile` | Apply resolved settings, retain one each, fix references in both directions |
| `AccessPolicy` | Remap identity and resource sides, including superseded settings identifiers; deduplicate before conflicting updates |
| `IdentityHierarchy` | Remap both ends, combine duplicates, preserve allowed types, prevent self-links/cycles |
| `AccessLog` | Remap identity/resource references; retain log identifiers, action, status and time; no permanent removed-user alias |
| `IdentifierTypeLink` | Delete superseded registrations after references are reassigned |
| Other references | Inventory database foreign keys and application-managed identifiers, including possible resource-hierarchy references |

Use one transaction, deterministic row locking, and revalidation of preview/proof before commit. Existing CRUD helpers commit internally, including policy/log helpers and normal user deletion. Do not compose them unchanged inside an allegedly atomic merge. Keep the narrow transaction-aware operation in `AccountMergeCRUD`, derived from `UserCRUD`/`BaseCRUD`, preserving normal helper behavior elsewhere. Transfer/release source unique identifiers in a safe flush order. Any failure rolls back every database change.

## Cache and socket reconciliation

Reconcile cache and sockets with the committed result: fence/revalidate affected operations, invalidate cached users/settings/permissions, disconnect affected sockets across instances, and rebuild subscriptions from fresh authorization. Stale rooms must not preserve former permissions or recreate a removed user. Database and Redis do not share a transaction: make cleanup retryable and fresh provider lookup authoritative if invalidation fails. Remove short-lived proof/preview data after completion or expiry, without adding permanent merge history.

## Files

`crud/account_merge.py`, `crud/identity.py`, `routers/api/v1/account_linking.py`, `routers/api/v1/identities.py`, access models/helpers, the inner authorization layer (`crud/base.py`, `crud/access.py`) for identity-reference reassignment only, the account menu in `Navbar.svelte`, and provider callbacks.

## Implemented design

- The initiating provider credential remains the ordinary request authorization. The independently verified linked-provider credential is sent in `X-Account-Link-Authorization`; no email or caller-supplied internal user identifier is accepted as proof.
- `POST /user/me/link/preview` directly attaches an unclaimed provider identity or returns a settings preview with an opaque hash. `POST /user/me/link/confirm` revalidates both credentials and the preview under deterministic row locks.
- `AccountMergeCRUD` contains provider attachment, merge preview, locking, reference reconciliation, and merge confirmation; general user signup and profile operations remain in `UserCRUD`.
- The initiating internal `User`, `UserAccount`, and `UserProfile` survive. Provider identifiers, access policies, hierarchy edges, resource hierarchy references, and access logs are reassigned in one database transaction; duplicates retain the strongest action or `inherit=True`.
- Provider link transactions are bound to the initiating provider and internal user. The provider-neutral Navbar account menu starts either link direction, and the protected merge page requires explicit confirmation for an existing-user merge.
- Successful merges invalidate every Redis session for both internal users and disconnect their sockets through per-session Socket.IO rooms. A short-lived Redis cleanup marker makes a failed post-commit disconnect/session cleanup retryable without retaining permanent merge history.
- Live validation (2026-09-25): starting from an existing Microsoft account and linking an existing LinkedIn account completed the merge successfully. The reverse LinkedIn-initiated direction remains pending live verification; automated tests cover both survivor directions.

## Completion

- [x] Both attachment and merge directions preserve the initiating internal user.
- [x] Explicit settings choices and Microsoft-before-LinkedIn defaults are covered.
- [x] Duplicate access policies and hierarchy memberships are reconciled without weakening access or inheritance.
- [x] Conflicting same-provider identifiers, stale previews, concurrent confirmations, and transaction rollback are covered.
- [x] Removed user/settings identifiers have no remaining application database references.
- [x] Affected sessions and sockets are invalidated, unrelated sessions remain, and failed cleanup can be retried.
- [ ] Complete one live existing-user merge in each provider direction in staging before production rollout.

## Rollout

Enable linking and confirmed merge only after atomicity and stale-authorization tests pass, and after the main plan's Stages A–D are in place. A completed merge is deliberately destructive and has no application merge history from which to undo it.
