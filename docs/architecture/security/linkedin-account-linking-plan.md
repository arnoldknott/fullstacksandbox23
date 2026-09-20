# LinkedIn authentication, account linking, and credential encryption

Status: implementation plan; application changes are not implemented by this document.

Agreed scope recorded on 2026-09-20. This is the shared implementation handoff for frontend, backend, database, and Redis changes. Keep decisions and progress here rather than maintaining separate plans in each application.

## 1. Agreed outcome

- Add LinkedIn login using the existing `openid-client` version 6 dependency. Keep Microsoft Authentication Library (MSAL) for Microsoft acquisition.
- Add only a nullable, unique `User.linkedin_user_id` containing the validated subject (`sub`). Keep `azure_user_id` and `azure_tenant_id`. No external-identity table, stored email requirement, or per-user issuer column.
- Keep the expected issuer (`iss`) and client identifier in configuration. Accept one configured LinkedIn application per identity namespace; pairwise subjects are not assumed equivalent across application registrations.
- Authenticate LinkedIn users with the provider's identity token under this application's explicitly configured frontend/backend authentication contract. No backend-issued tokens and no LinkedIn access-token authentication in this implementation.
- Keep ordinary backend requests authenticated by provider tokens. Keep Socket.IO's existing session reference for retrieving server-cached provider tokens; locating a session alone is not sufficient authentication.
- Preserve `guards: GuardTypes = Depends(...)` at endpoints. Events/endpoints configure outer admission; shared security resolves `CurrentUserData`; create/read/update/delete (CRUD) operations apply resource access policies.
- Keep `azure_token_roles` and `azure_token_groups` in `CurrentUserData`. Populate them only from the validated Microsoft authentication being used, restricted to the configured tenant. A LinkedIn session does not borrow claims from a linked Microsoft account.
- Authenticated message/numerical creators become owners through existing policies. Anonymous creation never grants ownership to a shared anonymous identity.
- Support first-time linking and merging existing users in either provider direction. Reassign references and delete superseded records; no merge history, alias records, or retired users.
- Encrypt necessary cached credentials and retained sensitive profile data. Load keys through existing startup configuration from local environment variables or Azure Key Vault when configured.
- Preserve anonymous admission per endpoint/event. Do not make every read public, open anonymous request-based creation because sockets allow it, or open anonymous answer update/delete.
- No cross-provider AND expressions, additional authentication service, new scripts, or deployment workflows.

## 2. Existing code and planned responsibility

Paths are relative to this document.

| Concern | Existing code | Planned responsibility |
| --- | --- | --- |
| User identifiers/settings | [identity model](../../../backend/src/models/identity.py) | LinkedIn subject, protected identifier updates, merge settings schemas |
| Signup and account operations | [identity CRUD](../../../backend/src/crud/identity.py) | Provider lookup/signup, verified attachment, common transactional merge |
| Authentication | [security.py](../../../backend/src/core/security.py) | Provider dispatch/validation, cached-token retrieval, guard evaluation and user resolution |
| Shared contracts | [types.py](../../../backend/src/core/types.py) | Provider alternatives in guards; retain current-user interface |
| Router-wide dependencies | [fastapi.py](../../../backend/src/core/fastapi.py) | Remove unintended Azure-only barriers on selected mixed-provider routes |
| Request-to-CRUD boundary | [BaseView](../../../backend/src/routers/api/v1/base.py) | Continue passing resolved users to CRUD, including admitted anonymous operations |
| Resource endpoints | [quiz.py](../../../backend/src/routers/api/v1/quiz.py), [presentation.py](../../../backend/src/routers/api/v1/presentation.py) | Named endpoint policies matching the matrix |
| Supporting endpoints | [identities.py](../../../backend/src/routers/api/v1/identities.py), [access.py](../../../backend/src/routers/api/v1/access.py) | Self-service link/merge and permission-controlled ownership operations |
| Inner authorization | [access CRUD](../../../backend/src/crud/access.py), [access models](../../../backend/src/models/access.py), [base CRUD](../../../backend/src/crud/base.py) | Ownership, filtering, inheritance, logs, reference reconciliation |
| Socket transport/security | [BaseNamespace](../../../backend/src/routers/socketio/v1/base.py) | Cached provider-token lookup and common policy evaluation |
| Socket declarations | [quiz namespaces](../../../backend/src/routers/socketio/v1/quiz_namespace.py), [presentation namespace](../../../backend/src/routers/socketio/v1/presentation_namespace.py) | Explicit event alternatives and existing anonymous admission |
| Provider acquisition | [microsoft.ts](../../../frontend_svelte/src/lib/server/oauth/microsoft.ts), [provider directory](../../../frontend_svelte/src/lib/server/oauth/) | Preserve Microsoft; implement prepared `linkedin.ts` placeholder |
| Login lifecycle | [login](../../../frontend_svelte/src/routes/(layout)/login/), [callback](../../../frontend_svelte/src/routes/(layout)/oauth/callback/), [logout](../../../frontend_svelte/src/routes/(layout)/logout/) | Provider-aware login/linking, callback completion and logout |
| Backend request credentials | [backendApi.ts](../../../frontend_svelte/src/lib/server/apis/backendApi.ts), [base.ts](../../../frontend_svelte/src/lib/server/apis/base.ts) | Select active provider credential without passing Microsoft scopes to LinkedIn |
| Sessions and interface | [types.d.ts](../../../frontend_svelte/src/lib/types.d.ts), [hooks.server.ts](../../../frontend_svelte/src/hooks.server.ts), [UserButton.svelte](../../../frontend_svelte/src/components/UserButton.svelte), [socketio.svelte.ts](../../../frontend_svelte/src/lib/socketio.svelte.ts) | Minimal provider-neutral display, link/merge controls, existing socket transport |
| Persistence/configuration | [frontend cache](../../../frontend_svelte/src/lib/server/cache.ts), [frontend config](../../../frontend_svelte/src/lib/server/config.ts), [backend cache](../../../backend/src/core/cache.py), [backend config](../../../backend/src/core/config.py) | Compatible encryption and provider configuration |

