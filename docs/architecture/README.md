# Architecture

These documents describe contracts that cross application directories or runtime services. Component-specific structure and commands live in the component guides; repository-wide conventions and security boundaries are defined in the root [AGENTS.md](../../AGENTS.md).

## Topics

- [Data transfer](data-transfer/README.md) — how internal application state is delivered and updated across services.
- [Security](security/README.md) — authentication and outer admission, inner access control, session transport, and permitted data storage.
- [Docker](docker/README.md) — Compose stacks and the development-container boundary.
- [Scripts](scripts/README.md) — repository-level automation entry points.
- [Git](git/README.md) — branch promotion and environment mapping.
- [VS Code](vscode/README.md) — devcontainer and workspace guidance.

When documents cover adjacent concerns, follow their stated ownership: for example, security owns the application-wide encryption contract, while the Redis guide owns Redis partitions and cache-specific handling.
