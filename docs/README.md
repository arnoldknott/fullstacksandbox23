# Repository documentation

Use this index to find the repository's component references and cross-cutting architecture contracts. For contributor conventions and the development/test environment workflow, start with the root [README](../README.md) and [AGENTS.md](../AGENTS.md). The nested [backend](../backend/AGENTS.md), [frontend](../frontend_svelte/AGENTS.md), and [infrastructure](../infrastructure/AGENTS.md) guides contain area-specific commands and practices.

## Components and services

- [Backend](backend/README.md) — FastAPI interfaces, data-access layers, and backend guidance.
- [Frontend Svelte](frontend_svelte/README.md) — SvelteKit routes, session handling, and real-time client architecture.
- [Infrastructure](infrastructure/README.md) — OpenTofu configuration and environment model.
- [PostgreSQL](postgres/README.md) — database ownership and schema migration workflow.
- [Redis](redis/README.md) — session/cache partitions, encryption scope, and performance measurements.
- [pgAdmin](pgadmin/README.md) — optional PostgreSQL administration interface.

## Cross-cutting architecture

- [Architecture overview](architecture/README.md) — links to repository-wide system concerns.
- [Security](architecture/security/README.md) — authentication, authorization boundaries, session transport, and data-storage contracts. Focused references cover [inner access control](architecture/security/inner-access-control.md), [collection child loading](architecture/security/collection-child-loading.md), [multi-provider session authorization](architecture/security/multi-provider-session-authorization.md), [account linking and merge](architecture/security/linkedin-azure-account-merge-plan.md), and the [session lifecycle](architecture/security/authentication-session-lifecycle-plan.md).
- [Data transfer](architecture/data-transfer/README.md) — data-transfer architecture, including [REST snapshots and incremental Socket.IO updates](architecture/data-transfer/internal/rest-snapshot-incremental-socketio.md).
- [Docker](architecture/docker/README.md) — Compose and development-container overview.
- [Scripts](architecture/scripts/README.md) — supported repository automation entry points.
- [Git](architecture/git/README.md) — repository branch and source-control workflow.
- [VS Code](architecture/vscode/README.md) — workspace and devcontainer setup.
