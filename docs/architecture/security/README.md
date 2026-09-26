# Security and OAuth

## Architecture and change boundary

The definitions of the inner and outer security layers and the consultation requirement are in [AGENTS.md](../../../AGENTS.md#security-layers-and-change-boundaries).

[Backend security](../../../backend/src/core/security.py) delegates provider-token validation to [authentication helpers](../../../backend/src/core/authentication/) and evaluates the alternatives configured by endpoint and Socket.IO guards. Endpoints retain `guards: GuardTypes = Depends(...)`; shared security resolves the internal user for the existing CRUD boundary. [Access enforcement](../../../backend/src/crud/access.py), including `filters_allowed()`, then applies resource permissions. Outer admission never replaces those checks. Preserve existing Microsoft administrator/group exceptions.

If tests reveal a necessary inner-layer change outside the agreed merge scope, report the concrete issue and proposed change to the user before implementing it; continue unaffected work. Ordinary resource/group operations under existing policies do not constitute a change to the security architecture.

## Authentication modules

Provider mechanics are separate from application admission policy:

| Module | Responsibility |
| --- | --- |
| `core/authentication/base.py` | Verified identity context, allowlisted issuer dispatch, and shared public signing-key retrieval/cache |
| `core/authentication/azure.py` | Microsoft discovery, signing-key retrieval, access-token validation, and existing refresh/retry behavior |
| `core/authentication/linkedin.py` | LinkedIn signing-key retrieval and identity-token validation, including one fresh-key retry after token validation fails |
| `core/security.py` | Guard requirements/evaluation, transport credential extraction, and internal-user resolution |

The LinkedIn provider uses its [published signing-key endpoint](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2). Issuer/audience expectations come from trusted application configuration; token claims never select an arbitrary network endpoint. `get_linkedin_token_payload(token, issuer=..., client_id=...)` wraps the pure validator with cached key retrieval. This helper does not enable LinkedIn login or signup by itself.

See [public signing-key caching](../../redis/README.md#public-signing-key-caching) for partitions and refresh behavior. Provider modules do not evaluate application scopes/roles or access policies.

### Frontend provider acquisition

The frontend `OAuthProvider` contract in `frontend_svelte/src/lib/server/oauth/base.ts` is deliberately narrow: shared API wrappers need only provider-independent access-token acquisition. Microsoft keeps its separate Microsoft Authentication Library (MSAL) implementation. Do not pre-emptively turn LinkedIn's `openid-client` implementation into a configurable provider framework.

When adding the next OpenID Connect provider through `openid-client`, first implement its working provider-specific flow. Compare that implementation with LinkedIn, then extract an `OpenIdConnectProvider` base around code that is actually identical. Keep discovery, authorization transactions, callback validation, token storage/refresh and subject checks in the shared base only where both providers have the same behavior; retain provider-specific scopes, client authentication, nonce or Proof Key for Code Exchange requirements, error handling and protocol quirks in their provider modules. This evidence-based extraction should avoid provider switches and unused configuration hooks.

## Registration session state

The OAuth callback sets `SessionStatus.REGISTRATION_PENDING` when the backend creates a user during login. This status is durable: it remains pending until the user submits the welcome profile form. The form submission is the registration-completion boundary and is intended to include acceptance of terms and conditions later; terms handling is not implemented yet.

The one-time welcome display is tracked separately with the session-only `welcomePending` flag. The first authenticated layout consumes that flag without changing the registration status, so reloading a page does not repeatedly open the modal while an incomplete registration remains pending. For development, the callback retains a commented switch that marks an existing user as registration-pending and sets the corresponding welcome flag through the same status-derived logic.

## Data-storage policy

This is the repository-wide policy for integrations, independent of where data would be stored:

- For third-party data, retain only authentication-derived tokens, authentication-library account metadata, and validated claims needed to authorize calls to the internal backend or external Application Programming Interfaces (APIs). Apply the [application encryption contract](#application-encryption), plus the [Redis-specific scope](../../redis/README.md#encryption-scope) when Redis is the storage location. Keep credentials server-side.
- Responses obtained by authorized third-party resource calls, including Microsoft Graph `/me` and LinkedIn `/v2/userinfo`, may exist only in transient application memory for processing/display. This covers selected fields, names, emails, pictures, picture URLs, avatars, downloaded media, and derived copies.
- Never persist that resource data in Redis, databases, files, logs, telemetry, durable queues, browser storage, service-worker caches, or other application-controlled storage, even encrypted. Use non-caching Hypertext Transfer Protocol (HTTP) fetch/response behavior. Do not enrich persisted authentication metadata or sessions with resource responses.
- Fetch resource data when needed. If request volume becomes an issue, fetch less and defer retrieval until the consuming frontend elements are activated; do not add persistent profile caches as a workaround.
- First-party application records/settings and minimal verified identifiers linking provider identities to internal users remain permitted. Do not relabel third-party response data as first-party data. The shared encryption module can support future database fields, but the current account-linking work does not itself introduce encrypted database columns.
- Use synthetic third-party data in stored test fixtures. When modifying an integration, remove conflicting persistence from the affected flow instead of reproducing it.

## Application encryption

The backend [encryption module](../../../backend/src/core/encryption.py) and frontend-server [encryption module](../../../frontend_svelte/src/lib/server/encryption.ts) implement the same application-wide authenticated-encryption contract. They share one environment-specific keyring and may protect approved Redis, database, or other server-side application data. Encryption does not make data permitted by itself; the [data-storage policy](#data-storage-policy) remains authoritative.

### Format and associated data

Use Advanced Encryption Standard in Galois/Counter Mode with a 256-bit key (AES-256-GCM). Binary fields are Base64 encoded. Every encrypted value uses this envelope:

| Field | Meaning |
| --- | --- |
| `version` | Envelope-format version |
| `key-version` | Key version selecting the decryption key |
| `nonce` | Fresh cryptographically random 12-byte value; never reuse it with the same key |
| `ciphertext` | Encrypted data |
| `tag` | Mandatory 16-byte authentication tag |

Bind the stable storage location, canonical field/path purpose, envelope version, and key version through consistently encoded associated data. Redis callers use the full Redis key and JSON path; future database callers must use a stable database-specific location and field purpose. This prevents valid ciphertext from being moved between accounts, records, or protected fields.

Verify the authentication tag before consuming plaintext. Wrong keys, modified ciphertext, malformed envelopes, or changed associated data fail closed. Keys remain in server memory and never appear in stored envelopes or browser-visible data. Cross-runtime tests maintain Python/TypeScript compatibility.

### Keyring and startup

- OpenTofu generates a cryptographically random 32-byte key and stores its Base64 representation as the Key Vault secret `application-encryption-key`. The frontend server, backend, and worker share this keyring within an environment. Development, test, stage, and production use different keys; encryption keys are never reused for signing.
- Key Vault startup fetches the latest secret, enumerates every version, orders versions newest-to-oldest by creation time, and retrieves each historical value by its exact version. It does not sort opaque version identifiers or perform Key Vault requests during encryption/decryption.
- The loader retries if rotation overlaps startup. Ambiguous creation times, disabled/unavailable versions, missing permissions, malformed keys, or an incomplete current version fail startup rather than silently dropping a decryption key.
- Every historical version remains enabled and retrievable while retained ciphertext may reference it. Durable database ciphertext can require substantially longer retention than cache data. Startup cost and memory grow linearly with retained versions.
- Local configuration uses `ENCRYPTION_KEY_1` and `ENCRYPTION_KEY_VERSION_1`, followed by contiguous `_2`, `_3`, and so on, ordered newest-to-oldest. At least one complete pair is mandatory. Three local/test keys—current plus two historical generations—are the recommended practical default; the loader supports more.
- New values always use the newest key. Readers select an already-loaded key by the envelope's `key-version`; unknown versions fail closed and never trigger an on-demand secret lookup.

### Rotation and deployment

`encryption_rotation_revision` is a non-secret OpenTofu rotation trigger. Changing it replaces the `random_id.applicationEncryptionKey` value and creates a new version under the same Key Vault secret name; unrelated infrastructure changes preserve the current key. Never delete and recreate the secret as a rotation mechanism.

Rotation revisions are environment-specific. GitHub Actions uses `ENCRYPTION_ROTATION_REVISION_DEV`, `ENCRYPTION_ROTATION_REVISION_STAGE`, and `ENCRYPTION_ROTATION_REVISION_PROD` repository/environment variables. Local infrastructure runs use `ENCRYPTION_ROTATION_REVISION` from `infrastructure/.env`. Increment the targeted environment's value, inspect the OpenTofu plan for replacement of the random key and a new Key Vault secret version, then approve the normal deployment. Localhost application keys in frontend/backend `.env` files and synthetic test keys are not managed by this revision.

Deploy the backend successfully before the frontend during a production rotation. A new process can read all retained historical versions, while an old process cannot read data newly written with the latest key. Secret changes do not update in-memory keyrings; all application processes must restart/redeploy to adopt the new version. Keep old versions enabled until all referencing data is expired, deleted, or re-encrypted.

### Encrypted-only behavior

Encryption is mandatory and has no runtime disable switch. There is no plaintext compatibility reader. Existing plaintext is never consumed as encrypted data. Redis provider-cache adapters delete unreadable existing records: Microsoft treats the deletion as a cache miss, while LinkedIn requires reauthentication. Missing keys fail startup; authentication failures, malformed envelopes, and unknown key versions fail closed.

## Implementation plans

- [LinkedIn authentication and credential encryption](linkedin-account-linking-plan.md) — provider/guard contracts, endpoint matrix, code mappings, stages, and validation.
- [Authentication session lifecycle and Socket.IO expiry recovery](authentication-session-lifecycle-plan.md) — sliding Redis/cookie renewal, one-session reauthentication, established-connection expiry enforcement, compact status events, and reconnect/replay.
- [Account linking and merge](linkedin-azure-account-merge-plan.md) — verified attachment, settings choices, reference reconciliation, and transactional merging across providers.

The [Redis README](../../redis/README.md) owns Redis partitions, protected cache/session boundaries, and Redis-specific performance measurements. This document owns the application-wide encryption and key-rotation contract. The plans describe implementation work; they do not imply that planned features are already deployed.

## References

- [Authenticated encryption](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM): nonce requirements, authentication tags, and rejection of modified ciphertext.
- [Key Vault JavaScript secret versions](https://learn.microsoft.com/en-us/azure/key-vault/secrets/javascript-developer-guide-get-secret) and [Python SecretClient](https://learn.microsoft.com/en-us/python/api/azure-keyvault-secrets/azure.keyvault.secrets.secretclient?view=azure-python): version-specific retrieval and metadata-listing permissions.
