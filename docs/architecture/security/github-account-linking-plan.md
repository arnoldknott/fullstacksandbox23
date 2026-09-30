# GitHub authentication and account linking

Add GitHub as a third linkable identity provider alongside Microsoft and LinkedIn. Each REST request or Socket.IO event still selects one independently verified linked-provider identity through its declared guard order; provider claims are never combined, and inner access-control semantics remain unchanged. This plan follows the same contract as [LinkedIn account linking](linkedin-account-linking-plan.md) and the [multi-provider session authorization](multi-provider-session-authorization.md) transport contract. Where GitHub behaves like LinkedIn, reuse the existing provider-neutral machinery; where GitHub diverges, this document calls it out explicitly.

## Decisions still needed from the maintainer

These choices change how the stages below are implemented. They are intentionally left open, and each affected step is annotated inline with **⚠️ INPUT NEEDED (Decision N)**. Nothing here blocks laying out the code structure, but the marked steps cannot be finalized until they are answered.

1. **App type.** GitHub OAuth App (opaque, non-expiring access tokens; simplest, closest to LinkedIn) versus GitHub App (expiring user-to-server tokens with refresh tokens). This plan is written assuming an OAuth App.
2. **Token validation method.** Token introspection (`POST /applications/{client_id}/token`, confirms the token was issued to this application and returns its scopes) versus a plain `GET /user` call. This plan assumes introspection.
3. **Change boundary confirmation.** Adding a provider self-signup is an outer-layer change and preserves inner access control, but per the [change boundary](../../../AGENTS.md#security-layers-and-change-boundaries) it should be confirmed before execution.
4. **Per-request GitHub session model.** GitHub has no re-validatable JWT, so a session cannot cheaply re-verify a GitHub credential on every request the way Microsoft and LinkedIn do. Either (a) store the validated GitHub subject in the session and trust it until the next login/reauthentication (validate at login/link only; revocation takes effect at next login), (b) re-validate against the GitHub API per request (rejected: network cost and rate limits), or (c) cache an introspection result with a short time-to-live. This plan assumes option (a).

## Why GitHub is different from the existing providers

The current outer layer assumes every provider credential is a signed JSON Web Token (JWT) that can be validated offline against a published JSON Web Key Set (JWKS). Microsoft issues signed access tokens and LinkedIn issues a signed OpenID Connect identity token; both are validated through cached JWKS in [`core/authentication/base.py`](../../../backend/src/core/authentication/base.py) and dispatched by their unverified `iss` claim. GitHub breaks this assumption:

1. **Opaque tokens, not JWTs.** GitHub OAuth Apps issue opaque access tokens (for example `gho_…`). There is no identity token and no JWKS for OAuth Apps. The shared dispatch decodes the token with `jwt.decode(token, options={"verify_signature": False})` to read `iss`; an opaque GitHub token raises a `PyJWTError` and is rejected before any GitHub-specific code runs. **The issuer-based dispatch model cannot validate a GitHub token.** GitHub needs a separate, non-JWT validation path.
2. **Identity is established by a network call, not a signature.** GitHub identity is resolved by calling the GitHub Application Programming Interface (API): either token introspection (`POST https://api.github.com/applications/{client_id}/token` with Hypertext Transfer Protocol (HTTP) Basic `client_id:client_secret` and the access token in the body) or `GET https://api.github.com/user`. Introspection is preferred because it confirms the token was issued to this application and returns the token's granted scopes.
3. **Validation is not free per request.** Microsoft and LinkedIn tokens are re-validated cheaply and offline on every request. A GitHub token requires an API call. The backend only needs the opaque proof at link time (the `X-Account-Link-Authorization` header), so GitHub identity is resolved at login/link only. The per-request session model already trusts the frontend-resolved candidate through `load_session_provider_candidates`; do **not** introduce a per-request GitHub API call.
4. **Stable subject is the numeric `id`, not the login.** A GitHub `login` (username) can change; the numeric `id` is immutable. Store the numeric `id` (as a string) in `github_user_id`. Never key identity on the username.
5. **Email is private by default.** Obtaining a verified email requires the `user:email` scope and `GET /user/emails`. Email is not required for identity mapping, matching the LinkedIn rule of storing no provider profile data.
6. **Not full OpenID Connect and no discovery document.** GitHub has static authorize/token endpoints and returns only an access token. The frontend cannot reuse LinkedIn's `openid-client` discovery/identity-token flow; GitHub needs a small custom OAuth 2.0 authorization-code implementation.
7. **No roles, groups, or tenant.** A `GitHubGuard()` admits a verified GitHub identity with no scope/role/group/tenant requirements, mirroring `LinkedInGuard()`. Administrator, tenant-group, and Azure-group behavior remain Microsoft-specific.

Token lifetime: classic GitHub OAuth App access tokens do not expire by default. This plan assumes an **OAuth App** (simplest, closest to LinkedIn); reauthentication is the recovery path. A GitHub App with expiring user-to-server tokens and refresh tokens is out of scope.

## What is reused versus what is new

### Reused without change (provider-neutral, enum-driven)

- Account link, merge, and unlink CRUD in [`crud/account_merge.py`](../../../backend/src/crud/account_merge.py): `link_or_preview`, `merge_provider_users`, `prepare_provider_unlink`.
- Link endpoints in [`routers/api/v1/identities.py`](../../../backend/src/routers/api/v1/identities.py): `/user/me/link/preview`, `/user/me/link/confirm`, `DELETE /user/me/link/{provider}`.
- Linking helpers in [`routers/api/v1/account_linking.py`](../../../backend/src/routers/api/v1/account_linking.py): `link_identities`, `account_identity`, `cleanup_unlinked_provider`.
- Guard framework in [`core/security.py`](../../../backend/src/core/security.py): `Guards`, `evaluate_guards`, `select_provider_candidate`, guard declaration order.
- Frontend linking flow: `completeAccountLink`, the `/oauth/providers` UI, the unlink action, and the `OAuthTransaction`/intent model.

### Not reusable for GitHub

- JWKS caching (`get_cached_jwks`) — GitHub has no JWKS.
- Issuer-based dispatch (`_provider_validators` keyed by `iss`) — needs a parallel opaque-token path.
- `openid-client`-based frontend validation — GitHub is not full OpenID Connect.

## Authentication and account contract

- GitHub login uses a custom OAuth 2.0 authorization-code flow. Microsoft acquisition uses Microsoft Authentication Library (MSAL); LinkedIn uses `openid-client`.
- Add only a nullable, unique `User.github_user_id` containing the validated numeric GitHub `id` as a string. Keep `azure_user_id`, `azure_tenant_id`, and `linkedin_user_id`. No external-identity table, stored email requirement, or per-user issuer column.
- Keep the GitHub client identifier and client secret in configuration. The client secret is used only for server-side token exchange and introspection, never exposed to the browser.
- Authenticate GitHub users by resolving the opaque access token to the immutable numeric subject through the GitHub API at login/link time. No backend-issued tokens; no per-request GitHub API calls.
- Internal backend requests continue to use the frontend application token plus `X-Application-Session`; direct backend clients use provider bearer tokens; browser Socket.IO uses short-lived one-time admission tickets. A session reference alone never authenticates a caller.
- Preserve `guards: GuardTypes = Depends(...)` at endpoints. Endpoints/events configure outer admission; shared security resolves `CurrentUserData`; CRUD applies resource access policies.
- Keep `azure_token_roles` and `azure_token_groups` in `CurrentUserData` populated only from a validated Microsoft authentication. A GitHub session never borrows Microsoft claims.
- First-time linking and merging existing users work in either provider direction. Merge reassigns references and deletes superseded records without retaining history, per the existing [account merge contract](./linkedin-azure-account-merge-plan.md).
- Apply the [data-storage policy](README.md#data-storage-policy), [application encryption contract](README.md#application-encryption), and [Redis storage contract](../../redis/README.md). The numeric GitHub `id` is a permitted minimal identifier; GitHub API responses (profile, email) stay transient in memory only and are never persisted.
- No cross-provider AND expressions, additional authentication service, new scripts, or deployment workflows.

## Component responsibilities

Paths are relative to this document.

| Concern | Code | Responsibility |
| --- | --- | --- |
| Provider token validation | [`core/authentication/github.py`](../../../backend/src/core/authentication/github.py) (new) | Resolve an opaque GitHub token to normalized claims via GitHub introspection/`/user`; no JWKS |
| Authentication dispatch and resolution | [`core/security.py`](../../../backend/src/core/security.py) | GitHub opaque-token path outside JWT issuer dispatch; `GitHubGuard` evaluation; GitHub branch in identity resolution |
| Shared contracts | [`core/types.py`](../../../backend/src/core/types.py) | `IdentityProvider.github`, `GitHubGuard`, `ProviderGuard` union member |
| User identifiers/settings | [`models/identity.py`](../../../backend/src/models/identity.py) | `github_user_id` field, protected identifier updates, merge settings schemas |
| Signup and account operations | [`crud/identity.py`](../../../backend/src/crud/identity.py), [`crud/account_merge.py`](../../../backend/src/crud/account_merge.py) | `github_user_self_sign_up`; `provider_identifier()` and merge field-list GitHub branches |
| Configuration | [`core/config.py`](../../../backend/src/core/config.py) | `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, GitHub API base |
| Provider acquisition | [`lib/server/oauth/github.ts`](../../../frontend_svelte/src/lib/server/oauth/) (new) | Custom OAuth 2.0 code flow, Redis-encrypted proof storage, proof-token retrieval |
| Login lifecycle | [`login`](../../../frontend_svelte/src/routes/(layout)/login/), [`callback`](../../../frontend_svelte/src/routes/(layout)/oauth/callback/), [`logout`](../../../frontend_svelte/src/routes/(layout)/logout/) | GitHub login/linking, callback completion, and logout |
| Linking UI and session | [`identityProvider.ts`](../../../frontend_svelte/src/lib/identityProvider.ts), [`accountLink.ts`](../../../frontend_svelte/src/lib/server/oauth/accountLink.ts), [`oauth/providers`](../../../frontend_svelte/src/routes/(layout)/oauth/providers/), [`types.d.ts`](../../../frontend_svelte/src/lib/types.d.ts), [`Navbar.svelte`](../../../frontend_svelte/src/routes/(layout)/Navbar.svelte) | Provider enum/field, proof-token branch, GitHub link/unlink controls, display fields |

## Authentication and guard contract

Follow the [security definitions and change boundary](../../../AGENTS.md#security-layers-and-change-boundaries) and [architecture guidance](README.md#architecture-and-change-boundary). This work changes outer admission only; it preserves inner access enforcement.

Guard declaration mirrors LinkedIn. Proposed syntax; this is not currently callable code:

```python
post_message_guards = Guards(
    MicrosoftGuard(scopes=["api.read", "api.write"], roles=["User"]),
    LinkedInGuard(),
    GitHubGuard(),
)

# Endpoint parameter; the callable returns policy configuration:
guards: GuardTypes = Depends(post_message_guards)
```

The common security flow is unchanged except that GitHub is not selected by an unverified `iss` claim:

1. Extract an optional request bearer token, or retrieve a server-cached token through the existing socket session reference.
2. For JWT providers, read the unverified `iss` only to select an allowlisted validator. For GitHub, the opaque proof is recognized on the dedicated link/login path and validated through the GitHub API; it is never routed through JWT issuer dispatch.
3. Validate the credential and carry the verified provider and normalized claims in an internal authentication context.
4. Evaluate declared alternatives in order. Alternatives are OR; requirements within a provider branch are AND. A token cannot satisfy another provider's branch.
5. Resolve the verified identifier through its provider lookup/signup handler and produce `CurrentUserData`, or `None` for admitted anonymous access.
6. Pass the result through `BaseView`/`BaseNamespace` to existing access checks.

### GitHub token validation

- Resolve the opaque access token to the immutable numeric subject through the GitHub API. Prefer token introspection (`POST /applications/{client_id}/token` with HTTP Basic `client_id:client_secret`), which confirms the token belongs to this application and returns its granted scopes; fall back to `GET /user` only if introspection is not used.
- Normalize the result to claims `{ "sub": str(id), "login": <login> }`. Key identity on `sub` (the numeric `id`), never on `login`.
- Do not fetch or persist profile or email data for identity mapping. If a verified email is ever needed for display, request the `user:email` scope and read `GET /user/emails` transiently.
- Validate callback state against a short-lived login transaction, binding provider, login/link intent, initiating user, exact redirect Uniform Resource Identifier (URI), and allowed return destination, exactly as the LinkedIn flow does.
- A GitHub access token authenticates only within this application's configured trust boundary and carries no GitHub resource permissions for the backend; guards and access policies make those decisions.

## Implementation stages

Dependency order: **A → B**, and **C** may proceed in parallel once Stage A's contract is fixed; **D** depends on A–C. Each stage lists concrete files, steps, decision markers, and completion criteria.

### Stage A — Policy types, configuration, and GitHub token validation

Goal: the backend can turn an opaque GitHub access token into a verified identity and evaluate a `GitHubGuard`, without any live endpoint enabling GitHub yet. No database or frontend changes; independently testable with mocks.

**A1. Shared types** — [`core/types.py`](../../../backend/src/core/types.py)

- Add `github = "github"` to the `IdentityProvider` enum (after `linkedin`).
- Add a `GitHubGuard` model mirroring `LinkedInGuard`: `model_config = ConfigDict(extra="forbid", frozen=True)`, `provider: Literal["github"] = "github"`, and no scope/role/group fields.
- Add `GitHubGuard` to the `ProviderGuard` discriminated union so the `provider` discriminator accepts `"github"`.

**A2. Configuration** — [`core/config.py`](../../../backend/src/core/config.py) and the backend environment example

- Add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` via `get_variable`, mirroring `LINKEDIN_CLIENT_ID`. An empty value disables the provider.
- Add a configurable GitHub API base (default `https://api.github.com`) so GitHub Enterprise can be pointed elsewhere without code changes.
- Add the new variables to the environment example with placeholder values.

**A3. GitHub validation module** — [`core/authentication/github.py`](../../../backend/src/core/authentication/github.py) (new)

- Expose `async def resolve_github_identity(token: str) -> dict[str, Any]` returning normalized claims `{ "sub": str(id), "login": login }`. Raise `HTTPException(503, …)` when the provider is not configured and `HTTPException(401, …)` for any invalid/foreign/failed token.
- ⚠️ **INPUT NEEDED (Decision 2):** choose the resolution transport. Introspection (`POST {api}/applications/{client_id}/token` with HTTP Basic `client_id:client_secret` and JSON body `{"access_token": token}`; read `user.id`, `user.login`, `scopes`; a `404` means the token is not valid for this app) confirms the token was issued to this application. The plain alternative is `GET {api}/user` with `Authorization: Bearer <token>` and the versioned `Accept` header. The plan assumes introspection; the module is structured so only this function body changes if the plain method is chosen.
- Use the repository's existing HTTP client as the other provider modules do. Do **not** add JWKS caching or any key handling — GitHub has none.

**A4. Security dispatch and resolution** — [`core/security.py`](../../../backend/src/core/security.py)

- Add an opaque-token path so `verify_access_token` (used by `link_identities` for the `X-Account-Link-Authorization` proof) first attempts the existing JWT issuer dispatch, and when the token is not a decodable JWT, falls back to `resolve_github_identity` when GitHub is configured, returning `VerifiedIdentity(IdentityProvider.github, claims)`. Design note: the link header carries no provider hint, so this try-JWT-then-opaque ordering keeps the generic `/user/me/link/*` endpoints provider-agnostic.
- Extend `resolve_verified_identity_with_status` and `resolve_session_identity` with a `github` branch that calls `github_user_self_sign_up(subject)` and returns `CurrentUserData` with empty Azure roles/groups, mirroring the existing `linkedin` branch.
- Extend `select_provider_candidate` and `evaluate_guards` to admit a `GitHubGuard` (no extra requirement checks, same shape as the LinkedIn branch).
- ⚠️ **INPUT NEEDED (Decision 4):** extend `load_session_provider_candidates` to build a GitHub candidate. The assumed model reads a stored `$.githubSubject` from the session and constructs `VerifiedIdentity(IdentityProvider.github, {"sub": subject})` **without** a per-request GitHub API call, trusting the frontend-authenticated session (option 4a). If a short-time-to-live re-check (option 4c) is chosen, the cached introspection lookup goes here instead.

**A5. Tests** (mocked, no live GitHub)

- `resolve_github_identity`: successful resolution, foreign/invalid token → 401, unconfigured provider → 503, network-failure propagation.
- `verify_access_token` fallback: a JWT still dispatches by issuer; an opaque token resolves through GitHub.
- Guard selection and provider isolation: a GitHub identity satisfies `GitHubGuard` only and never a Microsoft/LinkedIn branch.

**Completion criteria:** existing Microsoft/LinkedIn/anonymous tests still pass; GitHub validation, dispatch fallback, and guard selection are covered by synthetic tests; no endpoint enables GitHub yet.

### Stage B — Minimal user identity, signup, and merge

Goal: a verified GitHub subject resolves to an internal user, and GitHub participates in linking and merging. Depends on Stage A.

**B1. Identity model** — [`models/identity.py`](../../../backend/src/models/identity.py)

- Add `github_user_id` as a nullable, unique, case-sensitive string column with PostgreSQL `C` collation, allowing multiple nulls, mirroring the `linkedin_user_id` column definition (including `index=True, unique=True`). Store the numeric GitHub `id` as a string; do not treat it as an email or Universally Unique Identifier (UUID).
- Add `github_user_id` to the read schema and the admin-create schema; exclude it from user/profile update schemas so ordinary updates cannot set a provider identifier (mirror the LinkedIn `exclude=True` treatment on update schemas).

**B2. Signup and lookup CRUD** — [`crud/identity.py`](../../../backend/src/crud/identity.py)

- Add `github_user_self_sign_up(github_user_id: str)` mirroring `linkedin_user_self_sign_up`, delegating to `_provider_sign_up`.
- Add a `github_user_id` branch to `_provider_sign_up` and `resolve_existing_provider_user`, using the existing advisory-lock/savepoint pattern. Never call Azure group synchronization. Ensure a GitHub-only user does not acquire an Azure tenant through the `UserCreate` default.

**B3. Account merge CRUD** — [`crud/account_merge.py`](../../../backend/src/crud/account_merge.py)

- Add the `github` branch to `provider_identifier()` returning `("github_user_id", <id-string>, None)`.
- Add `github_user_id` to the merge conflict/reassignment field list and to unlink field handling so merge and unlink cover all three providers.

**B4. Development migration**

- Generate only the **development** migration adding the `github_user_id` column and its unique index, following the [PostgreSQL migration workflow](../../postgres/README.md#schema-migration-workflow). The maintainer runs the development migration manually.
- Do **not** author a stage/production migration; the continuous integration (CI) pipeline generates it from model metadata.
- ⚠️ **INPUT NEEDED (Decision 3):** this stage introduces provider self-signup (an outer-layer change). Confirm the change boundary before executing this stage.

**B5. Tests**

- `crud/tests/test_account_merge`: unclaimed GitHub identity attaches to an existing user; GitHub-versus-other merge preview and confirmation; unlink retains the active provider.
- Provider signup: GitHub subject creates the expected settings and self-ownership; concurrent signup and unique-conflict handling; disabled-user semantics preserved; GitHub-only user has no Azure tenant/roles/groups.

**Completion criteria:** all three providers resolve internal users; GitHub signup creates expected settings and self-ownership; existing Microsoft/LinkedIn data is unaffected; the development migration applies cleanly.

### Stage C — Frontend login, linking, unlink, and display

Goal: a signed-in user can link, use, and unlink a GitHub account through the existing UI. May proceed in parallel with Stage B once Stage A's contract is fixed; end-to-end verification depends on B.

**C1. Provider enum and types** — [`identityProvider.ts`](../../../frontend_svelte/src/lib/identityProvider.ts), [`types.d.ts`](../../../frontend_svelte/src/lib/types.d.ts)

- Add `GITHUB = 'github'` to the `IdentityProvider` enum and a `github_user_id?: string | null` field to the user shape.
- Include GitHub in `preferredIdentityProvider` ordering after the existing providers.

**C2. GitHub OAuth provider** — `frontend_svelte/src/lib/server/oauth/github.ts` (new)

- Implement a custom OAuth 2.0 authorization-code flow: `signIn()` builds the GitHub authorize URL with `client_id`, `redirect_uri` (`{origin}/oauth/callback/github`), state bound to the session, and the minimal scope; `authenticateWithCode()` exchanges the code at GitHub's token endpoint (server-side, with the client secret) for the opaque access token.
- ⚠️ **INPUT NEEDED (Decision 1):** if a GitHub App (expiring tokens) is chosen instead of an OAuth App, this module must also store and use the refresh token and handle token expiry/refresh; the OAuth App path stores only the access token.
- Store the encrypted proof in Redis mirroring the LinkedIn provider's per-user encrypted storage, and expose a proof-token accessor (the opaque access token) for linking.
- Extend `providerProofToken` in [`accountLink.ts`](../../../frontend_svelte/src/lib/server/oauth/accountLink.ts) with a GitHub branch returning the stored access token.

**C3. Login, callback, and logout routes**

- Add `routes/(layout)/login/github/+page.server.ts`, `routes/(layout)/oauth/callback/github/+page.server.ts`, and `routes/(layout)/logout/github/+page.server.ts`, mirroring the LinkedIn routes, including the `intent=link` handling that calls `completeAccountLink` and redirects to `/account/merge` when the backend returns `merge-required`.

**C4. Linking UI, unlink action, and navigation**

- Add a GitHub section to the [`/oauth/providers`](../../../frontend_svelte/src/routes/(layout)/oauth/providers/) page and its loader (login/logout button, token-status icon, link icon, unlink button), following the LinkedIn section.
- Extend the `unlinkaccount` action in [`routes/(layout)/+page.server.ts`](../../../frontend_svelte/src/routes/(layout)/+page.server.ts) to accept `github` and reload the user afterward.
- Add GitHub display fields/conditions to [`Navbar.svelte`](../../../frontend_svelte/src/routes/(layout)/Navbar.svelte).

**C5. Tests**

- Provider-preference logic, `accountLink` GitHub branch, `oauth/callback/github` (login, link, merge-required), `login/github` intent handling, and the `/oauth/providers` credential-availability check, mirroring the LinkedIn tests.

**Completion criteria:** a signed-in user can link and unlink a GitHub account; the merge path is reachable when the GitHub identity already belongs to another user; provider selection and display behave like LinkedIn.

### Stage D — End-to-end verification and documentation

Goal: confirm the three-provider system behaves correctly together and record the outcome. Depends on A–C.

- **D1. Backend suite** — run the affected backend tests in the test container: GitHub validation, `test_account_merge`, `test_account_link`, provider signup, plus ruff and the production-code type check. Report the pass/fail summary in the tool's own format.
- **D2. Frontend suite** — run the new/updated vitest files for `identityProvider`, `accountLink`, `oauth/callback/github`, `login/github`, and `/oauth/providers`.
- **D3. Manual end-to-end** — sign in with Microsoft, link a GitHub account, confirm `github_user_id` persists; exercise the merge path with a GitHub identity already tied to a second user; unlink GitHub and confirm the active provider is retained.
- **D4. Documentation** — update this plan's status and the security [README](README.md) authentication-modules table to list the GitHub module, matching the existing LinkedIn entries. No other documentation is created.

**Completion criteria:** backend and frontend suites pass (baseline failures, if any, called out explicitly); the manual link/merge/unlink flow works; documentation reflects the added provider.

## Scope exclusions

- No GitHub login as a primary/standalone identity beyond what linking requires.
- No stored GitHub profile or email data; no encrypted database columns introduced by this work.
- No roles, groups, tenant, or administrator semantics for GitHub.
- No stage/production migration authored here; CI generates it.
- No inner access-control (ACL) changes.
