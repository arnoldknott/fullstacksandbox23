# Authentication session lifecycle and Socket.IO expiry recovery

Status: planned. Provider login, server-side sessions, provider-token validation, Socket.IO connection rejection, snapshot subscription, and cursor replay are implemented. Sliding renewal, same-session reauthentication, established-socket expiry handling, and the compact status protocol below are not yet implemented.

This plan extracts the remaining authentication-lifecycle work from the [LinkedIn plan](linkedin-account-linking-plan.md). It applies to all identity providers; LinkedIn's measured one-hour identity-token lifetime merely makes the missing behavior visible.

## 1. Invariants

- Redis time to live (TTL) is authoritative for application-session validity. A cookie or open socket alone proves nothing.
- Provider credentials remain authoritative for provider authentication. Sliding an application session never extends a provider token.
- Renew the existing application session only when its remaining Redis TTL is less than half of `session_timeout`.
- A normal Hypertext Transfer Protocol (HTTP) response renews Redis and the existing HTTP-only cookie together. Socket.IO can renew Redis, but needs a same-origin HTTP touch to renew the cookie.
- Reauthentication retains the established `session_id`. Only initial unauthenticated login creates a pending session. Delete a superseded Redis session after any intentional rotation.
- Expired authentication ends protected socket operations and passive receipt of protected room broadcasts.
- Embedded recovery retains the allowlisted target and existing top-window navigation.
- Reconnection reuses the existing authorized snapshot subscription and cursor replay; it never reintroduces full collection transfer.

This is outer authentication and transport work. It does not change inner application access-control-list semantics.

## 2. Separate lifetimes

| Lifetime | Authority | Recovery |
| --- | --- | --- |
| Application session | Redis TTL, mirrored by the cookie deadline | Login if no valid session remains |
| Provider token | Validated provider claims/cache metadata | Reauthenticate that provider in the existing application session |
| OAuth transaction | Short-lived server transaction state | Restart the attempt |
| Established socket | Current session/provider validation | End protected access, reauthenticate, reconnect, and resubscribe |

An expired provider token must not be reported as an expired application session. A valid provider token cannot revive an absent Redis session.

## 3. Sliding renewal and touch coordination

After a valid normal request or successfully authenticated Socket.IO operation:

1. Read the remaining Redis TTL.
2. At or above half of `session_timeout`, do nothing.
3. Below half, atomically extend the same Redis key to the full timeout without recreating an already expired session.
4. On HTTP, reset the existing cookie to the same lifetime.
5. On Socket.IO, permit a same-origin HTTP touch so the cookie does not expire while Redis remains active.

Redis TTL is the only authoritative reference time. Do not persist `last_touched_at`.

The root layout owns a Svelte context session-lifecycle coordinator shared by every `SocketIO` instance. It keeps only process-local state such as `lastTouchAttemptAt` and an optional in-flight promise. Sockets ask it to touch after successful authenticated activity; it throttles and coalesces calls. The server still enforces the half-TTL threshold.

Do not mutate `page.data.session`: it is server-derived page data, replaced during navigation/invalidation, and is not a synchronization primitive. Do not store the timestamp in Redis, a database, browser storage, or the application session. A reload resetting it and occasional duplicate attempts across tabs are harmless.

The minimal same-origin touch endpoint validates the current session/provider authentication, uses the existing cookie, accepts no caller-selected session identifier or lifetime, and returns no credential data.

## 4. One-session reauthentication

When an application session remains valid but the required provider token expires:

1. Select the provider from trusted session/link information under the existing preference rule.
2. Associate a short-lived OAuth transaction with the established session. Do not replace it with a pending-login session, change its established status, or create another authenticated session.
3. Bind provider, intent, established session, exact callback URI, and allowlisted target in transaction state.
4. Validate the callback and update only that provider's server-side credentials/cache reference.
5. Return to the target and reconnect affected sockets.

If a security boundary deliberately requires rotation, complete the replacement first, then delete the old Redis key and stale references. Tests must show that ordinary reauthentication keeps the same `session_id` and leaves no abandoned authenticated session. Embedded reauthentication continues through the provider-specific client page to support top-window navigation.

## 5. Compact status protocol

Preserve `SocketioStatus` as a fully discriminated typed union. Success variants remain unchanged; add compact machine-readable access and connection variants, and migrate existing display errors to an explicit `other` variant:

```ts
| { error: 'access'; code: 'authentication-expired' | 'authorization-failed' }
| { error: 'connection'; code: 'connection-failed' }
| { error: 'other'; detail: string }
```

