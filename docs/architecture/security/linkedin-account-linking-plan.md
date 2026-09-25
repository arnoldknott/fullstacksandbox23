# LinkedIn authentication, account linking, and credential encryption

Status: Stages A (guards), B (minimal identity/signup), and D (resource/event policies and answer ownership) are implemented. Stage C lifecycle code, focused automated coverage, deployment configuration, and the live LinkedIn expiry/reconnect sequence are verified; the measured LinkedIn identity-token lifetime is one hour. Equivalent Microsoft live acceptance remains tracked in the [authentication session lifecycle plan](authentication-session-lifecycle-plan.md). Account linking/merge and cache encryption remain subsequent stages.

Agreed scope recorded on 2026-09-20; encryption and rotation decisions updated on 2026-09-21. This is the shared implementation handoff for frontend, backend, database, and Redis changes. Keep shared login/encryption decisions here and account-merge decisions in the linked merge plan, rather than maintaining separate plans in each application.

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
- Apply the [data-storage policy](README.md#data-storage-policy) and [Redis encryption contract](../../redis/README.md); Stage F maps them to implementation.
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

Follow the [security definitions and change boundary](../../../AGENTS.md#security-layers-and-change-boundaries) and [architecture guidance](README.md#architecture-and-change-boundary). This stage changes outer admission; it preserves inner access enforcement.

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
- Validate callback state against a short-lived login transaction. Bind provider, login/link intent, initiating user, exact redirect URI, and allowed return destination. LinkedIn does not advertise or return the OpenID Connect nonce claim, so this provider flow does not request or validate one. LinkedIn login uses the member-authorized 3-legged OAuth authorization-code flow. During the code-to-token exchange, the frontend server sends the client ID and client secret in the request body as required by LinkedIn; the grant type remains authorization_code. LinkedIn's separately enabled native-client Proof Key for Code Exchange (PKCE) flow is outside this implementation.
- This identity token authenticates within this application's configured login-client/backend trust boundary. It contains no LinkedIn-issued resource permissions for our backend; guards and access policies supply those decisions.
- No UserInfo call is needed merely to obtain the validated subject. No email/profile persistence is necessary for identity mapping.
- Cached token/key lookup never extends token validity. Check expiry for requests and authorized socket operations, subscriptions and replay. End protected room access on expiry and require valid authentication before resubscribing.
- Live verification measured `exp - iat` as 3,600 seconds for the LinkedIn identity token. The returned access token had an approximately 60-day lifetime, and the observed response contained no refresh token. These token lifetimes are independent: the identity token remains the backend credential and reauthentication is the recovery path when it expires. Never accept an expired identity token or substitute the LinkedIn access token as backend authentication.

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

### A. Policy types, provider dispatch, and guard migration

Files: `core/types.py`, `core/security.py`, request `BaseView`, socket `BaseNamespace`.

- Implement provider alternatives, callable `Guards`, and shared evaluation with a minimal verified-provider/claims context.
- Migrate all application guard declarations together. Do not retain old keyword constructors or implicit `guards=None` policies. Empty policies and missing event declarations fail closed; anonymous admission requires `AllowAnonymous()` explicitly.
- Separate policy configuration from validation and user lookup; keep current endpoint layering.
- Add mocked tests before enabling LinkedIn: provider selection, wrong issuer/audience/signature, expiry, exact scope membership, roles/groups, anonymous compatibility and socket cache lookup.

Completion: existing Microsoft/anonymous tests pass and both transports evaluate the new representation. LinkedIn database signup is not yet required.

Implementation notes:

- The `authentication/` package contains identity-provider token validation helpers in `azure.py` and `linkedin.py`, with shared issuer dispatch and public-key caching in `base.py`. `security.py` owns provider requirement checks, guard evaluation, and internal user resolution. Guard evaluation returns `GuardOutcome.AUTHENTICATED` or `GuardOutcome.ANONYMOUS` on admission and raises on rejection; it never uses `False` to mean successful anonymous admission.
- Endpoint dependencies inline single-alternative policies, for example `Depends(Guards(MicrosoftGuard(scopes=["api.write"], roles=["User"])))`. Multiple-alternative policies may use named declarations. Both return `GuardTypes` configuration. Router-wide dependencies use the same policy's `check_http` method to enforce admission without database user resolution.
- Socket event declarations use `Guards(...)()` for the same configuration. Read, subscribe, and replay reuse the connect policy; link/unlink retain the documented submit aliases.
- Missing/invalid credentials require an explicit anonymous alternative. Verified identities failing provider requirements never fall back to anonymous.
- Provider dispatch and LinkedIn signature/claim validation have synthetic signed-token tests. Runtime extraction still uses Microsoft until Stages B–C connect provider signup and frontend acquisition; no live endpoint enables LinkedIn yet.
- Validation in the test Docker Compose stack: the combined security, REST, and Socket.IO run recorded `894 passed, 4 failed, 2 deselected`; the four failures were corrected and the targeted rerun recorded `4 passed`. Two live Microsoft key-fetch tests were excluded. Ruff and production-code Pyright checks passed. Missing/invalid bearer credentials now consistently use the `Invalid token.` error detail with status 401 on protected routes.


### B. Minimal user identity and signup

Files: `models/identity.py`, `crud/identity.py`, frontend identity types, [development migrations](../../../backend/src/migrations/dev/) and [stage/production migrations](../../../backend/src/migrations/stage_prod/).

- Add a nullable unique case-sensitive string `linkedin_user_id`, allowing multiple nulls. Preserve subject case/content rather than treating it as an email or universally unique identifier.
- Ensure LinkedIn-only users do not acquire an Azure tenant solely through `UserCreate`'s current default. Existing Microsoft users remain unchanged.
- Implement `linkedin_user_self_sign_up`; reuse internal user/account/profile/identifier creation where appropriate. Never invoke Azure group synchronization for LinkedIn.
- Resolve Microsoft identities against the validated configured tenant and object identifier; do not reinterpret its object identifier as an OpenID subject.
- Allow administrators to assign provider identifiers when creating users through guarded REST or Socket.IO interfaces. Exclude provider-identifier reassignment from ordinary user/profile updates; verified signup and linking remain the other permitted identity paths.
- Handle concurrent signup and unique conflicts without duplicates or orphan settings records. Preserve deliberate disabled-user semantics.
- Follow each migration tree's actual current head and existing environment workflow, rather than assuming one revision can attach to both histories.

Completion: both providers resolve internal users, signup creates expected settings/self-ownership, and Microsoft data migrates unchanged.

Implementation notes:

- `User.linkedin_user_id` has a unique index with PostgreSQL `C` collation. No provider profile data is stored. Admin create schemas accept provider identifiers. User/profile update schemas exclude provider identifiers from database updates; `UserUpdate.id` remains a REST/Socket.IO resource selector excluded from database updates.
- `UserCRUD._provider_sign_up()` serializes signup for each provider identifier with a transaction-scoped PostgreSQL advisory lock. Helpers run in a savepoint-bound session, so their internal commits cannot leave partial users, settings, policies, or logs if signup fails. Existing inner access-control helpers are unchanged.
- Microsoft signup still synchronizes Azure groups; LinkedIn signup never does. `check_token_against_guards()` resolves a verified LinkedIn subject with empty Azure roles/groups. Runtime transport extraction remains Microsoft-only until Stage C.
- Inactive initialized users stay disabled. An inactive Microsoft invitation with neither account nor profile settings is initialized on its first verified login; a legacy invitation with no tenant adopts the verified tenant. A conflicting stored tenant is rejected.
- Local development revision `b19e08c4f126` follows this workspace's `e2c3b40e9e73`; development revisions remain gitignored. The pipeline generates the stage/production revision from model metadata; no manual stage/production revision is needed for this column/index addition. Follow the [PostgreSQL migration workflow](../../postgres/README.md#schema-migration-workflow). Fresh checkouts generate their own development revisions from model metadata.
- Regression coverage includes provider isolation, concurrent signup, rollback after helper commits, disabled users, invitation activation, HTTP/Socket.IO input boundaries, and database identifier constraints. Migration validation follows the existing PostgreSQL workflow without a dedicated test for each generated revision. The frontend skips Microsoft Graph lookup for users without an Azure identifier.

### C. Frontend login, credential selection, and expiry

Files: provider modules, login/callback/logout routes, `backendApi.ts`, session types/hooks/layouts, configuration loaders.

- Implement prepared `linkedin.ts` with the installed version 6 interface and existing route scaffolding. Register the actual callback addresses. First-party parameters use kebab-case; external protocol parameters remain unchanged.
- During Stage C, `linkedin:<sub>` temporarily follows the existing plaintext `msal:<homeAccountId>` cache posture. This is an explicit interim implementation decision; Stage F must encrypt both complete provider-cache values before encrypted-cache rollout is complete.
- Keep credentials server-side and separate from client session/layout data. Store active provider and private cache references in the server session.
- Select the active provider's credential for backend requests and socket cache lookup. Linking must not silently switch active identity or union cached claims.
- Keep Graph acquisition separate: LinkedIn-only login must not run unconditional Microsoft Graph `/me`, Microsoft silent acquisition, or Microsoft logout redirects.
- Add a LinkedIn frontend-server integration wrapper alongside `lib/server/apis/msgraph.ts`, reusing the existing `BaseAPI` pattern. Use the LinkedIn access token for `GET https://api.linkedin.com/v2/userinfo` to retrieve the signed-in member's display name and picture. Request `openid profile`; add `email` only if an actual feature needs it. Check the returned `sub` matches the validated identity-token subject before associating profile data. The identity token remains the backend authentication credential.
- Apply the [transient resource-data policy](README.md#data-storage-policy) to the wrappers and consumers. Profile retrieval failure must not attach another identity or turn an otherwise valid login into an anonymous user.
- Remove the existing callback's write of the Microsoft Graph `/me` response to Redis `$.microsoftProfile`, and adapt consumers to transient retrieval/display. Audit the affected Graph/LinkedIn wrappers, layouts, session restoration, logging, and client storage for other copies. Existing persistence is a known incompatibility to correct during implementation, not an exception to the global rule. Do not perform live cache/database deletion as part of documenting this plan; identify any necessary cleanup for the implementation rollout.
- UserInfo retrieves the member represented by its access token, not arbitrary members by subject. General retrieval of other LinkedIn members is outside the basic sign-in integration and requires separately approved access. Displaying another user's profile within this application from data that member explicitly shares is a separate feature requiring application visibility rules and review of applicable provider terms; it is not authorized merely by knowing their `sub`, and it must obey the same memory-only rule for third-party resource data.
- Reuse `locals.sessionData`, session status and `/user/me`. Adapt Microsoft-specific profile display and route protection without fabricating Microsoft profiles.
- Bind and consume login/link state securely, rotate/complete sessions, allowlist return destinations, and preserve embed/session restoration.
- Add visible reauthentication and socket reconnect/resubscribe behavior on expiry. Logout removes application session/references; do not blindly delete account-wide caches used by other sessions.
- Use a sliding application-session lifetime. After a valid normal page request or successfully authenticated Socket.IO event, renew the Redis expiry to `session_timeout` only when the remaining lifetime is less than half of `session_timeout`. A normal page request renews the existing `session_id` cookie at the same time. Socket.IO can renew Redis but cannot renew the HTTP-only cookie, so long-lived socket-only activity also needs a throttled same-origin session touch before the cookie expires.
- Create a new ten-minute pending session only for an initial unauthenticated login. Reauthentication and provider linking from an authenticated session retain that established `session_id`; keep their short-lived OAuth transaction separate so it neither changes the established session status nor shortens its lifetime. Remove a superseded session after intentional rotation or consolidation instead of leaving duplicate authenticated sessions until expiry.
- Implement and validate those renewal, reauthentication, established-socket expiry, compact status, and reconnect details through the [authentication session lifecycle plan](authentication-session-lifecycle-plan.md). This document retains their Stage C acceptance dependency without duplicating the transport design.
- Extend existing configuration/example environment and synthetic test fixtures. LinkedIn configuration is part of every environment, while configuration field types and initialization continue following the existing Microsoft patterns.


Implementation notes:

- Provider routes are `/login/microsoft`, `/logout/microsoft`, `/login/linkedin`, `/logout/linkedin`, and `/oauth/callback/linkedin`; the existing Microsoft callback remains `/oauth/callback`. The generic `/login` route redirects server-side to `/login/microsoft`, whose page performs the OAuth navigation client-side and targets the top-level window when embedded; the LinkedIn provider route uses the same client-side top-window behavior. Navbar and sidebar controls retain Microsoft as their provider. `/oauth/providers` offers both providers only as a hidden debugging page; normal login and reauthentication flows do not redirect users there.
- Login entry parameters are target-url and parent-url. LinkedIn callback state binds the server session, exact redirect URI, state, and return values. The one-time authorization transaction is removed after a successful code exchange, and the application session becomes logged in only after /user/me succeeds.
- Backend requests select the active provider from the server-side session. Microsoft sends its backend access token; LinkedIn sends its identity token. LinkedIn UserInfo uses only the LinkedIn access token and is fetched into memory for the current response without profile persistence.
- The protected `/identities/linkedin` page provides a deliberately simple diagnostic view comparable to the Microsoft Graph identity page. It reads the inherited root-layout session data directly and displays the signed-in member's transient `/v2/userinfo` name, picture and response. It performs no additional request or persistence.
- The navbar avatar reuses the root layout profile data: Microsoft sessions use the proxied Graph photo, LinkedIn sessions fall back to the transient UserInfo `picture`, and sessions without either render the generic user icon. The LinkedIn picture URL is not persisted.
- The Key Vault secrets are linkedin-client-id and linkedin-client-secret. OpenTofu creates both from the corresponding required GitHub/environment inputs LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET. Each LinkedIn application registration must allow the exact frontend callback URL <frontend-origin>/oauth/callback/linkedin.
- The observed LinkedIn response did not include a refresh token. If reauthentication is required while session data remains available, the frontend derives the provider from the active provider and linked identities, with Microsoft taking precedence. Socket.IO and server-rendered redirects preserve target-url. No additional provider cookie or browser storage is used; after a full reload with an expired application session, Microsoft is the fallback. Live testing must still verify Socket.IO reconnect/resubscribe behavior.

Completion: a real LinkedIn login reaches an authorized request and socket connection; identity-token lifetime, sliding application-session renewal, one-session reauthentication, expiry recovery, and transient UserInfo display are verified; Microsoft login/logout still work. Live verification requires developer-app configuration; mocked tests do not.

### D. Resource/event policies and answer ownership

Files: matrix endpoints/namespaces, `core/fastapi.py`.

- Verify existing ownership and filtering behavior against the matrix under the [inner-layer change boundary](../../../AGENTS.md#security-layers-and-change-boundaries).
- Extend the named guard configurations with LinkedIn according to the matrix; retain router-level Microsoft guards on Microsoft-only routers. Stage A already replaces optional-token admission with explicit `AllowAnonymous()` policies.
- Ensure authenticated creation assigns `Action.own` to the internal user, including creation under a publicly writable question. The public-creation branch must not discard valid caller identity.
- Preserve anonymous creation without a shared owner grant; update/delete remain blocked at the outer layer.
- Permit ownership-based sharing/hierarchy operations through existing access checks; retain checks on parent and child resources.
- Attribute activity to internal users consistently and preserve application-group inheritance.

Implementation notes:

- Request guards admit LinkedIn for the documented quiz answer operations, question reads, presentation reads, and access-policy/right/hierarchy routes. Question and presentation mutations, group administration, demo resources/files, and protected resources retain their Microsoft-only outer policies.
- Socket.IO connect/read/subscription/replay policies admit LinkedIn on question, presentation, message, and numerical namespaces. Message and numerical creation, update, delete, share, and the existing link/unlink guard aliases admit LinkedIn; question and presentation mutations remain Microsoft-only.
- Existing CRUD access-policy enforcement remains unchanged. Focused request tests verify that a LinkedIn caller owns an answer created under a publicly connectable question and can read/update/delete it through the public interfaces. Focused socket tests exercise LinkedIn creation, update, deletion, and sharing through the provider-specific Redis session/cache path.
- Test-environment validation recorded `4 passed` for the focused request matrix, `26 passed` for focused Socket.IO coverage, and `1065 passed, 3 failed` for the full backend suite. The three failures were stale session-lifecycle exception assertions; after aligning them with the typed authentication/authorization errors, their targeted rerun recorded `3 passed`. Black and Ruff pass.

Completion: owner/non-owner/anonymous request and socket tests pass for creation, reads, modification, deletion, sharing, hierarchy operations, snapshots and replay. This is the first complete participation milestone; linking is not required to release it.

### E. Linking and merge (separate plan)

First-time attachment and existing-user merge, including verified proof of control, settings-conflict resolution, atomic reassignment of identity references, and cache/socket reconciliation, are specified in the separate [account merge plan](./linkedin-azure-account-merge-plan.md). That plan is written provider-generically so further identity providers reuse the same merge operation. It depends on Stage B's identity model and Stage C's proof-of-identity interface, and is the only work that touches the inner authorization layer. Stages A–D and F do not require it.

### F. Compatible encrypted cache persistence

Contract: [Redis encryption, partitioning, startup keys, rotation, and performance requirements](../../redis/README.md). That document is authoritative for cache design; this stage tracks the implementation.

Files: `microsoft.ts`, frontend `cache.ts`, backend `RedisPersistence` in `security.py`, [frontend config](../../../frontend_svelte/src/lib/server/config.ts), [backend config](../../../backend/src/core/config.py), [security.tf](../../../infrastructure/security.tf), and infrastructure rotation configuration in `variables.tf`.

- Implement the shared encryption envelope and provider-cache adapters in both runtimes.
- Adapt session path/whole-session readers and writers, including backend direct Redis consumers, while preserving the account fields required by existing MSAL token retrieval.
- Implement startup key loading, per-environment generation, and explicit rotation configuration using the existing configuration/deployment surfaces. Put the backend-first deployment reminder beside the secret-generation resource.
- Add compatible migration readers before encrypted writers, preserving expiry and concurrent-write behavior.
- Run cross-runtime, tamper, account-lookup, and JSON path tests. Perform and report the [required benchmarks](../../redis/README.md#performance-measurement).

Completion: the Redis contract is implemented and validated, including encrypted credentials and protected user data, the explicit plaintext-identifier exceptions, and absence of prohibited third-party resource data. Key generation and application changes remain planned until implemented.

## 6. Validation and rollout

Use only the test environment for formatting, linting, type checks, tests and benchmarks. Follow [backend guidance](../../../backend/AGENTS.md), [frontend guidance](../../../frontend_svelte/AGENTS.md), and existing [backend](../../../.github/workflows/backendAPI.yml) / [frontend](../../../.github/workflows/frontend_svelte.yml) continuous-integration workflows. Do not introduce alternate scripts. Report validation summaries in the called tools' format and distinguish baseline failures.

Extend these suites:

- Encryption/configuration tests in both runtimes: first generation, unsorted/paginated version discovery, ambiguous predecessor, startup rotation race, missing permissions, unavailable previous versions, malformed keys, current/previous reads, unknown key version, and modified nonce/ciphertext/tag/associated data. Verify tag failures expose no plaintext, and loading performs no per-cache-operation Key Vault calls. Cover encrypted `$.microsoftAccount` compatibility with existing frontend/backend token acquisition, encrypted user data, whole-session and selective/deeper-path access, and absence of plaintext duplicates.
- [Security](../../../backend/src/core/tests/test_security.py) and [types](../../../backend/src/core/tests/test_types.py): dispatch, claims, policy alternatives, optional compatibility, cached tokens, administrator/tenant isolation.
- [Base CRUD](../../../backend/src/crud/tests/test_base_crud.py) and [access CRUD](../../../backend/src/crud/tests/test_access_crud.py): ownership, inheritance, strongest grants and non-owner denial. Add adjacent identity CRUD tests for merge transactions as needed.
- [Identity routes](../../../backend/src/routers/api/v1/tests/test_identities.py), [quiz routes](../../../backend/src/routers/api/v1/tests/test_quiz.py), [presentation routes](../../../backend/src/routers/api/v1/tests/test_presentation.py), [access routes](../../../backend/src/routers/api/v1/tests/test_access.py): full matrix, enclosing dependencies and forbidden provider-field updates.
- [Socket suites](../../../backend/src/routers/socketio/v1/tests/): providers, expiry, reconnect, mutation authorization, link/unlink aliases, subscription/replay isolation and merge invalidation.
- [Backend wrapper](../../../frontend_svelte/src/lib/server/apis/backendApi.test.ts), [socket client](../../../frontend_svelte/src/lib/socketio.svelte.test.ts), and adjacent provider/cache/component tests: selection, callback state and redirect binding, login versus link, conflict choices, recovery, UserInfo subject matching, memory-only profile display, missing pictures/profile-service failures, independent token expirations, and cross-runtime encryption using synthetic fixtures. Add regression coverage proving that UserInfo and Graph responses/derived profile fields never reach Redis, database writes, persisted sessions, browser storage, or logs, while authentication tokens and necessary authentication metadata remain cacheable.

Rollout:

1. Add identity migration and compatible guard/cache readers; require LinkedIn configuration in every environment before deploying the provider integration.
2. Enable LinkedIn login and selected endpoint/event alternatives after A–D pass; verify expiry recovery and Socket.IO reconnect/resubscribe behavior.
3. Enable linking/confirmed merge after atomicity and stale-authorization tests pass; see the [account merge plan](./linkedin-azure-account-merge-plan.md).
4. Enable encrypted writes only after every reader is compatible; F can ship earlier if that condition is satisfied.
5. Verify staging before production using existing branches/environments. Disabling LinkedIn admission is reversible. A completed merge is deliberately destructive and has no application merge history from which to undo it. A migration downgrade must not silently discard populated provider identifiers.

## 7. Sequencing, handoffs, and tracking

Main chain: **A → B → C → D**, with tests in each stage. **F** can run alongside B–D after agreeing on cache format, partitioning, configuration and transition. Linking and merge move to the separate [account merge plan](./linkedin-azure-account-merge-plan.md).

Keep authentication, guards and socket integration together: they share `security.py`, `types.py`, and the namespace base. Encryption is a suitable separate task once its contract is fixed. Merge work (separate plan) can be handed off after B and C's proof-of-identity interface are stable. Separate work uses isolated branches/worktrees and coordinates shared-file edits; do not run independent chats concurrently in this checkout.

No additional design decision is required to continue. The identifier-storage decision is recorded in the [Redis contract](../../redis/README.md#encryption-scope). Sliding-session, socket-expiry, and independently expiring intent-bound OAuth transaction code are implemented with focused automated coverage; live expiry/reconnect acceptance still remains. Encryption needs startup key configuration. Do not paste real tokens or secrets into documentation or chat.

- [x] A: policy and validation contract
- [x] B: minimal identity/signup and migrations
- [ ] C: login, cache lookup, request integration and expiry (code, focused automated coverage, and live LinkedIn expiry/reconnect verified; equivalent Microsoft live acceptance pending)
- [x] D: endpoint/event matrix and ownership
- [ ] E: linking, merge preview, atomic reassignment and cleanup — see [account merge plan](./linkedin-azure-account-merge-plan.md)
- [ ] F: encrypted cache compatibility and rollout
- [ ] Test-environment validation and staging verification

## References

- [LinkedIn OpenID Connect](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2): identity claims, issuer, pairwise subjects and public verification keys. The provider documentation does not promise a fixed identity-token lifetime; the current live result is recorded above.
- [OpenID Connect identity-token validation](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation): issuer, audience, signature, time and nonce rules.
- [openid-client version 6.8.8](https://github.com/panva/openid-client/tree/v6.8.8): use the installed major version's interface.
- [MSAL Node cache guidance](https://learn.microsoft.com/en-us/entra/msal/javascript/node/caching): distributed persistence and encryption responsibilities.
- [LinkedIn Profile API restrictions](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api): other-member profile lookup requires separately approved access; it is not a UserInfo feature.
