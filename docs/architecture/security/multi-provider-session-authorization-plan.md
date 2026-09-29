# Multi-provider session authorization

Status: in progress; stages A and B are implemented. This plan replaces the currently implemented single-active-provider selection model for communication from the trusted frontend server to the backend. Account linking, provider credential acquisition, encrypted cache storage, and the existing inner access-control layer remain unchanged until this plan is implemented.

## 1. Outcome and terminology

An application session may hold independently validated credentials for multiple providers linked to the same internal `User`. Each Hypertext Transfer Protocol (HTTP) request or Socket.IO operation selects one provider identity that satisfies that interface's existing guard policy. Claims are never combined into a synthetic identity.

- **Available provider:** the session contains a credential that can currently be validated, including normal silent renewal where the provider supports it.
- **Selected provider:** the one available provider used for one authorization decision.
- **Preferred provider:** the first suitable provider in the interface's guard declaration order.
- **Linked provider:** a persistent provider identifier attached to the internal user. Linking alone does not make a credential available.

The most recently completed login does not globally select authorization for the session. `identityProvider` must no longer be interpreted as a session-wide active provider. Remove it where it becomes redundant or retain it only as explicitly named login/diagnostic history; it must not drive REST or Socket.IO authorization.

## 2. Authorization invariants

- Endpoint and event `Guards(...)` declarations remain the only source of truth for accepted providers and Microsoft scope, role, group, and tenant requirements. Do not duplicate guard configuration in frontend route wrappers.
- For one operation, evaluate one provider's validated claims. Never union Microsoft roles/groups/scopes with LinkedIn claims or let one provider satisfy another provider's requirements.
- Evaluate authenticated alternatives in guard declaration order. A Microsoft-only operation never falls back to LinkedIn; an operation declaring both providers uses whichever eligible provider guard appears first.
- Evaluate `AllowAnonymous` only after every authenticated alternative, regardless of its declaration position. Missing, invalid, expired, or insufficient provider credentials may therefore use explicitly permitted anonymous access, with no provider claims or `CurrentUserData` passed to the inner layer. Session/user binding failures, cache decryption failures, and authentication-service failures still fail closed rather than becoming anonymous.
- Every candidate provider identity must resolve to the same active internal user recorded in the application session. A mismatch fails the entire session request with status 401 and must not fall through to another provider.
- Inner application access-control-list enforcement continues to receive one `CurrentUserData` derived from the selected identity. General CRUD authorization semantics do not change.
- Account-link and merge proof headers remain explicit, separately validated proof-of-control inputs. They are not replaced by automatic session-provider selection.
- Provider unlinking must explicitly select a retained provider different from the provider being removed; it must not let the normal Microsoft-first preference accidentally authorize removal through the target provider itself.

## 3. REST transport contract

### Trusted frontend-server requests

The frontend server sends the opaque application-session reference in `X-Application-Session` instead of acquiring and forwarding a provider token for every internal API request. `BackendAPI` applies this header centrally; the generic `BaseAPI` and third-party API wrappers remain unaware of application sessions. Callers never put it in a query parameter or repeat it themselves. The accompanying `Authorization` bearer is the frontend application's client-credentials token for the backend audience, not a user's provider token.

The backend accepts that session-reference credential only when the accompanying Microsoft Entra token is valid for the backend audience, is an app-only token, and identifies the configured frontend client through its `azp`/`appid` claim. This application-level Access Control List (ACL) does not require an Entra application-role assignment. Public and other direct backend clients continue to use `Authorization: Bearer <provider-token>`. Merely knowing the header name or reaching the backend through its public ingress does not enable session-reference authentication.

The backend then:

1. Loads the unexpired Redis session without renewing or recreating a missing key.
2. Loads every provider credential referenced by that session.
3. Validates each candidate with its provider validator.
4. Resolves each candidate to an internal user and verifies equality with the session's `currentUser.id` and stored linked identifiers.
5. Selects the first candidate that independently satisfies an endpoint guard alternative, using guard declaration order.
6. Supplies only that selected `VerifiedIdentity` and its derived `CurrentUserData` to the endpoint and CRUD layer.

The backend may perform Microsoft silent acquisition against the encrypted Microsoft Authentication Library cache. LinkedIn availability requires a valid identity token or a successful supported refresh; a LinkedIn access token alone cannot authenticate the backend.

### Direct backend clients

Keep ordinary `Authorization: Bearer <provider-token>` support for direct clients and diagnostics. A direct bearer request contributes exactly one candidate identity and follows the same guard evaluation. It cannot access other credentials merely because its provider identity belongs to a linked account.