`code` is required on the actionable protocol variants and no human-readable text accompanies them; user-interface copy belongs in the client and diagnostic details stay in server logs. Existing operation-specific error strings remain available to browser consumers as `{ error: 'other', detail }`.

The distinct `error` literals support direct exhaustive narrowing without property-existence checks. Migrate backend `{ error: str(error) }` payloads to `{ error: 'other', detail: str(error) }` and update display consumers to read `status.detail`.

- `access/authentication-expired`: session or required provider credential cannot authenticate; begin provider-aware recovery when possible.
- `access/authorization-failed`: authentication is valid but guard/resource authorization rejects the operation; never trigger automatic login.
- `connection/connection-failed`: non-authentication transport/establishment failure; use connection retry or terminal handling.

Connection-time rejection still uses `connect_error`, because no socket exists for `status`. Its structured data uses the same code vocabulary. The currently implemented `reauthentication-required` code migrates to `authentication-expired`; add compatibility coverage if rolling deployment can mix versions.

`connect_error` and coded `status` variants call one client lifecycle handler. Mandatory expiry handling runs before an optional application status callback, so custom handlers cannot suppress disconnect/reauthentication. `other` errors continue through existing display callbacks. Unknown variants fail safely and remain observable.

## 6. Established socket expiry

Protected incoming events continue to retrieve the session, validate provider authentication, evaluate guards, and apply resource authorization. Missing sessions or expired tokens stop the operation before create/read/update/delete work.

This is insufficient for idle sockets already in protected rooms. Implement an expiry boundary:

1. Track enough non-sensitive connection state to schedule or check the earliest session/provider expiry.
2. At expiry, or when an event discovers it, best-effort emit `{ error: 'access', code: 'authentication-expired' }`.
3. Promptly remove the socket from protected rooms and disconnect it. Enforcement must not depend on status delivery.
4. Permit room entry again only after fresh authentication and normal guard/resource checks.

Authorization denial emits `access/authorization-failed` for the operation without disconnection or a login loop. Do not expose resource existence or policy details.

After reauthentication, reconnect and follow the existing [REST snapshot and incremental Socket.IO contract](../data-transfer/internal/rest-snapshot-incremental-socketio.md): authorized subscription, final-batch cursor, filtering, room entry, and mutation replay. Add no alternate recovery stream.

## 7. Implementation stages

### A. Protocol and client lifecycle

- Add matching backend/frontend status definitions.
- Share provider-aware handling between `connect_error` and `status`.
- Add the root-layout context coordinator and in-memory throttle.
- Preserve embedded top-window navigation and target URLs.

### B. Renewal and reauthentication

- Implement atomic Redis threshold renewal and synchronized cookie renewal.
- Add the minimal touch route and coordinator integration.
- Keep OAuth transaction state separate from the established session.
- Delete superseded sessions after intentional rotation.

### C. Socket enforcement and recovery

- End protected room membership and disconnect at session/provider expiry.
- Reconnect only after successful reauthentication.
- Resubscribe and replay missed mutations through the existing cursor contract.

## 8. Tests and acceptance

Use the test Docker Compose environment and the narrow commands in the frontend/backend guides. Cover:

- TTL above, equal to, and below half; invalid/expired sessions; concurrent renewal without key recreation.
- HTTP Redis/cookie renewal and coalesced socket touch across multiple sockets.
- An in-memory shared coordinator that does not mutate `page.data.session` or persistent storage.
- Initial pending login versus same-ID reauthentication, preserved status/target/identities, and cleanup after intentional rotation.
- Provider expiry remaining distinct from session expiry and not bypassed by sliding renewal.
- Shared recovery for connection-time and established-event expiry.
- Correct behavior for all three compact error codes, safe exhaustive narrowing, `other` display errors, and mandatory lifecycle handling before custom callbacks.
- An idle expired socket receiving no protected broadcast caused by another client.
- Authorized reconnect, resubscription, and cursor replay without full transfer or duplicates.
- Embedded top-window recovery to an allowlisted target.
- Microsoft/LinkedIn login, logout, requests, and non-expiry socket regressions.

Live acceptance is:

```text
valid session and subscribed socket
-> provider token expires
-> protected room access ends and socket disconnects
-> correct provider reauthentication retains the session id
-> client returns to the target
-> socket reconnects with fresh authentication
-> authorized subscription and cursor replay resume
-> no protected mutation was delivered while expired
```

Completion requires verified sliding Redis/cookie renewal, socket-only cookie synchronization, one-session reauthentication, superseded-session cleanup, established-socket expiry enforcement, and end-to-end reconnect/replay.
