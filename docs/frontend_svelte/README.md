# Frontend Svelte

The [frontend_svelte](../../frontend_svelte/) application uses SvelteKit for server-rendered routes and browser interactions. Keep server-only credentials, provider tokens, and backend calls on the server; browser components receive only the page data and client configuration they need.

## Runtime map

- `src/hooks.server.ts` loads the Redis-backed session and enforces the protected and admin route groups.
- `src/routes/` contains SvelteKit pages, server loads/actions, and route-group boundaries. The root layout constructs shared backend API configuration.
- `src/lib/server/` contains server-only API wrappers, OAuth providers, configuration, and Redis access. Backend requests should use the shared API wrappers so application credentials and session headers stay consistent.
- `src/lib/` contains shared domain types, access helpers, client session behavior, entity containers, and Socket.IO integration.
- `src/components/` contains reusable UI components; reusable test support is under `src/test/`.

## Session and live data

The server stores provider credentials in Redis and associates them with the application session. Protected routes use the shared session checks rather than adding independent authentication logic. REST snapshots seed the frontend entity container; Socket.IO adds authorized subscriptions, cursor replay, and subsequent mutations. See [REST snapshots and incremental Socket.IO](../architecture/data-transfer/internal/rest-snapshot-incremental-socketio.md) and the [security architecture](../architecture/security/README.md) for the cross-service contracts.

## Development and validation

Use [frontend_svelte/AGENTS.md](../../frontend_svelte/AGENTS.md) for route conventions, test organization, and the required test-container commands. Tests are colocated with the production code; shared render helpers, factories, mocks, and fixtures belong under `src/test/`. Production modules must not import from that test-support directory.
