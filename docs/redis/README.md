# Redis

Redis supports cached sessions and tokens, Socket.IO coordination, and Celery transport. Runtime configuration and access-control-list templates live in [cache](../../cache/); service wiring follows the application and Docker Compose configuration.

This document owns Redis-specific partitions, protected session/cache boundaries, and performance measurements. The [security architecture](../architecture/security/README.md#application-encryption) owns the application-wide encryption format, keyring, startup, and rotation contract. Follow the [data-storage policy](../architecture/security/README.md#data-storage-policy) to decide what may be retained; encryption never makes prohibited third-party resource data eligible for storage. Implementation stages and tests are tracked in [Stage F](../architecture/security/linkedin-account-linking-plan.md#f-encrypted-cache-persistence).

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

## Performance measurement

Benchmark synthetic representative payloads in both runtimes in the test environment. Measure encryption and decryption separately, report payload sizes, sample counts, warm-up conditions, median, 95th/99th percentiles and observed maximum. Measure both cryptographic work and added serialization/envelope overhead; report Redis network time and complete `set()`/`get()` timings separately. Notify the user of measured encryption/decryption overhead above 50 microseconds, including tail observations, for their acceptance decision. This is a reporting threshold, not an automatic failure limit or permission to omit encryption.

Measurements from the isolated test containers on 2026-09-26 include JavaScript Object Notation serialization, Base64 conversion, envelope construction/parsing, and AES-256-GCM. Each runtime used 1,000 warm-up iterations and 10,000 measured samples:

| Runtime | Payload | Operation | Median | 95th | 99th | Maximum |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Python | 1,390 bytes | encrypt | 7.79 µs | 14.38 µs | 20.88 µs | 221.62 µs |
| Python | 1,390 bytes | decrypt | 5.50 µs | 6.96 µs | 12.46 µs | 65.17 µs |
| Python | 8,558 bytes | encrypt | 29.92 µs | 110.79 µs | 367.58 µs | 1,258.38 µs |
| Python | 8,558 bytes | decrypt | 20.08 µs | 28.75 µs | 35.96 µs | 360.17 µs |
| Python | 33,134 bytes | encrypt | 149.92 µs | 698.08 µs | 1,080.58 µs | 3,762.46 µs |
| Python | 33,134 bytes | decrypt | 78.52 µs | 110.79 µs | 374.71 µs | 711.75 µs |
| TypeScript | 1,390 bytes | encrypt | 3.71 µs | 27.54 µs | 304.17 µs | 5,763.46 µs |
| TypeScript | 1,390 bytes | decrypt | 5.75 µs | 12.29 µs | 19.08 µs | 2,415.38 µs |
| TypeScript | 8,558 bytes | encrypt | 12.29 µs | 115.25 µs | 438.79 µs | 4,149.50 µs |
| TypeScript | 8,558 bytes | decrypt | 24.25 µs | 59.29 µs | 88.21 µs | 2,199.92 µs |
| TypeScript | 33,134 bytes | encrypt | 36.67 µs | 614.71 µs | 1,270.58 µs | 3,051.83 µs |
| TypeScript | 33,134 bytes | decrypt | 98.75 µs | 349.33 µs | 976.13 µs | 3,337.50 µs |

Redis timings used the 8,558-byte payload, 100 warm-up iterations, and 1,000 measured samples from the Python backend container. Plain RedisJSON network/serialization time and the complete encrypted operation were measured separately:

| Operation | Median | 95th | 99th | Maximum |
| --- | ---: | ---: | ---: | ---: |
| Plain Redis `set()` | 101.83 µs | 138.71 µs | 397.25 µs | 1,368.17 µs |
| Plain Redis `get()` | 106.12 µs | 142.75 µs | 343.96 µs | 995.71 µs |
| Complete encrypted `set()` | 151.04 µs | 197.96 µs | 548.92 µs | 1,538.33 µs |
| Complete encrypted `get()` | 136.17 µs | 183.04 µs | 478.67 µs | 979.08 µs |

The 50-microsecond reporting threshold is exceeded for large-payload medians and for several 95th/99th-percentile and maximum observations. For the representative 8,558-byte Redis case, the measured median increase was 49.21 µs for `set()` and 30.05 µs for `get()`.