Reject requests containing both a provider bearer token and a session reference. Do not define precedence between credential modes.

### Dependency boundary

Refactor credential extraction and guard evaluation together so the selected identity cannot differ between router-wide admission, endpoint dependencies, and `check_token_against_guards_with_status()`. A request-scoped authentication context should carry the selected `VerifiedIdentity`; selection must occur once per request and be reused. Avoid retries after a mutation has executed.

## 4. Socket.IO contract

Browser code is not the trusted frontend service. When Socket.IO connects directly from a browser to public backend ingress, an origin check, custom header, or knowledge of the frontend URL cannot prove that the caller is the application frontend. The browser must therefore not send the reusable application-session reference directly to public backend ingress.

Use one of these deployments while retaining the same backend candidate loader used by REST:

1. Proxy the Socket.IO connection through the authenticated frontend-service channel without exposing the reusable session reference to the browser-to-backend hop.
2. Let the authenticated frontend service exchange the application session for a short-lived, audience-bound, backend-verifiable Socket.IO admission ticket. The ticket must have a narrow lifetime, must not be accepted by REST endpoints, and must be invalid after application-session revocation. Prefer one-time use when reconnect behavior can support it.

Select the deployment-compatible option during implementation. A raw session-reference fallback on public Socket.IO ingress is not permitted.

- Connect and event guards select a provider independently from their declared alternatives.
- Cache validated candidate identities only for the lifetime and context in which their credentials remain valid; do not treat connection-time validation as permanent authorization.
- If a later event requires another available provider, select that provider for the event without combining claims.
- When credential availability changes, subsequent events use the new candidate set. Expired credentials produce the existing compact authentication-expired status only when no available provider can satisfy that event.
- Provider selection changes alone do not require reconnecting if event authorization is resolved afresh. Reconnect remains required after session invalidation, authentication-expired disconnect, or transport loss.
- Room membership established under a stronger provider must be revalidated when the credential set changes. A socket must leave protected rooms it can no longer access and must not continue receiving passive broadcasts based on stale authorization.

REST and Socket.IO must call the same candidate loading, same-user binding, priority, and guard-evaluation implementation rather than maintain parallel provider-selection rules.

## 5. Transport-security assessment

Sending only the session reference on the frontend-server→backend hop reduces the number of components, request objects, logs, and traces through which provider access/identity tokens pass. A leaked session reference does not disclose a reusable third-party token directly and can be revoked centrally by deleting one Redis session.

It is not intrinsically a weaker bearer secret. The session reference authorizes access to all suitable provider credentials in that session and may therefore be more powerful than one provider token. Treat it as a high-value credential:

- Require cryptographically random, unguessable session identifiers; rotate on authentication-boundary changes and delete superseded sessions.
- Accept session references only in headers, redact them everywhere, and never place them in URLs, logs, error details, telemetry, or client-visible page data beyond the existing deliberate browser session mechanism.
- Enforce Redis expiry, provider-token expiry, user/provider binding, disabled-user checks, and unlink/session invalidation on every authentication path.
- Keep Transport Layer Security (TLS) for every hop. An Azure Container Apps internal network reduces exposure but is not caller authentication.
- Because the backend currently has public ingress, do not trust a header merely because the frontend normally sends it. Authenticate the frontend-to-backend service channel using the deployed Azure architecture, and reject session-reference authentication when that service identity is absent. Network location, a private header name, and Cross-Origin Resource Sharing (CORS) are not authentication.
- Keep direct provider-bearer validation available on public API ingress. An arbitrary public caller must never be able to nominate a session ID.
- Apply public rate limits to direct bearer authentication and general abuse prevention. Apply appropriately scoped service-to-service limits to the session-reference path; its primary protections are service authentication, unguessable references, expiry, and replay prevention rather than public credential-guessing limits.

The deployment design must therefore provide an authenticated frontend-service identity that the backend can verify independently of the application session. Review the deployed Container Apps ingress topology during implementation to select the existing Azure mechanism; do not enable session-reference authentication until that channel is enforced.

## 6. Frontend and user-interface behavior

- Remove provider-token acquisition from the internal `backendAPI` request path after the session-reference transport is implemented. External integration wrappers such as Microsoft Graph and LinkedIn UserInfo continue acquiring their provider-specific access tokens directly.
- `/oauth/providers` reports each provider independently: usable credential, linked relationship, and optional preference. It must not expose tokens or private cache metadata.
- Replace the singular active-provider indicator. Highlight every usable provider token; optionally mark Microsoft as preferred when multiple providers are usable.
- “Log out” remains global: delete the application session, clear its cookie, and disconnect sockets. Selective provider-token removal remains out of scope.
- Reauthentication targets the provider required by the failed operation. Do not always redirect to Microsoft when only a LinkedIn guard can satisfy the interface.

