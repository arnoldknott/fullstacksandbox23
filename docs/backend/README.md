# Backend

The [backend](../../backend/) is a FastAPI application that exposes REST, Socket.IO, and WebSocket interfaces. Its entry point is [`src/main.py`](../../backend/src/main.py); it mounts REST routes under `/api/v1`, Socket.IO under `/socketio/v1`, and WebSocket routes under `/ws/v1`.

## Code map

- `src/core/` assembles application middleware and routing, configuration, database sessions, security, and Socket.IO infrastructure.
- `src/models/` defines SQLModel tables and generated request/response schemas. `create_model(...)` in `models/base.py` is the shared model factory.
- `src/crud/` owns database operations. Application CRUD classes inherit from `BaseCRUD`, which applies shared access-policy and access-log behavior.
- `src/routers/` contains the REST, Socket.IO, and WebSocket interfaces. REST views and Socket.IO namespaces should delegate persistence and access checks to CRUD classes.
- `src/jobs/` contains Celery tasks; `src/migrations/` contains the Alembic migration trees.

## Request and access flow

`core/fastapi.py` mounts the API routers. Outer security validates a provider identity and evaluates endpoint or event guards; CRUD access policies then control which application resources that identity may use. Passing a guard does not grant resource access. See the [security architecture](../architecture/security/README.md) for the admission boundary and [inner access control](../architecture/security/inner-access-control.md) for resource permissions.

For collection views, REST provides the initial authorized snapshot and cursor. The frontend then subscribes through Socket.IO for authorized replay and incremental changes; this contract is described in [REST snapshots and incremental Socket.IO](../architecture/data-transfer/internal/rest-snapshot-incremental-socketio.md).

## Development and validation

Use [backend/AGENTS.md](../../backend/AGENTS.md) for environment setup, required test-container commands, and single-test examples. Use the [PostgreSQL guide](../postgres/README.md#schema-migration-workflow) for the supported migration workflow. Backend tests live under `backend/src/**/tests/` and should be run in the repository test environment.
