---
applyTo: "backend/**"
---

## Build, test, and lint commands

There are no backend package scripts. The backend uses `uv` plus Docker Compose.

From `backend/` directly:

- Update the dev environment: `uv sync --frozen --extra dev`
- Format check: `uv run black --check .`
- Lint: `uv run ruff check .`
- Full test suite: `uv run pytest -vv`
- Single test: `uv run pytest -vv src/core/tests/test_security.py::test_get_azure_jwks`

**Interactive shortcut for developers:** run `./scripts/enter_backend_test.sh` from the repo root to build, start the test stack, and drop into the `backend_api` container shell where you can run `uv run pytest -vv `, `uv run black --check .`, etc. directly.

To mirror CI and the devcontainer non-interactively (used by CI and coding agents) from the repo root:

- Build the backend image: `docker compose -f compose.yml -f compose.override.test.yml build backend_api`
- Start the backend test stack: `docker compose -f compose.yml -f compose.override.test.yml up -d postgres redis backend_api`
- Format/lint in container: `docker compose -f compose.yml -f compose.override.test.yml exec -T backend_api sh -lc "uv run black --check . && uv run ruff check ."`
- Full tests in container: `docker compose -f compose.yml -f compose.override.test.yml exec -T backend_api sh -lc "uv run pytest -vv"`
- Single test in container: `docker compose -f compose.yml -f compose.override.test.yml exec -T backend_api sh -lc "uv run pytest -vv src/core/tests/test_security.py::test_get_azure_jwks"`

Notes from the current baseline:

- The reliable backend entrypoint is `uv run ...`; bare `black`, `ruff`, and `pytest` were not available on the shell PATH in the running container.
- The backend image build succeeds.
- Backend pytest collection currently depends on the backend environment being populated first. `backend/src/core/config.py` eagerly parses values such as `REDIS_PORT` at import time, so missing or blank env values break test collection before tests run.
- Use `backend/src/.env.example` as the reference for the required local env surface.

## High-level architecture

- The backend entrypoint is `backend/src/main.py`. It creates `fastapi_app`, runs migrations during lifespan startup, mounts REST routes at `/api/v1`, mounts Socket.IO at `/socketio/v1`, and mounts websocket routes at `/ws/v1`.
- `backend/src/core/fastapi.py` is the router/middleware assembly point. It wires CORS, then mounts the resource/identity/access/core routers and applies top-level scope/role dependencies to selected routers.
- Authentication and authorization are centralized in `backend/src/core/security.py`. It validates Azure JWTs, caches Microsoft JWKS in Redis, loads cached MSAL tokens by session id, and provides the guard/dependency helpers used by both HTTP and Socket.IO flows.
- Real-time infrastructure is centralized in `backend/src/core/socketio.py`. It configures the Socket.IO server with an `AsyncRedisManager` and registers all namespaces from `routers/socketio/v1`.
- CRUD behavior is centralized in `backend/src/crud/base.py`. Each CRUD class uses async sessions, integrates access-policy and access-log CRUDs, and detects whether a model belongs to the resource or identity hierarchy. All database interaction from REST-API views and Socket.IO namespaces must use CRUD classes that inherit from `BaseCRUD`.
- Model/schema generation is centralized in `backend/src/models/base.py`. The repository relies on `create_model(...)` to produce the SQLModel table plus matching `.Create`, `.Read`, `.Update`, and `.Extended` schemas.
- HTTP route modules such as `backend/src/routers/api/v1/demo_resource.py` are intentionally thin. They usually instantiate `BaseView(CRUDClass)` and use `Depends(Guards(...))` plus `get_http_access_token_payload`.
- Socket.IO namespace modules inherit from `backend/src/routers/socketio/v1/base.py::BaseNamespace`, declare event guards, optionally wire a CRUD class and read/update models, and authenticate via Redis-backed session data rather than per-event bearer tokens.
- Background work hangs off Celery (`backend/src/core/celery_app.py`) with task modules under `backend/src/jobs/`.

## Key conventions

- Shared enums and guard types in `backend/src/core/types.py` drive much of the backend design. Resource names, identity names, access actions, and guard handling are reused across models, CRUD, routers, and socket namespaces.
- When adding a new CRUD-backed entity, expect coordinated changes across `models/`, `crud/`, `routers/api/v1/`, and sometimes `routers/socketio/v1/`. The layers are intentionally parallel.
- Prefer the repository's `BaseView` + CRUD pattern for HTTP endpoints instead of hand-rolling route logic. Authorization is expected to flow through `Guards(...)`, `get_http_access_token_payload`, and `check_token_against_guards(...)`.
- Prefer the `create_model(...)` factory and the generated `.Create`/`.Read`/`.Update`/`.Extended` schemas over writing parallel schema classes by hand unless the existing pattern clearly cannot express the model.
- Backend tests live under `backend/src/**/tests/`, not a top-level `backend/tests/` tree. Use file paths from `src/.../tests/...` for single-test invocations.
- Write unit tests for everything security related, such as authenticatio, authorization, and access control logic. Use the existing `test_security.py` as a reference for style and coverage of auth-related tests. Also for any interfaces exposed by the backend, such as REST endpoints and Socket.IO events, write tests that cover both successful and unsuccessful authorization scenarios to ensure that access control is working as intended.
- The backend imports `config` eagerly in many modules. If you add new config fields, keep in mind that import-time parsing affects app startup, test collection, and background workers.
- Socket.IO authentication depends on the Redis-backed server session cache. Reuse the existing session-id/token-cache flow instead of inventing a separate websocket auth mechanism.
- Logging already uses subsystem-specific emoji markers such as `🔑` for security/auth, `🧦` for Socket.IO, `💨` for FastAPI startup, and `📄` for config. Match that style when touching those layers.
- For debug printing, use two lines where the first line marks the origin of the console output and the second line prints the relevant data. For example:

```
print("🔑 routes - api - v1 identities - get user by id")
print(f"token payload: {token_payload}", flush=True)
```

and for longer data structures:

```
print("🔑 routes - api - v1 identities - get user by id")
pprint(f"token payload: {token_payload}")
```