## 7. Implementation stages

### A. Shared candidate and selection model

- Introduce a request-independent provider-candidate loader in backend security code.
- Validate all referenced credentials and bind them to the session user.
- Implement deterministic guard-declaration-order selection through `GuardTypes`, with anonymous access as the final explicit fallback.
- Return the selected `VerifiedIdentity` plus `CurrentUserData` without combining claims.

### B. REST session-reference mode

- Add one centralized frontend-server session-reference transport in `BackendAPI` without coupling generic or third-party API wrappers to application sessions.
- Add backend extraction and request-scoped authentication context while preserving direct bearer clients.
- Migrate guards/endpoints without changing endpoint declarations or duplicating their requirements.
- Reject ambiguous credential modes and ensure anonymous behavior remains explicit.

### C. Socket.IO per-event selection

- Replace active-provider cache lookup with the shared candidate loader.
- Select per connect/event guard, revalidate expiry, and reconcile protected rooms after capability loss.
- Preserve compact status, reconnect, snapshot subscription, and cursor replay contracts.

### D. Lifecycle and interface cleanup

- Remove authorization dependence on session `identityProvider` and rename/remove the field according to its remaining diagnostic purpose.
- Align reauthentication with the provider required by the failed interface.
- Update `/oauth/providers` from active-provider display to usable/preferred-provider display.
- Retain global logout and explicit account-link/unlink proof semantics.

### E. Deployment boundary

- Configure and document the authenticated frontend-service channel through which session-reference credentials are accepted.
- Reject session-reference credentials received without the verified frontend-service identity, including through public ingress.
- Configure ingress/service authentication and secret-header redaction before enabling the new REST mode in any environment.
- Deploy backend support before switching the frontend transport; retain bearer-token compatibility for rollback.

## 8. Required tests and acceptance

- Candidate loading: Microsoft only, LinkedIn only, both valid, each independently expired, silent Microsoft renewal, LinkedIn refresh/no-refresh behavior, missing session, expired Redis session, disabled user, unlinked credential, tampered encryption, and credential-to-user mismatch.
- Guard selection: Microsoft-only, LinkedIn-only, both alternative orders, provider requirement failure followed by the next declared provider, and explicit anonymous fallback without provider claims.
- REST: internal session-reference mode, direct bearer compatibility, conflicting modes, request-scoped single selection, no mutation retry, no provider token forwarded by the frontend server, and no credential/session value in logs or errors.
- Socket.IO: provider choice per connect and event, transition between providers, expiry fallback, LinkedIn-only event while Microsoft is available, stale-room removal, passive broadcast denial, reconnect, and session deletion.
- Same-user binding: credentials for two different internal users fail closed even if both tokens are individually valid. Linked/merged credentials for one user succeed without claim union.
- Account lifecycle: link and merge proofs remain explicit; unlink cannot be authorized by the provider being removed; logout invalidates every cached selection and live socket.
- User interface: independent usable/linked/preferred indicators and provider-specific reauthentication targets without exposing authentication metadata.
- Transport: public-ingress session-reference rejection, forged/missing frontend-service identity, header redaction, session entropy/expiry, replay after logout, conflicting credential modes, direct Socket.IO rejection of a raw session reference, socket-ticket or proxy boundary tests, rate limiting where configured, and stage verification through the authenticated Container Apps service boundary.

Completion requires REST and Socket.IO to select from the same verified session credential set using existing guard declarations, direct bearer clients to remain supported, mismatched identities to fail closed, and no provider token to traverse the trusted frontend-server→backend hop.

## 9. Tracking

- [x] Select and document the Azure mechanism for authenticating the frontend service to the backend: Microsoft Entra client credentials with strict app-only-token validation and a frontend-client-ID ACL.
- [ ] Select authenticated Socket.IO proxying or short-lived admission tickets; prohibit raw session references on public ingress.
- [x] A: shared candidate loading, same-user binding, and guard-aware selection.
- [x] B: REST session-reference transport and direct bearer compatibility.
- [ ] C: Socket.IO per-event selection and room reconciliation.
- [ ] D: lifecycle, reauthentication, session-field, and providers-page cleanup.
- [ ] E: deployment boundary, complete automated validation, and live staging verification.