## 3. Authentication and guard contract

### Declaration and evaluation remain separate

Proposed syntax; this is not currently callable code:

```python
post_message_guards = Guards(
    MicrosoftGuard(scopes=["api.read", "api.write"], roles=["User"]),
    LinkedInGuard(),
)

# Endpoint parameter; the callable returns policy configuration:
guards: GuardTypes = Depends(post_message_guards)
```

Add `AllowAnonymous()` only where anonymous admission already exists. Socket `EventGuard` declarations use the same representation without FastAPI dependencies. No separate `Authorize` class or injected endpoint `current_user` is required.

The common security flow:

1. Extract an optional request bearer token, or retrieve a server-cached token through the existing socket session reference.
2. Read unverified `iss` only to select an allowlisted validator. Never trust identity claims or fetch keys/discovery from an arbitrary supplied issuer.
3. Validate the credential; carry the verified provider and claims in an internal authentication context.
4. Evaluate declared alternatives in order. Alternatives are OR; requirements within a provider branch are AND. A token cannot satisfy another provider's branch.
5. Resolve the verified identifier through its provider lookup/signup handler and produce `CurrentUserData`, or `None` for admitted anonymous access.
6. Pass that result through `BaseView`/`BaseNamespace` to existing access checks.

Replace `provide_http_token_payload_optional` with provider-neutral extraction/validation plus explicit anonymous policies. Required extraction must not reject missing credentials before an anonymous branch can be considered. Avoid duplicate cryptographic validation between dependencies and the common checker; policy configuration remains separate from validated token context.

**Anonymous compatibility:** current optional request authentication treats invalid Azure tokens as anonymous, and public socket paths also have fallback behavior. The instruction to preserve existing anonymous behavior requires characterization tests and preservation on currently anonymous paths. Never carry unverified claims into user data or fall back to anonymous on authenticated-only operations. Replacing this with strict rejection is a separate hardening decision, not an incidental provider-migration change. Tests distinguish absent tokens, invalid tokens, unmet branch requirements, and cache failures.

### LinkedIn identity-token validation and expiry

- Validate signature, explicit allowed algorithm, expected issuer, exact configured client audience, and applicable authorized-party/multiple-audience rules.
- Require a nonempty string subject, issuance time (`iat`), and expiry (`exp`); enforce relevant time checks with bounded clock tolerance.
- Validate callback state and nonce against a short-lived login transaction. Bind provider, login/link intent, initiating user, and allowed return destination. Use Proof Key for Code Exchange (PKCE) according to supported provider behavior and version 6 client-library guidance.
- This identity token authenticates within this application's configured login-client/backend trust boundary. It contains no LinkedIn-issued resource permissions for our backend; guards and access policies supply those decisions.
- No UserInfo call is needed merely to obtain the validated subject. No email/profile persistence is necessary for identity mapping.
- Cached token/key lookup never extends token validity. Check expiry for requests and authorized socket operations, subscriptions and replay. End protected room access on expiry and require valid authentication before resubscribing.
- A fixed identity-token lifetime has not been verified. Measure `exp - iat` during a real login without logging the token. Do not assume the advertised access-token lifetime applies or that refresh tokens are available. Reauthentication is the initial recovery path. If lifetime is unsuitable, revisit the decision explicitly; do not silently accept expired tokens or switch token types.

