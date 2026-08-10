# Frontend agent guidance

Applies to everything under `frontend_svelte/`.

See the repository root `AGENTS.md` for shared conventions (branching, test-environment lifecycle, cross-app integration contracts).

## Validation: format, lint and test commands

Use the package scripts from `frontend_svelte/package.json` when working directly in the app directory:

- `bun format`
- `bun lint`
- `bun check`
- `bun test:unit`
- Single test file: `bun test:unit -- src/components/Guard.spec.ts`

**Interactive shortcut for developers:** run `./scripts/enter_frontend_svelte_test.sh` from the repo root to build, start the test stack, and drop into the `frontend_svelte` container shell where you can run `bun lint`, `bun check`, `bun test:unit`, etc. directly.

To mirror the repository's containerized workflow non-interactively (used by CI and coding agents), run the commands inside the `frontend_svelte` Compose service from the repo root:

- Start the service: `docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env up frontend_svelte -d`
- Lint: `docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env exec -T frontend_svelte sh -lc "bun lint"`
- Check: `docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env exec -T frontend_svelte sh -lc "bun check"`
- Unit tests: `docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env exec -T frontend_svelte sh -lc "bun test:unit"`
- Single test file: `docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env exec -T frontend_svelte sh -lc "bun test:unit -- src/components/Guard.spec.ts"`
- Build: `docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env exec -T frontend_svelte sh -lc "bun run build"`

The `--env-file backend/src/tests/.env` flag is required; without it compose will not resolve the test-stack environment variables. The scripts under `scripts/` already pass this flag for you.

- Use `backend/src/.env.example` as the reference for the required local env surface.

## Build command

Use the same docker compose handling as for validation

- Start the service: `docker compose -f compose.yml -f compose.override.test.yml up frontend_svelte -d`
- Build: `docker compose -f compose.yml -f compose.override.test.yml exec -T frontend_svelte sh -lc "bun run build"`

## High-level architecture

- This frontend is a SvelteKit app with a Node adapter. The root server load in `frontend_svelte/src/routes/+layout.server.ts` constructs `backendAPIConfiguration` and exposes session data to the entire app.
- Route groups are important. `src/routes/(layout)` is the main authenticated application shell with sidebar, theming, and account UI. `src/routes/(plain)` is the stripped-down shell used for docs/session flows. Nested `(protected)` and `(admin)` groups are enforced centrally in `src/hooks.server.ts`.
- Authentication/session state is split across Redis, cookies, and local storage. `src/hooks.server.ts` reads a bearer token or `session_id` cookie, loads the session from Redis, and guards protected routes. `src/routes/+layout.svelte`, `src/routes/(plain)/session/+server.ts`, and `src/hooks.client.ts` implement the iframe/embed flow that restores a cookie-backed server session from `localStorage`.
- Server-side backend access goes through `src/lib/server/apis/base.ts` and `src/lib/server/apis/backendApi.ts`. Those wrappers are responsible for token acquisition and consistent REST API scope/header handling.
- Real-time updates use `src/lib/socketio.svelte.ts`. Components/routes provide accessors for their current entity arrays and edit-id sets, while `SocketIO` mutates those collections in place to keep Svelte reactivity working as expected.
- Theming is centralized in `src/routes/(layout)/+layout.svelte` and `src/lib/theming.ts`. The `theme` store only holds the computed theme object; the heavy Material/FlyonUI theme generation logic lives in `theming.ts`.
- Shared application types live in `src/lib/types.d.ts`. Access-control logic is centralized in `src/lib/accessHandler.ts`, and many dashboard routes rely on those shared types and permission helpers.
- `src/routes/(layout)/playground/` hosts several examples of completed and work in progress elements for the desin, and layout of pages and components as well as theri styling.
- `src/routes/(layout)/(protected)/` acts as a development playground for integration with backend-driven real-time data and access control. It is protected by user authentication and sends the access tokens to the backend. It integrates with various other services, such as Microsoft Graph. It has examples of many patterns used across the app, so it is a good reference when building new pages and features.

