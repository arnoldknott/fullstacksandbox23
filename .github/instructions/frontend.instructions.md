---
applyTo: "frontend_svelte/**"
---

## Build, test, and lint commands

Use the package scripts from `frontend_svelte/package.json` when working directly in the app directory:

- `bun run build`
- `bun lint`
- `bun check`
- `bun test:unit`
- Single test file: `bun test:unit -- src/components/Guard.spec.ts`

**Interactive shortcut for developers:** run `./scripts/enter_frontend_svelte_test.sh` from the repo root to build, start the test stack, and drop into the `frontend_svelte` container shell where you can run `bun lint`, `bun check`, `bun test:unit`, etc. directly.

To mirror the repository's containerized workflow non-interactively (used by CI and coding agents), run the commands inside the `frontend_svelte` Compose service from the repo root:

- Start the service: `docker compose -f compose.yml -f compose.override.test.yml up frontend_svelte -d`
- Lint: `docker compose -f compose.yml -f compose.override.test.yml exec -T frontend_svelte sh -lc "bun lint"`
- Check: `docker compose -f compose.yml -f compose.override.test.yml exec -T frontend_svelte sh -lc "bun check"`
- Unit tests: `docker compose -f compose.yml -f compose.override.test.yml exec -T frontend_svelte sh -lc "bun test:unit"`
- Single test file: `docker compose -f compose.yml -f compose.override.test.yml exec -T frontend_svelte sh -lc "bun test:unit -- src/components/Guard.spec.ts"`
- Build: `docker compose -f compose.yml -f compose.override.test.yml exec -T frontend_svelte sh -lc "bun run build"`

Notes from the current baseline:

- `bun run build` succeeds in the container, but bare `bun build` is the Bun bundler and is the wrong command for this app.
- `bun check` currently exits non-zero because the codebase already has many existing Svelte rune warnings (`state_referenced_locally`), so do not assume that failure was introduced by your change.

## High-level architecture

- This frontend is a SvelteKit app with a Node adapter. The root server load in `frontend_svelte/src/routes/+layout.server.ts` constructs `backendAPIConfiguration` and exposes session data to the entire app.
- Route groups are important. `src/routes/(layout)` is the main authenticated application shell with sidebar, theming, and account UI. `src/routes/(plain)` is the stripped-down shell used for docs/session flows. Nested `(protected)` and `(admin)` groups are enforced centrally in `src/hooks.server.ts`.
- Authentication/session state is split across Redis, cookies, and local storage. `src/hooks.server.ts` reads a bearer token or `session_id` cookie, loads the session from Redis, and guards protected routes. `src/routes/+layout.svelte`, `src/routes/(plain)/session/+server.ts`, and `src/hooks.client.ts` implement the iframe/embed flow that restores a cookie-backed server session from `localStorage`.
- Server-side backend access goes through `src/lib/server/apis/base.ts` and `src/lib/server/apis/backendApi.ts`. Those wrappers are responsible for token acquisition and consistent REST API scope/header handling.
- Real-time updates use `src/lib/socketio.ts`. Components/routes provide accessors for their current entity arrays and edit-id sets, while `SocketIO` mutates those collections in place to keep Svelte reactivity working as expected.
- Theming is centralized in `src/routes/(layout)/+layout.svelte` and `src/lib/theming.ts`. `themeStore` only holds the computed theme object; the heavy Material/FlyonUI theme generation logic lives in `theming.ts`.
- Shared application types live in `src/lib/types.d.ts`. Access-control logic is centralized in `src/lib/accessHandler.ts`, and many dashboard routes rely on those shared types and permission helpers.
- `src/routes/(layout)/playground/` hosts several examples of completed and work in progress elements for the desin, and layout of pages and components as well as theri styling.
- `src/routes/(layout)/(protected)/dashboard/` acts as a development playground for integration with backend-driven real-time data and access control. It is protected by user authentication and sends the access tokens to the backend. It integrates with various other services, such as Microsoft Graph. It has examples of many patterns used across the app, so it is a good reference when building new pages and features.

## Key conventions

- Use Svelte 5 rune syntax in new Svelte files. Existing components/routes consistently use `$props`, `$state`, `$derived`, and `$effect`.
- Prefer route-group protection over ad hoc auth checks. If a page must require authentication or admin access, place it under `(protected)` or `(admin)` so `hooks.server.ts` enforces it.
- On the client, session data is expected at `page.data.session`. On the server, it is expected at `locals.sessionData`. Reuse those surfaces instead of adding a separate session store.
- When calling the backend from server loads/actions, use `backendAPI` instead of raw `fetch` so OAuth scopes and auth headers stay aligned with the rest of the app.
- `backendAPIConfiguration` is passed through Svelte context from the root layout. Client-side utilities such as `SocketIO` expect that context to exist; do not bypass it with hard-coded URLs.
- Keep shared domain types in `src/lib/types.d.ts` when they are reused across routes, components, and server helpers. This repository relies on those shared types heavily.
- When wiring socket-driven pages, preserve the existing mutate-in-place pattern for entity arrays. Several pages rely on that instead of replacing arrays wholesale.
- Logging in the auth/session/cache layers uses emoji-prefixed messages such as `🔑`, `🥞`, `🚪`, and `🔥`. Match that local style when adding logs near those systems.
- For debug printing use two lines, where the first line marks the origin of the conosle output and the second line prints the relevant data. For example:

```
console.log("🔑 playground - design -flyonui - page - <function name>);
console.log({ myVariable });
```