## 4. Endpoint and event matrix

Request paths below are relative to the Application Programming Interface (API) prefix `/api/v1`. Preserve each existing Microsoft branch's scopes, roles and groups; do not introduce new Microsoft role checks on currently optional reads. All admitted operations still run the inner access-policy checks.

### Request endpoints

| Existing route(s) | LinkedIn alternative | Anonymous alternative |
| --- | --- | --- |
| `GET /quiz/question/`, `/quiz/message/`, `/quiz/numerical/` | Yes | No, matching existing list guards |
| `GET /quiz/{question,message,numerical}/snapshot` | Yes | Yes |
| `GET /quiz/{question,message,numerical}/{resource_id}` | Yes | Yes |
| `POST /quiz/message/` | Yes; existing standalone-creation rules apply | No |
| `POST /quiz/question/{question_id}/message/` and `/numerical/` | Yes; verify parent permission and assign ownership | No |
| `PUT`, `DELETE /quiz/{message,numerical}/{resource_id}` | Yes; resource permissions decide | No |
| Question create/update/delete | No; retain Microsoft guards | No |
| `GET /presentation/` and `/presentation/snapshot` | Yes | No |
| `GET /presentation/{resource_id}` and `/presentation/path/{path}` | Yes | Yes |
| Presentation create/update/delete | No; retain Microsoft guards | No |

Do not activate commented-out standalone numerical creation or legacy quiz routes.

### Socket.IO

| Namespace/event | LinkedIn alternative | Anonymous alternative |
| --- | --- | --- |
| `/question`, `/presentation`, `/message`, `/numerical`: connect, read, subscribe and authorized replay | Yes | Preserve existing public admission/resource filtering |
| `/message`, `/numerical`: `submit:create` | Yes; authenticated creator owns answer | Yes, matching current socket behavior |
| `/message`, `/numerical`: `submit:update`, `delete` | Yes; resource permissions decide | No |
| `/message`, `/numerical`: `share` | Yes; policy-management permissions decide | No |
| `/question`, `/presentation`: create/update/delete | No; retain Microsoft guards | No |

Sharing/hierarchy authorization remains derived from the inner layer. Do not add a blanket Microsoft-only restriction on answer ownership operations. Currently `on_link` reuses `submit:create` guards and `on_unlink` reuses `submit:update`; account for these aliases explicitly. Preserve existing anonymous admission on those aliases, but enforce permissions on both related entities. Owning an answer does not authorize modifying an arbitrary question or group.

Preserve the [snapshot and incremental Socket.IO contract](../data-transfer/internal/rest-snapshot-incremental-socketio.md): no full collection transfer for snapshot-aware connections, with consistent authorization for snapshots, rooms, replay and mutations.

### Supporting routes

- Admit LinkedIn to own-user/profile/account operations and authenticated link/merge routes. Ordinary profile updates cannot set provider identifiers, update another user, or modify trusted claims.
- Admit LinkedIn to existing policy/right/hierarchy operations needed to exercise ownership, including relevant `access.py` routes. Retain required actions and filters, including per-resource checks for bulk operations. This is not unrestricted access to the entire router.
- Review router-wide dependencies: `/user` and `/access` currently require Azure scopes before endpoint policies execute. Move restrictions into relevant declarations so mixed-provider routes work without opening unrelated routes.
- Preserve group administration's existing Microsoft restrictions. LinkedIn users can be application-group members and inherit grants without receiving blanket group-management privileges.
- Keep administrator and tenant-group behavior Microsoft-specific, including frontend navigation and administrator socket rooms.
- Inventory every affected `GuardTypes` consumer, including unrelated namespaces and raw websocket routes; preserve behavior outside this rollout.

## 5. Implementation stages

### A. Policy types, provider dispatch, and compatibility tests

Files: `core/types.py`, `core/security.py`, request `BaseView`, socket `BaseNamespace`.

