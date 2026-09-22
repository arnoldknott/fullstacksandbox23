# Redis

Redis supports cached sessions and tokens, Socket.IO coordination, and Celery transport. Runtime configuration and access-control-list templates live in [cache](../../cache/); service wiring follows the application and Docker Compose configuration.

This document owns the agreed encryption contract and operational requirements. Encryption/key-loading work is planned, not implemented by this documentation. Follow the [data-storage policy](../architecture/security/README.md#data-storage-policy) to decide what may be retained; encryption never makes prohibited third-party resource data eligible for storage. Implementation stages and tests are tracked in [Stage F](../architecture/security/linkedin-account-linking-plan.md#f-compatible-encrypted-cache-persistence).

## Public signing-key caching

The backend caches JSON Web Key Sets (JWKS), used to verify provider signatures, as Redis JSON documents at `jwks:microsoft` and `jwks:linkedin`. These public verification keys contain no user tokens or profile data and remain unencrypted. They are separate from the user credential partitions described below.

`core/authentication/base.py` implements cache-first retrieval; each provider supplies its trusted discovery/key endpoint and partition. A cache miss fetches and stores the keys. `no_cache=True` explicitly fetches a replacement; malformed responses or failed requests do not overwrite existing keys. Both providers retry token validation once with fresh keys after a validation failure. There is no added expiry policy: this preserves Microsoft's existing on-demand refresh behavior. Microsoft retains its existing broader retry on retrieval/validation exceptions; LinkedIn's retry is limited to token-validation errors.

## Encryption scope

| Data | Treatment |
| --- | --- |
| `msal:<homeAccountId>` and `linkedin:<sub>` values | Encrypt each complete provider-cache value, including all tokens and provider authentication information |
| Session `$.microsoftAccount` | Retain the account data needed by Microsoft Authentication Library (MSAL) token retrieval; encrypt the entire subdocument |
| Other retained user-identifiable data, including first-party session subdocuments | Encrypt at the field/subdocument granularity used by existing consumers |
| Standalone `homeAccountId`, `sub`, and `sessionId`, including Redis key names and `$.sessionId` | May remain plaintext by the user's explicit decision; no opaque-key redesign is required |
| Non-sensitive operational fields, such as status/boolean flags | May remain plaintext; inspect contents before treating an entire object this way |

The identifier exception is the project's accepted pseudonymization boundary for this encryption work. It does not permit plaintext access, refresh, or identity tokens. An identifier inside an otherwise encrypted object stays inside that object's envelope; do not split `$.microsoftAccount` merely to expose a plaintext pointer. Keep existing session/authentication checks regardless of storage format.

Retain the `homeAccountId` used by `RedisPartitionManager`, the account object required by frontend silent acquisition, and the `username` currently used by backend token lookup. Remove unrelated authentication-derived fields only after checking all consumers; never enrich the account object with third-party resource responses.

## Partitioning and access granularity

Keep `msal:<homeAccountId>`, `linkedin:<sub>`, and `session:<id>` names. The client identifier is application configuration, not part of each LinkedIn partition key. This assumes environment/cache isolation and one LinkedIn application per namespace; changing the application registration requires invalidating its old cache. Server sessions reference provider partitions for frontend requests and backend Socket.IO lookup. Track identity/access token expirations independently; retain refresh tokens only when issued and needed. Cache retention cannot extend token validity.

Preserve Redis JavaScript Object Notation (JSON) session path operations. Encrypt/decrypt each protected field or subdocument at its existing access boundary; selective reads need not decrypt the whole session. Whole-session readers decode protected units too. Audit deeper-path reads/writes before placing a parent behind an envelope. Preserve caller-facing object shapes, cache expiry, and concurrent writes; do not persist decrypted duplicates.

MSAL adapters read/write complete serialized caches: decrypt before deserialization and encrypt after serialization, without depending on the library's internal token-field schema. Frontend wrappers and backend direct Redis consumers must agree on both whole-record and subdocument handling.

## Encryption format

Use Advanced Encryption Standard in Galois/Counter Mode with a 256-bit key (AES-256-GCM) and the same environment-specific key in both server runtimes. Use established libraries and the same envelope:

| Field | Meaning |
| --- | --- |
| `version` | Envelope-format version |
| `key-version` | Key Vault secret version selecting the decryption key |
| `nonce` | Fresh cryptographically random 12-byte value per encryption; never reuse with the same key |
| `ciphertext` | Encrypted data |
| `tag` | Mandatory 16-byte authentication tag generated and verified by the library |

Encode binary fields as Base64. Version identifiers and nonces are not secrets. Bind the full Redis key, canonical subdocument path/purpose, envelope version, and key version through consistently encoded associated data. This prevents moving ciphertext between accounts, providers, or protected fields.

Verify the tag before consuming any plaintext; wrong keys, tampering, or changed associated data must fail. Libraries that append the tag to ciphertext must split/recombine it consistently at the envelope boundary. Cross-runtime tests establish compatibility. Keys remain in server memory, outside Redis/PostgreSQL and browser-visible data.

## Key generation and startup configuration

- Generate a cryptographically random 32-byte symmetric key in `infrastructure/security.tf` and store its Base64 representation as the Key Vault **secret** `auth-cache-encryption-key`. The same key encrypts and decrypts. Share it between the frontend server and backend for permitted authentication-cache data within one environment; keep separate keys for development, testing, staging, and production and for unrelated future encryption/signing purposes.
- OpenTofu owns rotation. An explicit non-secret rotation revision changes the generated key; unrelated infrastructure updates preserve it. Update the value under the same secret name so previous secret versions remain available. Do not delete/recreate the secret to rotate it. Generated secrets can appear in infrastructure state and saved plans; protect those artifacts and do not print secret values.
- Give only the frontend/backend application identities the additional secret `List` permission required for this feature, alongside their existing `Get`; leave other identities unchanged. These two permission additions are recorded in `security.tf`; this document does not establish deployment status. Under the existing vault access policies, `List` exposes vault-wide secret metadata, not secret values by itself.
- At startup, fetch the latest secret, enumerate all pages of version metadata, and determine the immediately preceding version by creation time. Do not rely on listing order or sort opaque version identifiers. Fetch the previous value using its exact version. If creation times cannot establish a unique predecessor, fail with a configuration error rather than guess. Rotation must not run concurrently with startup discovery; detect a changed latest version and retry the snapshot if necessary.
- Keep `encryption_key`, `previous_encryption_key`, and their version identifiers in memory, following each application's field-naming conventions. Versions come from Key Vault metadata; they require no additional Key Vault secrets or deployment environment variables. `config.ts` uses `getSecret` and `listPropertiesOfSecretVersions`; `config.py` uses `get_secret` and `list_properties_of_secret_versions`. Reuse a client within the loading operation.
- The first generation has no previous key: use `undefined`/`None`. A permission, network, disabled-version, or malformed-key error is not equivalent to an absent predecessor. Validate decoded key lengths and fail configuration loading if required material cannot be loaded; do not copy the backend `get_variable()` helper's catch-all empty-string fallback for encryption keys. Do not skip an unavailable immediate predecessor and silently choose an older version.
- Local development/test configuration supplies current/optional previous keys and matching non-secret version labels through the existing environment-variable setup, using only synthetic keys in fixtures. No new scripts or workflows are required. Keep configuration initialization compatible with frontend builds and backend test/worker imports.
- New records use the current key. Readers select the in-memory key by the record's `key-version`; unknown versions produce a controlled cache/authentication failure, never an arbitrary on-demand Key Vault lookup. Redis versions select keys during reads; `List` separately discovers the predecessor at startup. There are no Key Vault requests per cache operation.

## Routine rotation and deployment

- Use the existing infrastructure-success triggers for the frontend/backend deployment workflows. For production rotation, approve and complete the backend deployment before approving the frontend deployment. When adding the secret-generation resource, put this reminder beside it in `security.tf`.
- The user accepts temporary authentication failures, including affected existing sessions, while old and new processes overlap. Backend-first ordering reduces some incompatibilities but does not make rotation atomic: a new backend can write records the old frontend cannot decrypt. Applications must recover through normal cache/authentication failure handling; never bypass verification. A separate preparation deployment for zero interruption is not required.
- Keep the previous version enabled and readable until every record encrypted with it has expired or been re-encrypted. Retaining a current and previous key only works if another rotation does not strand records from two generations earlier. Count retention from the last write by an old process, including remaining replicas, and account for session metadata as well as provider-cache expiry. Do not rotate again before that boundary unless deliberately accepting cache invalidation and fresh login.
- Secret changes do not update keys already in process memory; both application deployments must complete to adopt them. Rolling back to processes that loaded only older keys can require deliberate authentication-cache invalidation. This routine key rotation is separate from the initial plaintext-to-encrypted format migration, which still requires compatible readers before encrypted writers.

## Initial encryption rollout

Deploy compatible readers on every instance before enabling encrypted writers. Retire temporary plaintext compatibility after migration/expiry; malformed encrypted data must never be interpreted as legacy plaintext. Missing required keys or failed authentication tags never permit plaintext fallback. Rollback after encrypted writes requires compatible readers or deliberate authentication-cache invalidation and fresh login, never persisted decrypted tokens.

## Performance measurement

Benchmark synthetic representative payloads in both runtimes in the test environment. Measure encryption and decryption separately, report payload sizes, sample counts, warm-up conditions, median, 95th/99th percentiles and observed maximum. Measure both cryptographic work and added serialization/envelope overhead; report Redis network time and complete `set()`/`get()` timings separately. Notify the user of measured encryption/decryption overhead above 50 microseconds, including tail observations, for their acceptance decision. This is a reporting threshold, not an automatic failure limit or permission to omit encryption. No deployment-specific timing has been measured; remove unverified microsecond performance claims.

## References

- [Authenticated encryption](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM): nonce requirements, authentication tags, and rejection of modified ciphertext.
- [Key Vault JavaScript secret versions](https://learn.microsoft.com/en-us/azure/key-vault/secrets/javascript-developer-guide-get-secret) and [Python SecretClient](https://learn.microsoft.com/en-us/python/api/azure-keyvault-secrets/azure.keyvault.secrets.secretclient?view=azure-python): version-specific retrieval and metadata listing permissions.
