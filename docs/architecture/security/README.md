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

## Data-storage policy

This is the repository-wide policy for integrations, independent of where data would be stored:

- For third-party data, retain only authentication-derived tokens, authentication-library account metadata, and validated claims needed to authorize calls to the internal backend or external Application Programming Interfaces (APIs). Apply the [Redis encryption contract](../../redis/README.md#encryption-scope), including its explicit identifier exceptions. Keep credentials server-side.
- Responses obtained by authorized third-party resource calls, including Microsoft Graph `/me` and LinkedIn `/v2/userinfo`, may exist only in transient application memory for processing/display. This covers selected fields, names, emails, pictures, picture URLs, avatars, downloaded media, and derived copies.
- Never persist that resource data in Redis, databases, files, logs, telemetry, durable queues, browser storage, service-worker caches, or other application-controlled storage, even encrypted. Use non-caching Hypertext Transfer Protocol (HTTP) fetch/response behavior. Do not enrich persisted authentication metadata or sessions with resource responses.
- Fetch resource data when needed. If request volume becomes an issue, fetch less and defer retrieval until the consuming frontend elements are activated; do not add persistent profile caches as a workaround.
- First-party application records/settings and minimal verified identifiers linking provider identities to internal users remain permitted. Do not relabel third-party response data as first-party data. Redis encryption does not introduce database encryption into this task.
- Use synthetic third-party data in stored test fixtures. When modifying an integration, remove conflicting persistence from the affected flow instead of reproducing it.

## Implementation plans

- [LinkedIn authentication and credential encryption](linkedin-account-linking-plan.md) — provider/guard contracts, endpoint matrix, code mappings, stages, and validation.
- [Account linking and merge](linkedin-azure-account-merge-plan.md) — verified attachment, settings choices, reference reconciliation, and transactional merging across providers.

The [Redis README](../../redis/README.md) owns the cache/encryption contract and operational details. The plans describe implementation work; they do not imply that planned features are already deployed.