- Implement provider alternatives, callable `Guards`, and shared evaluation with a minimal verified-provider/claims context.
- Keep existing declarations working through a small migration adapter or migrate all call sites together. Old constructors or missing event declarations must not silently become public.
- Separate policy configuration from validation and user lookup; keep current endpoint layering.
- Add mocked tests before enabling LinkedIn: provider selection, wrong issuer/audience/signature, expiry, exact scope membership, roles/groups, anonymous compatibility and socket cache lookup.

Completion: existing Microsoft/anonymous tests pass and both transports evaluate the new representation. LinkedIn database signup is not yet required.

### B. Minimal user identity and signup

Files: `models/identity.py`, `crud/identity.py`, frontend identity types, [development migrations](../../../backend/src/migrations/dev/) and [stage/production migrations](../../../backend/src/migrations/stage_prod/).

- Add a nullable unique case-sensitive string `linkedin_user_id`, allowing multiple nulls. Preserve subject case/content rather than treating it as an email or universally unique identifier.
- Ensure LinkedIn-only users do not acquire an Azure tenant solely through `UserCreate`'s current default. Existing Microsoft users remain unchanged.
- Implement `linkedin_user_self_sign_up`; reuse internal user/account/profile/identifier creation where appropriate. Never invoke Azure group synchronization for LinkedIn.
- Resolve Microsoft identities against the validated configured tenant and object identifier; do not reinterpret its object identifier as an OpenID subject.
- Exclude provider-identifier assignment from ordinary profile/create/update inputs; permit only verified signup/linking paths.
- Handle concurrent signup and unique conflicts without duplicates or orphan settings records. Preserve deliberate disabled-user semantics.
- Follow each migration tree's actual current head and existing environment workflow, rather than assuming one revision can attach to both histories.

Completion: both providers resolve internal users, signup creates expected settings/self-ownership, and Microsoft data migrates unchanged.

### C. Frontend login, credential selection, and expiry

Files: provider modules, login/callback/logout routes, `backendApi.ts`, session types/hooks/layouts, configuration loaders.

- Implement prepared `linkedin.ts` with the installed version 6 interface and existing route scaffolding. Register the actual callback addresses. First-party parameters use kebab-case; external protocol parameters remain unchanged.
- Keep credentials server-side and separate from client session/layout data. Store active provider and private cache references in the server session.
- Select the active provider's credential for backend requests and socket cache lookup. Linking must not silently switch active identity or union cached claims.
- Keep Graph acquisition separate: LinkedIn-only login must not run unconditional Microsoft Graph `/me`, Microsoft silent acquisition, or Microsoft logout redirects.
- Reuse `locals.sessionData`, session status and `/user/me`. Adapt Microsoft-specific profile display and route protection without fabricating Microsoft profiles.
- Bind and consume login/link state securely, rotate/complete sessions, allowlist return destinations, and preserve embed/session restoration.
- Add visible reauthentication and socket reconnect/resubscribe behavior on expiry. Logout removes application session/references; do not blindly delete account-wide caches used by other sessions.
- Extend existing configuration/example environment and synthetic test fixtures. Unconfigured LinkedIn must not break imports, worker startup, or frontend builds.

Completion: a real LinkedIn login reaches an authorized request and socket connection; actual token lifetime and recovery are verified; Microsoft login/logout still work. Live verification requires developer-app configuration; mocked tests do not.

### D. Resource/event policies and answer ownership

Files: matrix endpoints/namespaces, `core/fastapi.py`, `crud/base.py`, `crud/access.py`.

- Apply named guard configurations and remove Azure-specific optional extraction from migrated endpoints.
- Ensure authenticated creation assigns `Action.own` to the internal user, including creation under a publicly writable question. The public-creation branch must not discard valid caller identity.
- Preserve anonymous creation without a shared owner grant; update/delete remain blocked at the outer layer.
- Permit ownership-based sharing/hierarchy operations through existing access checks; retain checks on parent and child resources.
- Attribute activity to internal users consistently and preserve application-group inheritance.

Completion: owner/non-owner/anonymous request and socket tests pass for creation, reads, modification, deletion, sharing, hierarchy operations, snapshots and replay. This is the first complete participation milestone; linking is not required to release it.

### E. Verified attachment and reusable merge

Files: `crud/identity.py`, `routers/api/v1/identities.py`, access models/helpers, existing account interface around `UserButton.svelte`, provider callbacks.

Two distinct flows:

1. **First-time attachment:** bind a link transaction to the signed-in user and authenticate the other provider. Attach an unclaimed identifier directly without creating another user/account/profile. An identifier already attached to the same user is an idempotent success.
2. **Existing-user merge:** if the verified identifier belongs to another user, require proof of control of both identities, show a settings preview, and require explicit confirmation. Never silently transfer an identifier or use email matching as proof.

