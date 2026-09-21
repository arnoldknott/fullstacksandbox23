# LinkedIn authentication, account linking, and credential encryption

Status: implementation plan; application changes are not implemented by this document.

Agreed scope recorded on 2026-09-20; encryption and rotation decisions updated on 2026-09-21. This is the shared implementation handoff for frontend, backend, database, and Redis changes. Keep decisions and progress here rather than maintaining separate plans in each application.

## 1. Agreed outcome

- Add LinkedIn login using the existing `openid-client` version 6 dependency. Keep Microsoft Authentication Library (MSAL) for Microsoft acquisition.
- Add only a nullable, unique `User.linkedin_user_id` containing the validated subject (`sub`). Keep `azure_user_id` and `azure_tenant_id`. No external-identity table, stored email requirement, or per-user issuer column.
- Keep the expected issuer (`iss`) and client identifier in configuration. Accept one configured LinkedIn application per identity namespace; pairwise subjects are not assumed equivalent across application registrations.
- Authenticate LinkedIn users with the provider's identity token under this application's explicitly configured frontend/backend authentication contract. No backend-issued tokens and no LinkedIn access-token authentication in this implementation.
- Keep ordinary backend requests authenticated by provider tokens. Keep Socket.IO's existing session reference for retrieving server-cached provider tokens; locating a session alone is not sufficient authentication.
- Preserve `guards: GuardTypes = Depends(...)` at endpoints. Events/endpoints configure outer admission; shared security resolves `CurrentUserData`; create/read/update/delete (CRUD) operations apply resource access policies.
- Keep `azure_token_roles` and `azure_token_groups` in `CurrentUserData`. Populate them only from the validated Microsoft authentication being used, restricted to the configured tenant. A LinkedIn session does not borrow claims from a linked Microsoft account.
- Authenticated message/numerical creators become owners through existing policies. Anonymous creation never grants ownership to a shared anonymous identity.
- Stages A–D require no changes to the inner authorization layer (`crud/access.py`, `crud/base.py`, `filters_allowed()`): it already operates on the internal `user_id` and treats a LinkedIn user with empty roles/groups correctly. Only the separate merge plan reassigns inner-layer identity references.
- Support first-time linking and merging existing users in either provider direction. Reassign references and delete superseded records; no merge history, alias records, or retired users. Linking and merge are specified in the separate [account merge plan](./linkedin-azure-account-merge-plan.md); Stages A–D of this document do not require them.
- Cache only authentication-derived third-party data, including credentials and necessary authentication metadata. Encrypt this permitted data. Data obtained by authorized third-party resource calls, including LinkedIn UserInfo and Microsoft Graph, remains transient in memory and is never cached or persisted, even encrypted. Follow the repository-wide [third-party data storage rule](../../../AGENTS.md#third-party-data-storage). Load encryption keys through existing startup configuration from local environment variables or Azure Key Vault when configured.
- Preserve anonymous admission per endpoint/event. Do not make every read public, open anonymous request-based creation because sockets allow it, or open anonymous answer update/delete.
- No cross-provider AND expressions, additional authentication service, new scripts, or deployment workflows.

## 2. Existing code and planned responsibility

Paths are relative to this document.

| Concern | Existing code | Planned responsibility |
| --- | --- | --- |
| User identifiers/settings | [identity model](../../../backend/src/models/identity.py) | LinkedIn subject, protected identifier updates, merge settings schemas |
| Signup and account operations | [identity CRUD](../../../backend/src/crud/identity.py) | Provider lookup/signup and verified attachment; transactional merge in the separate merge plan |
| Authentication | [security.py](../../../backend/src/core/security.py) | Provider dispatch/validation, cached-token retrieval, guard evaluation and user resolution |
| Shared contracts | [types.py](../../../backend/src/core/types.py) | Provider alternatives in guards; retain current-user interface |
| Router-wide dependencies | [fastapi.py](../../../backend/src/core/fastapi.py) | Relax router-level Microsoft guards only on selected mixed-provider routes; keep them on Microsoft-only routers |
| Request-to-CRUD boundary | [BaseView](../../../backend/src/routers/api/v1/base.py) | Continue passing resolved users to CRUD, including admitted anonymous operations |
| Resource endpoints | [quiz.py](../../../backend/src/routers/api/v1/quiz.py), [presentation.py](../../../backend/src/routers/api/v1/presentation.py) | Named endpoint policies matching the matrix |
| Supporting endpoints | [identities.py](../../../backend/src/routers/api/v1/identities.py), [access.py](../../../backend/src/routers/api/v1/access.py) | Self-service link/merge and permission-controlled ownership operations |
| Inner authorization | [access CRUD](../../../backend/src/crud/access.py), [access models](../../../backend/src/models/access.py), [base CRUD](../../../backend/src/crud/base.py) | Unchanged for Stages A–D; reference reconciliation only in the separate merge plan |
| Socket transport/security | [BaseNamespace](../../../backend/src/routers/socketio/v1/base.py) | Cached provider-token lookup and common policy evaluation |
| Socket declarations | [quiz namespaces](../../../backend/src/routers/socketio/v1/quiz_namespace.py), [presentation namespace](../../../backend/src/routers/socketio/v1/presentation_namespace.py) | Explicit event alternatives and existing anonymous admission |
| Provider acquisition | [microsoft.ts](../../../frontend_svelte/src/lib/server/oauth/microsoft.ts), [provider directory](../../../frontend_svelte/src/lib/server/oauth/) | Preserve Microsoft; implement prepared `linkedin.ts` placeholder |
| Login lifecycle | [login](../../../frontend_svelte/src/routes/(layout)/login/), [callback](../../../frontend_svelte/src/routes/(layout)/oauth/callback/), [logout](../../../frontend_svelte/src/routes/(layout)/logout/) | Provider-aware login/linking, callback completion and logout |
| Backend request credentials | [backendApi.ts](../../../frontend_svelte/src/lib/server/apis/backendApi.ts), [base.ts](../../../frontend_svelte/src/lib/server/apis/base.ts) | Select active provider credential without passing Microsoft scopes to LinkedIn |
| Sessions and interface | [types.d.ts](../../../frontend_svelte/src/lib/types.d.ts), [hooks.server.ts](../../../frontend_svelte/src/hooks.server.ts), [UserButton.svelte](../../../frontend_svelte/src/components/UserButton.svelte), [socketio.svelte.ts](../../../frontend_svelte/src/lib/socketio.svelte.ts) | Minimal provider-neutral display, link/merge controls, existing socket transport |
| Encryption infrastructure | [security.tf](../../../infrastructure/security.tf), [variables.tf](../../../infrastructure/variables.tf), existing deployment workflows | Per-environment secret generation, deliberate rotation, application secret-version discovery permissions, backend-first deployment |
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
- Keep existing router-level Microsoft guards in place for most routers. Selectively relax only the routers and endpoints that need non-Microsoft access: `presentation` reads, `quiz` question reads plus all `message`/`numerical` operations, and the user-handling endpoints (and the group-membership endpoints) required for LinkedIn signup and ownership. For those, move the Microsoft scope requirement from the router-level dependency (`/user`, `/access` in `fastapi.py`) into per-endpoint guard declarations so mixed-provider access works without opening unrelated endpoints. Microsoft-only routers such as `demo` file/resource and `protected` resource keep their router-level Microsoft guards for now.
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
- Add a LinkedIn frontend-server integration wrapper alongside `lib/server/apis/msgraph.ts`, reusing the existing `BaseAPI` pattern. Use the LinkedIn access token for `GET https://api.linkedin.com/v2/userinfo` to retrieve the signed-in member's display name and picture. Request `openid profile`; add `email` only if an actual feature needs it. Check the returned `sub` matches the validated identity-token subject before associating profile data. The identity token remains the backend authentication credential.
- Keep UserInfo and Graph response data only in transient server/client memory for processing and display. Do not cache names, emails, picture URLs, downloaded pictures, avatar data, or derived copies in Redis, databases, files, logs, browser storage, or other application-controlled persistence. Use non-caching fetch/response behavior and do not serialize these fields into persisted sessions. Profile retrieval failure must not attach another identity or turn an otherwise valid login into an anonymous user.
- Remove the existing callback's write of the Microsoft Graph `/me` response to Redis `$.microsoftProfile`, and adapt consumers to transient retrieval/display. Audit the affected Graph/LinkedIn wrappers, layouts, session restoration, logging, and client storage for other copies. Existing persistence is a known incompatibility to correct during implementation, not an exception to the global rule. Do not perform live cache/database deletion as part of documenting this plan; identify any necessary cleanup for the implementation rollout.
- UserInfo retrieves the member represented by its access token, not arbitrary members by subject. General retrieval of other LinkedIn members is outside the basic sign-in integration and requires separately approved access. Displaying another user's profile within this application from data that member explicitly shares is a separate feature requiring application visibility rules and review of applicable provider terms; it is not authorized merely by knowing their `sub`, and it must obey the same memory-only rule for third-party resource data.
- Reuse `locals.sessionData`, session status and `/user/me`. Adapt Microsoft-specific profile display and route protection without fabricating Microsoft profiles.
- Bind and consume login/link state securely, rotate/complete sessions, allowlist return destinations, and preserve embed/session restoration.
- Add visible reauthentication and socket reconnect/resubscribe behavior on expiry. Logout removes application session/references; do not blindly delete account-wide caches used by other sessions.
- Extend existing configuration/example environment and synthetic test fixtures. Unconfigured LinkedIn must not break imports, worker startup, or frontend builds.

Completion: a real LinkedIn login reaches an authorized request and socket connection; actual token lifetime and recovery are verified; Microsoft login/logout still work. Live verification requires developer-app configuration; mocked tests do not.

### D. Resource/event policies and answer ownership

Files: matrix endpoints/namespaces, `core/fastapi.py`.

- Make no changes to the inner authorization layer (`crud/base.py`, `crud/access.py`, `filters_allowed()`): ownership assignment and access filtering already operate on the internal `current_user.user_id`, so admitting LinkedIn users needs no inner-layer edit.
- Apply named guard configurations and remove Azure-specific optional extraction only from the migrated endpoints; leave router-level Microsoft guards in place for Microsoft-only routers.
- Ensure authenticated creation assigns `Action.own` to the internal user, including creation under a publicly writable question. The public-creation branch must not discard valid caller identity.
- Preserve anonymous creation without a shared owner grant; update/delete remain blocked at the outer layer.
- Permit ownership-based sharing/hierarchy operations through existing access checks; retain checks on parent and child resources.
- Attribute activity to internal users consistently and preserve application-group inheritance.

Completion: owner/non-owner/anonymous request and socket tests pass for creation, reads, modification, deletion, sharing, hierarchy operations, snapshots and replay. This is the first complete participation milestone; linking is not required to release it.

### E. Linking and merge (separate plan)

First-time attachment and existing-user merge, including verified proof of control, settings-conflict resolution, atomic reassignment of identity references, and cache/socket reconciliation, are specified in the separate [account merge plan](./linkedin-azure-account-merge-plan.md). That plan is written provider-generically so further identity providers reuse the same merge operation. It depends on Stage B's identity model and Stage C's proof-of-identity interface, and is the only work that touches the inner authorization layer. Stages A–D and F do not require it.

### F. Compatible encrypted cache persistence

Files: `microsoft.ts`, frontend `cache.ts`, backend `RedisPersistence` in `security.py`, [frontend config](../../../frontend_svelte/src/lib/server/config.ts), [backend config](../../../backend/src/core/config.py), [security.tf](../../../infrastructure/security.tf), and infrastructure rotation configuration in `variables.tf`.

- Encrypt whole MSAL cache blobs: inspected adapters load/save complete documents. Decrypt before MSAL deserialization and encrypt after serialization; avoid depending on MSAL's internal credential-field schema.
- Store LinkedIn credentials in a separate Redis `linkedin:` namespace, analogous to `msal:`; partition key: `linkedin:<sub>`. The client identifier is configuration shared by the application, so it is not repeated in each key. This assumes the existing environment/cache isolation and one LinkedIn application per namespace; changing application registration requires invalidating the old provider cache. Server sessions reference the partition for frontend-server requests and backend Socket.IO token lookup. Encrypt both the identity token used for backend authentication and the access token used by the frontend server for LinkedIn UserInfo requests in this provider record. Track their expirations independently; retaining a longer-lived access token never extends identity-token validity. Retain a refresh token only if issued and needed; do not assume basic sign-in supplies one.
- Use the same configured active encryption key, Advanced Encryption Standard in Galois/Counter Mode with a 256-bit key (AES-256-GCM), versioned envelope, and previous decryption key for `linkedin:` and `msal:` records within an environment. Both frontend and backend implement the same format. Generate a fresh nonce for every encryption across both namespaces; never reuse a key/nonce pair. Bind the full cache key and purpose as associated data so ciphertext cannot be moved between providers or accounts.
- Keep the session document (`session:<id>`) as plaintext JSON so Redis JavaScript Object Notation (JSON) path operations keep reading only the requested field. Do not encrypt individual session leaves: AES-256-GCM on a few hundred bytes costs microseconds and is dominated by the Redis round trip, but plaintext leaves preserve the read-only-what-you-need benefit and avoid whole-document decrypts. Confine encryption to the standalone `msal:`/`linkedin:` credential blobs, which are already read and written whole.
- Remove `$.microsoftProfile` (the Microsoft Graph `/me` response) from the session entirely; retrieve Graph data transiently in memory for display and never cache it, applying the same rule to LinkedIn UserInfo.
- Reduce `$.microsoftAccount` to the minimal `homeAccountId` partition pointer that MSAL's `RedisPartitionManager` needs to locate the encrypted `msal:` cache; drop `username`/`name`/other account fields. Keep this pointer as plaintext permitted authentication-library metadata. Do not drop it entirely: the credential cache is partitioned by `homeAccountId`, so removing it would require re-partitioning MSAL by session identifier.
- Keep `$.status`, `$.currentUser`, `$.loggedIn`, and `$.sessionId` as plaintext JSON path reads; do not store third-party UserInfo/Graph responses or their fields in any session subdocument.
- Use the same envelope in both runtimes: `version` (envelope format), `key-version` (Key Vault secret version), `nonce` (12 random bytes), `ciphertext` (encrypted data), and `tag` (16-byte authentication tag). Encode binary fields as Base64. Version identifiers and nonces are not secrets. Generate nonces using the platform cryptographic random generator; never reuse a key/nonce pair.
- The encryption library generates the tag and must verify it before any decrypted data is consumed. It detects ciphertext tampering and incorrect keys, nonces, or associated data. The tag is mandatory, not an optional checksum or separate secret. Libraries that append it to ciphertext must split/recombine it consistently at the envelope boundary; cross-runtime tests establish compatibility. Bind envelope format/key version as well as cache key/purpose into consistently encoded associated data.
- Load the current and previous key once through startup configuration as described below. Keep keys outside Redis/PostgreSQL and browser-visible data. Missing required keys or failed tag verification must never trigger plaintext writes or acceptance of unverified plaintext.
- Preserve cache expiry and refresh-write concurrency. Partitions must not collide across providers/applications.
- Transition in order: compatible readers on all instances, encrypted writers, then retire plaintext compatibility after migration/expiry. Malformed encrypted data is never reinterpreted as legacy plaintext. Retain old read keys while their records remain.
- Rollback after encrypted writes requires compatible readers, or deliberate authentication-cache invalidation and fresh login. Do not roll back by persisting decrypted tokens.
- Benchmark synthetic representative payloads in the test environment, including serialization, Redis round trips and tail latency. No deployment-specific encryption latency has been measured yet.

#### Key generation and startup configuration

- Generate a cryptographically random 32-byte symmetric key in `infrastructure/security.tf` and store its Base64 representation as the Key Vault **secret** `auth-cache-encryption-key`. The same key encrypts and decrypts. Share it between the frontend server and backend for permitted authentication-cache data within one environment; keep separate keys for development, testing, staging, and production and for unrelated future encryption/signing purposes.
- OpenTofu owns rotation. An explicit non-secret rotation revision changes the generated key; unrelated infrastructure updates preserve it. Update the value under the same secret name so previous secret versions remain available. Do not delete/recreate the secret to rotate it. Generated secrets can appear in infrastructure state and saved plans; protect those artifacts and do not print secret values.
- Give only the frontend/backend application identities the additional secret `List` permission required for this feature, alongside their existing `Get`; leave other identities unchanged. These two permission additions are recorded in `security.tf`; they are not deployed by this documentation update. Under the existing vault access policies, `List` exposes vault-wide secret metadata, not secret values by itself.
- At startup, fetch the latest secret, enumerate all pages of version metadata, and determine the immediately preceding version by creation time. Do not rely on listing order or sort opaque version identifiers. Fetch the previous value using its exact version. If creation times cannot establish a unique predecessor, fail with a configuration error rather than guess. Rotation must not run concurrently with startup discovery; detect a changed latest version and retry the snapshot if necessary.
- Keep `encryption_key`, `previous_encryption_key`, and their version identifiers in memory, following each application's field-naming conventions. Versions come from Key Vault metadata; they require no additional Key Vault secrets or deployment environment variables. `config.ts` uses `getSecret` and `listPropertiesOfSecretVersions`; `config.py` uses `get_secret` and `list_properties_of_secret_versions`. Reuse a client within the loading operation.
- The first generation has no previous key: use `undefined`/`None`. A permission, network, disabled-version, or malformed-key error is not equivalent to an absent predecessor. Validate decoded key lengths and fail configuration loading if required material cannot be loaded; do not copy the backend `get_variable()` helper's catch-all empty-string fallback for encryption keys. Do not skip an unavailable immediate predecessor and silently choose an older version.
- Local development/test configuration supplies current/optional previous keys and matching non-secret version labels through the existing environment-variable setup, using only synthetic keys in fixtures. No new scripts or workflows are required. Keep configuration initialization compatible with frontend builds and backend test/worker imports.
- New records use the current key. Readers select the in-memory key by the record's `key-version`; unknown versions produce a controlled cache/authentication failure, never an arbitrary on-demand Key Vault lookup. Redis versions select keys during reads; `List` separately discovers the predecessor at startup. There are no Key Vault requests per cache operation.

#### Routine rotation and deployment

- Use the existing infrastructure-success triggers for the frontend/backend deployment workflows. For production rotation, approve and complete the backend deployment before approving the frontend deployment. When adding the secret-generation resource, put this reminder beside it in `security.tf`.
- The user accepts temporary authentication failures, including affected existing sessions, while old and new processes overlap. Backend-first ordering reduces some incompatibilities but does not make rotation atomic: a new backend can write records the old frontend cannot decrypt. Applications must recover through normal cache/authentication failure handling; never bypass verification. A separate preparation deployment for zero interruption is not required.
- Keep the previous version enabled and readable until every record encrypted with it has expired or been re-encrypted. Retaining a current and previous key only works if another rotation does not strand records from two generations earlier. Count retention from the last write by an old process, including remaining replicas, and account for session metadata as well as provider-cache expiry. Do not rotate again before that boundary unless deliberately accepting cache invalidation and fresh login.
- Secret changes do not update keys already in process memory; both application deployments must complete to adopt them. Rolling back to processes that loaded only older keys can require deliberate authentication-cache invalidation. This routine key rotation is separate from the initial plaintext-to-encrypted format migration, which still requires compatible readers before encrypted writers.

Completion: cross-runtime writes/reads, tamper/wrong-key rejection, JSON path behavior, expiry and transition tests pass; permitted credentials/authentication metadata are encrypted, and third-party resource response data is absent from persisted records.

## 6. Validation and rollout

Use only the test environment for formatting, linting, type checks, tests and benchmarks. Follow [backend guidance](../../../backend/AGENTS.md), [frontend guidance](../../../frontend_svelte/AGENTS.md), and existing [backend](../../../.github/workflows/backendAPI.yml) / [frontend](../../../.github/workflows/frontend_svelte.yml) continuous-integration workflows. Do not introduce alternate scripts. Report validation summaries in the called tools' format and distinguish baseline failures.

Extend these suites:

- Encryption/configuration tests in both runtimes: first generation, unsorted/paginated version discovery, ambiguous predecessor, startup rotation race, missing permissions, unavailable previous versions, malformed keys, current/previous reads, unknown key version, and modified nonce/ciphertext/tag/associated data. Verify tag failures expose no plaintext, and loading performs no per-cache-operation Key Vault calls.
- [Security](../../../backend/src/core/tests/test_security.py) and [types](../../../backend/src/core/tests/test_types.py): dispatch, claims, policy alternatives, optional compatibility, cached tokens, administrator/tenant isolation.
- [Base CRUD](../../../backend/src/crud/tests/test_base_crud.py) and [access CRUD](../../../backend/src/crud/tests/test_access_crud.py): ownership, inheritance, strongest grants and non-owner denial. Add adjacent identity CRUD tests for merge transactions as needed.
- [Identity routes](../../../backend/src/routers/api/v1/tests/test_identities.py), [quiz routes](../../../backend/src/routers/api/v1/tests/test_quiz.py), [presentation routes](../../../backend/src/routers/api/v1/tests/test_presentation.py), [access routes](../../../backend/src/routers/api/v1/tests/test_access.py): full matrix, enclosing dependencies and forbidden provider-field updates.
- [Socket suites](../../../backend/src/routers/socketio/v1/tests/): providers, expiry, reconnect, mutation authorization, link/unlink aliases, subscription/replay isolation and merge invalidation.
- [Backend wrapper](../../../frontend_svelte/src/lib/server/apis/backendApi.test.ts), [socket client](../../../frontend_svelte/src/lib/socketio.svelte.test.ts), and adjacent provider/cache/component tests: selection, state/nonce, login versus link, conflict choices, recovery, UserInfo subject matching, memory-only profile display, missing pictures/profile-service failures, independent token expirations, and cross-runtime encryption using synthetic fixtures. Add regression coverage proving that UserInfo and Graph responses/derived profile fields never reach Redis, database writes, persisted sessions, browser storage, or logs, while authentication tokens and necessary authentication metadata remain cacheable.

Rollout:

1. Add identity migration and compatible guard/cache readers; keep LinkedIn disabled until configuration and tests are ready.
2. Enable LinkedIn login and selected endpoint/event alternatives after A–D pass; verify actual token lifetime and recovery.
3. Enable linking/confirmed merge after atomicity and stale-authorization tests pass; see the [account merge plan](./linkedin-azure-account-merge-plan.md).
4. Enable encrypted writes only after every reader is compatible; F can ship earlier if that condition is satisfied.
5. Verify staging before production using existing branches/environments. Disabling LinkedIn admission is reversible. A completed merge is deliberately destructive and has no application merge history from which to undo it. A migration downgrade must not silently discard populated provider identifiers.

## 7. Sequencing, handoffs, and tracking

Main chain: **A → B → C → D**, with tests in each stage. **F** can run alongside B–D after agreeing on cache format, partitioning, configuration and transition. Linking and merge move to the separate [account merge plan](./linkedin-azure-account-merge-plan.md).

Keep authentication, guards and socket integration together: they share `security.py`, `types.py`, and the namespace base. Encryption is a suitable separate task once its contract is fixed. Merge work (separate plan) can be handed off after B and C's proof-of-identity interface are stable. Separate work uses isolated branches/worktrees and coordinates shared-file edits; do not run independent chats concurrently in this checkout.

No additional endpoint-policy decision is required to begin. Live verification needs provider application configuration, encryption needs startup key configuration, and actual identity-token lifetime must be measured before accepting the login experience. Do not paste real tokens or secrets into documentation or chat.

- [ ] A: policy and validation contract
- [ ] B: minimal identity/signup and migrations
- [ ] C: login, cache lookup, request integration and expiry
- [ ] D: endpoint/event matrix and ownership
- [ ] E: linking, merge preview, atomic reassignment and cleanup — see [account merge plan](./linkedin-azure-account-merge-plan.md)
- [ ] F: encrypted cache compatibility and rollout
- [ ] Test-environment validation and staging verification

## References

- [LinkedIn OpenID Connect](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2): identity claims, issuer, pairwise subjects and public verification keys; no fixed identity-token lifetime is assumed.
- [OpenID Connect identity-token validation](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation): issuer, audience, signature, time and nonce rules.
- [openid-client version 6.8.8](https://github.com/panva/openid-client/tree/v6.8.8): use the installed major version's interface.
- [MSAL Node cache guidance](https://learn.microsoft.com/en-us/entra/msal/javascript/node/caching): distributed persistence and encryption responsibilities.
- [LinkedIn Profile API restrictions](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api): other-member profile lookup requires separately approved access; it is not a UserInfo feature.
- [Authenticated encryption](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM): nonce requirements, authentication tags, and rejection of modified ciphertext.
- [Key Vault JavaScript secret versions](https://learn.microsoft.com/en-us/azure/key-vault/secrets/javascript-developer-guide-get-secret) and [Python SecretClient](https://learn.microsoft.com/en-us/python/api/azure-keyvault-secrets/azure.keyvault.secrets.secretclient?view=azure-python): version-specific retrieval and metadata listing permissions.