## Key conventions

- Use Svelte 5 rune syntax in new Svelte files. Existing components/routes consistently use `$props`, `$state`, `$derived`, and `$effect`.
- Use ES6 module syntax and features in `.ts` and `.svelte` files. The app is built on Bun, so top-level await, ES modules, and Bun's polyfilled APIs are all available.
- Prefer route-group protection over ad hoc auth checks. If a page must require authentication or admin access, place it under `(protected)` or `(admin)` so `hooks.server.ts` enforces it.
- On the client, session data is expected at `page.data.session`. On the server, it is expected at `locals.sessionData`. Reuse those surfaces instead of adding a separate session store.
- When calling the backend or thrid party Application Programable Interfaces from server loads/actions, use `backendAPI` or the relevant counterparts from `lib/server` instead of raw `fetch` so OAuth scopes and auth headers stay aligned with the rest of the app.
- `backendAPIConfiguration` is passed through Svelte context from the root layout. Client-side utilities such as `SocketIO` expect that context to exist; do not bypass it with hard-coded URLs.
- Keep shared domain types in `src/lib/types.d.ts` when they are reused across routes, components, and server helpers. This repository relies on those shared types heavily.
- When wiring socket-driven pages, preserve the existing mutate-in-place pattern for entity arrays. Several pages rely on that instead of replacing arrays wholesale.
- Logging in the layers security, cache and integrations use emoji-prefixed messages `🔑`, `🥞`, `🚪` respectively, and `🔥` for errors. Match that local style when adding logs near those systems.
- For debug printing use two lines, where the first line marks the origin of the console
  output, framed by "===", and the second line prints the relevant data. Never combine them, unless explicitly asked for. For example:

```
console.log("🔑 === playground - design - flyonui - page - <function name> - <variable name> ===");
console.log({ myVariable });
```

- When refactoring never delete comments in the code that is being refactored, unless the comment is no longer relevant. If the comment is relevant but needs to be updated, update it instead of deleting it. If the comment is not relevant, but you are not sure if it is safe to delete it, leave it in place and add a TBD comment with your question for the next developer who works on the code.

## Frontend test organization

Reusable frontend test support lives under `frontend_svelte/src/test/` using
the Testing Library / Vitest / common JS conventions:

- `src/test/` (top level) — composed render helpers (e.g. `renderSocketIO.ts`)
  that wire context, props, mocks, and factories together. Mirrors Testing
  Library's `test-utils/index.ts` convention.
- `src/test/helpers/` — small reusable test-only utilities and Svelte
  **wrapper** components that mount a system-under-test inside a real Svelte
  runtime (e.g. `SocketIOWrapper.svelte`). Use the term `wrapper` for test-only
  Svelte components that host a system under test.
- `src/test/factories/` — typed object factories (e.g. `createDemoResource`)
  that build domain entities for tests with sensible defaults plus overrides.
- `src/test/mocks/` — shared `vi.mock` / `vi.fn` setup helpers and stand-ins
  for external modules.
- `src/test/fixtures/` — static test data or Vitest `test.extend` fixtures.

Conventions:

- Specs live next to the production code as `*.spec.ts` (component specs in
  `src/components/`, library specs in `src/lib/`). Vitest is configured to
  pick up `src/**/*.{test,spec}.{js,ts}`.
- Provide Svelte context to a wrapper through Testing Library's `context`
  render option (`render(Wrapper, { context: new Map([...]) })`) instead of
  calling `setContext` inside the wrapper, so the wrapper stays minimal.
- For modules that must be replaced before any production code imports them
  (e.g. `socket.io-client`), declare `vi.mock(...)` at module top level in the
  spec and define the mock state inside `vi.hoisted(...)` — hoisted code runs
  before imports resolve, so it cannot import from `src/test/mocks/`.
- **Production code must not import from `src/test/`.** Tests may freely
  import from `$lib`, components, or other production paths.