Provider handlers supply verified identities; one common merge operation handles internal users. Proposed retention convention: keep the initiating user's internal identifier, independently of which provider wins unresolved settings.

Settings and conflicts:

- Present conflicting `theme_color`, `theme_variant`, `contrast`, `ai_enabled`, and other differing settings as per-field choices.
- Explicit choices win. Unresolved settings use configured provider precedence: Microsoft before LinkedIn initially. Equal precedence retains the surviving user's value. A user with multiple linked providers has the highest-ranked configured provider for this fallback.
- Show defaults in the preview. Abandoning the dialog never commits a merge; defaults apply only to a confirmed operation.
- Preserve combined memberships/grants. Duplicate policies keep the strongest existing action using existing action ordering; duplicate hierarchy edges keep `inherit=True` if either enables it.
- Reject different identifiers for the same provider rather than discarding a login. One column per provider supports one account from each provider per user.

Transactional reassignment:

| Record | Handling |
| --- | --- |
| `User` provider fields | Transfer verified identifiers with safe unique-constraint ordering and concurrent-operation control |
| `UserAccount`, `UserProfile` | Apply resolved settings, retain one each, fix references in both directions |
| `AccessPolicy` | Remap identity and resource sides, including superseded settings identifiers; deduplicate before conflicting updates |
| `IdentityHierarchy` | Remap both ends, combine duplicates, preserve allowed types, prevent self-links/cycles |
| `AccessLog` | Remap identity/resource references; retain log identifiers, action, status and time; no permanent removed-user alias |
| `IdentifierTypeLink` | Delete superseded registrations after references are reassigned |
| Other references | Inventory database foreign keys and application-managed identifiers, including possible resource-hierarchy references |

Use one transaction, deterministic row locking, and revalidation of preview/proof before commit. Existing CRUD helpers commit internally, including policy/log helpers and normal user deletion. Do not compose them unchanged inside an allegedly atomic merge. Add a narrow transaction-aware operation under `UserCRUD`/`BaseCRUD`, preserving normal helper behavior elsewhere. Transfer/release source unique identifiers in a safe flush order. Any failure rolls back every database change.

Reconcile cache and sockets with the committed result: fence/revalidate affected operations, invalidate cached users/settings/permissions, disconnect affected sockets across instances, and rebuild subscriptions from fresh authorization. Stale rooms must not preserve former permissions or recreate a removed user. Database and Redis do not share a transaction: make cleanup retryable and fresh provider lookup authoritative if invalidation fails. Remove short-lived proof/preview data after completion or expiry, without adding permanent merge history.

Completion: both link directions, choices/defaults, duplicates, conflicting provider identifiers, concurrent attempts, rollback and stale-session tests pass. Successful cleanup leaves no application/database references to removed user/settings identifiers.

### F. Compatible encrypted cache persistence

Files: `microsoft.ts`, frontend `cache.ts`, backend `RedisPersistence` in `security.py`, both configuration loaders.

- Encrypt whole MSAL cache blobs: inspected adapters load/save complete documents. Decrypt before MSAL deserialization and encrypt after serialization; avoid depending on MSAL's internal credential-field schema.
- Encrypt cached LinkedIn identity tokens. Retain access/refresh tokens only for an actual integration need, not merely identity mapping.
- Preserve Redis JavaScript Object Notation (JSON) path operations on sessions. Encrypt needed sensitive account/profile subdocuments and minimize retained fields. Adapt both whole-session and path access in both runtimes so callers see original logical objects; never expose decrypted server-only data through layouts.
- Use compatible versioned envelopes, proposed fields `version`, `key-id`, `nonce`, `ciphertext`, `tag`. Use established libraries for Advanced Encryption Standard in Galois/Counter Mode (AES-GCM), fresh nonces, and associated data binding cache key/purpose.
- Load active and rotation read keys once through startup configuration. Keep keys outside Redis/PostgreSQL. Missing required keys must not trigger plaintext writes.
- Preserve cache expiry and refresh-write concurrency. Partitions must not collide across providers/applications.
- Transition in order: compatible readers on all instances, encrypted writers, then retire plaintext compatibility after migration/expiry. Malformed encrypted data is never reinterpreted as legacy plaintext. Retain old read keys while their records remain.
- Rollback after encrypted writes requires compatible readers, or deliberate authentication-cache invalidation and fresh login. Do not roll back by persisting decrypted tokens.
- Benchmark synthetic representative payloads in the test environment, including serialization, Redis round trips and tail latency. No deployment-specific encryption latency has been measured yet.

Completion: cross-runtime writes/reads, tamper/wrong-key rejection, JSON path behavior, expiry and transition tests pass; targeted stored credentials/profile fields contain no plaintext secrets.

## 6. Validation and rollout

Use only the test environment for formatting, linting, type checks, tests and benchmarks. Follow [backend guidance](../../../backend/AGENTS.md), [frontend guidance](../../../frontend_svelte/AGENTS.md), and existing [backend](../../../.github/workflows/backendAPI.yml) / [frontend](../../../.github/workflows/frontend_svelte.yml) continuous-integration workflows. Do not introduce alternate scripts. Report validation summaries in the called tools' format and distinguish baseline failures.

Extend these suites:

- [Security](../../../backend/src/core/tests/test_security.py) and [types](../../../backend/src/core/tests/test_types.py): dispatch, claims, policy alternatives, optional compatibility, cached tokens, administrator/tenant isolation.
- [Base CRUD](../../../backend/src/crud/tests/test_base_crud.py) and [access CRUD](../../../backend/src/crud/tests/test_access_crud.py): ownership, inheritance, strongest grants and non-owner denial. Add adjacent identity CRUD tests for merge transactions as needed.
- [Identity routes](../../../backend/src/routers/api/v1/tests/test_identities.py), [quiz routes](../../../backend/src/routers/api/v1/tests/test_quiz.py), [presentation routes](../../../backend/src/routers/api/v1/tests/test_presentation.py), [access routes](../../../backend/src/routers/api/v1/tests/test_access.py): full matrix, enclosing dependencies and forbidden provider-field updates.
- [Socket suites](../../../backend/src/routers/socketio/v1/tests/): providers, expiry, reconnect, mutation authorization, link/unlink aliases, subscription/replay isolation and merge invalidation.
- [Backend wrapper](../../../frontend_svelte/src/lib/server/apis/backendApi.test.ts), [socket client](../../../frontend_svelte/src/lib/socketio.svelte.test.ts), and adjacent provider/cache/component tests: selection, state/nonce, login versus link, conflict choices, recovery, cross-runtime encryption using synthetic fixtures.

Rollout:

1. Add identity migration and compatible guard/cache readers; keep LinkedIn disabled until configuration and tests are ready.
2. Enable LinkedIn login and selected endpoint/event alternatives after A–D pass; verify actual token lifetime and recovery.
3. Enable linking/confirmed merge after atomicity and stale-authorization tests pass.
4. Enable encrypted writes only after every reader is compatible; F can ship earlier if that condition is satisfied.
5. Verify staging before production using existing branches/environments. Disabling LinkedIn admission is reversible. A completed merge is deliberately destructive and has no application merge history from which to undo it. A migration downgrade must not silently discard populated provider identifiers.

## 7. Sequencing, handoffs, and tracking

Main chain: **A → B → C → D → E**, with tests in each stage. **F** can run alongside B–D after agreeing on cache format, partitioning, configuration and transition.

Keep authentication, guards and socket integration together: they share `security.py`, `types.py`, and the namespace base. Encryption is a suitable separate task once its contract is fixed. Merge work can be handed off after B and C's proof-of-identity interface are stable. Separate work uses isolated branches/worktrees and coordinates shared-file edits; do not run independent chats concurrently in this checkout.

No additional endpoint-policy decision is required to begin. Live verification needs provider application configuration, encryption needs startup key configuration, and actual identity-token lifetime must be measured before accepting the login experience. Do not paste real tokens or secrets into documentation or chat.

- [ ] A: policy and validation contract
- [ ] B: minimal identity/signup and migrations
- [ ] C: login, cache lookup, request integration and expiry
- [ ] D: endpoint/event matrix and ownership
- [ ] E: linking, merge preview, atomic reassignment and cleanup
- [ ] F: encrypted cache compatibility and rollout
- [ ] Test-environment validation and staging verification

## References

- [LinkedIn OpenID Connect](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2): identity claims, issuer, pairwise subjects and public verification keys; no fixed identity-token lifetime is assumed.
- [OpenID Connect identity-token validation](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation): issuer, audience, signature, time and nonce rules.
- [openid-client version 6.8.8](https://github.com/panva/openid-client/tree/v6.8.8): use the installed major version's interface.
- [MSAL Node cache guidance](https://learn.microsoft.com/en-us/entra/msal/javascript/node/caching): distributed persistence and encryption responsibilities.
