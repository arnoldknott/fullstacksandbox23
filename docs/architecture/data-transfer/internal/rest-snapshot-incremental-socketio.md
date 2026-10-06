# REST snapshots and incremental Socket.IO

## Current contract

Initial collection state is loaded through REST snapshot endpoints. The frontend seeds its entity containers from those responses, then Socket.IO subscribes to the returned entity identifiers and handles cursor replay and subsequent mutations. Snapshot-aware connections set `snapshot-subscription=true`, which suppresses namespace collection transfer during connection.

## REST snapshots

Snapshot endpoints return an array of extended entity representations and expose the snapshot mutation position in the `X-Entity-Cursor` response header. [BaseCRUD.read_entity_snapshot()](../../../../backend/src/crud/base.py) applies authorization and supports optional parent filtering, metadata enrichment, effective access-right enrichment, and ordering.

Supported first-party collection values are:

- Repeated `include` parameters: `creation-date`, `last-modified-date`, and `access-right`.
- `sort=creation-date`.
- `direction=asc` or `direction=desc`.
- `parent-id=<UUID>` on hierarchical snapshot routes.

Snapshot endpoints currently exist for Presentation, Question, Message, Numerical, DemoResource, ProtectedResource, ProtectedChild, ProtectedGrandChild, UeberGroup, Group, SubGroup, and SubSubGroup.

The SvelteKit server uses [backendAPI.getSnapshot<T>()](../../../../frontend_svelte/src/lib/server/apis/backendApi.ts) to return `{ entities, cursor }` to pages. [SocketIO](../../../../frontend_svelte/src/lib/socketio.svelte.ts) seeds `EntityContainer` state from that object, including available access rights, policies, and hierarchies.

## Socket.IO subscriptions

After connection, the frontend emits `subscribe` events sequentially and waits for each acknowledgement. Each event contains `entity_ids` and may contain `cursor`; batches contain at most 500 identifiers, and the frontend sends the cursor with the final batch. The acknowledgement contains `subscribed` and `rejected` identifier lists, or an `error`.

The backend validates identifiers, filters the requested entity query through the same read authorization used by CRUD operations, and enters only authorized `resource:<UUID>` rooms. When a cursor is supplied, mutation logs newer than that cursor are read for the namespace entity type. Replay on a connection with `parent-id` is limited to that parent's access-controlled children, matching the REST snapshot collection; other parents' entities are neither transferred nor added to resource rooms by replay. Active authorized entities are emitted through `transferred`; snapshot entities deleted after the cursor are emitted through `deleted`. Normal create, update, delete, share, link, and unlink events continue over Socket.IO after subscription.

Authentication expiry, protected-room removal, reauthentication, and reconnect are specified in the [authentication session lifecycle plan](../../security/authentication-session-lifecycle-plan.md). After successful reauthentication, reconnection reuses this document's authorized subscription and cursor-replay path; it does not introduce full collection transfer or a separate recovery stream.

## Security invariants

Client-provided entity identifiers are subscription requests and never grant room membership. Snapshot reads, room subscriptions, replay reads, parent-room entry, and explicit single-entity reads remain access-controlled. Public namespace behavior and authenticated guard behavior continue to use their configured policy and guard paths.

First-party query parameter names and serialized values use kebab-case. Python and TypeScript identifiers remain idiomatic, and externally defined protocol parameters retain their external spelling.

## Load-test protocol

The stage load test in [socketio-load.mjs](../../../../frontend_svelte/tests/stage-stress/socketio-load.mjs) models the production sequence: fetch REST snapshots, read entity identifiers and `X-Entity-Cursor`, connect with `snapshot-subscription=true`, subscribe in batches, wait for acknowledgements, hold connections, and report latency percentiles. It accepts `--users`, `--ramp`, `--hold`, `--timeout`, `--frontend-only`, and `--backend-only`.

It targets the public `34654/e26/introduction` presentation and therefore exercises anonymous snapshot and Socket.IO subscription behavior. It does not authenticate a user or test Socket.IO admission-ticket issuance.

### Configuration and execution

Copy `frontend_svelte/tests/stage-stress/.env.example` to the ignored `.env` file beside it and set the public frontend and backend origins. These values are URLs, not credentials:

```sh
cp frontend_svelte/tests/stage-stress/.env.example frontend_svelte/tests/stage-stress/.env
```

The recommended runner uses an ephemeral frontend test container, does not start the local test stack, and forwards all load-test arguments:

```sh
# Small smoke test
./scripts/socketio_load.sh --users=5 --ramp=5 --hold=10 --timeout=60

# Reference 200-user scenario
./scripts/socketio_load.sh --users=200 --ramp=30 --hold=30 --timeout=120

# Reference 500-user stress scenario
./scripts/socketio_load.sh --users=500 --ramp=30 --hold=30 --timeout=120
```

Use `--frontend-only` to load only the rendered frontend route. The default, or the explicit `--backend-only` flag, loads backend snapshots and opens three Socket.IO connections per simulated user.

It can also run directly inside a devcontainer that has Bun and the frontend dependencies installed:

```sh
cd frontend_svelte
set -a
. tests/stage-stress/.env
set +a
bun run test:stage:load -- --users=5 --ramp=5 --hold=10 --timeout=60
```

### Azure Container Apps live logs

After Azure login, set the workspace and the two non-secret project names used by OpenTofu:

```sh
WORKSPACE=stage
PROJECT_NAME=<project-name>
PROJECT_SHORT_NAME=<project-short-name>
RESOURCE_GROUP="${PROJECT_NAME}-${WORKSPACE}"
```

Stream each application in a separate terminal while the test runs:

```sh
az containerapp logs show \
  --name "${PROJECT_SHORT_NAME}-frontend-${WORKSPACE}" \
  --resource-group "$RESOURCE_GROUP" \
  --type console \
  --follow \
  --tail 100 \
  --format text
```

```sh
az containerapp logs show \
  --name "${PROJECT_SHORT_NAME}-backend-${WORKSPACE}" \
  --resource-group "$RESOURCE_GROUP" \
  --type console \
  --follow \
  --tail 100 \
  --format text
```

Measured stage results on 2026-09-09:

- 200 users over a 30-second ramp: 200/200 snapshot groups succeeded, 600/600 sockets connected, 600/600 subscriptions were acknowledged, and no errors occurred. Snapshot latency was p50 297 ms, p95 976 ms, p99 1162 ms; connection latency was p50 197 ms and p95 1039 ms; subscription latency was p50 100 ms and p95 523 ms.
- 500 users over a 30-second ramp: 500/500 snapshot groups succeeded, 1500/1500 sockets connected, 1500/1500 subscriptions were acknowledged, and no errors occurred. Latency increased as arrivals exceeded immediate processing capacity.
- 200 users after adding 100 Numerical rows: 200/200 snapshot groups succeeded, 600/600 sockets connected, 600/600 subscriptions were acknowledged, and no errors occurred. Snapshot latency was p50 1046 ms, p95 1515 ms, p99 1641 ms, max 1675 ms; connection latency was p50 214 ms and p95 329 ms; subscription latency was p50 167 ms and p95 292 ms.

Measured stage result on 2026-09-29 after the multi-provider session and Socket.IO admission-ticket work:

- `--users=200 --ramp=5 --hold=30 --timeout=90`: 200/200 snapshot groups succeeded, 600/600 sockets connected, 600/600 subscriptions were acknowledged, and no errors occurred. The run completed in 119251 ms. Snapshot latency was p50 12513 ms, p95 19354 ms, p99 20727 ms, max 21830 ms; connection latency was p50 2963 ms, p95 14573 ms, p99 68348 ms, max 68510 ms; subscription latency was p50 1005 ms, p95 5171 ms, p99 8868 ms, max 15529 ms. During the burst, a manually requested presentation page still loaded fresh in slightly over one second and subsequently in approximately 600–700 ms.
- `--users=500 --ramp=30 --hold=30 --timeout=90`: 498/500 snapshot groups succeeded, 1493/1500 sockets connected, 1492/1500 subscriptions were acknowledged, and five errors occurred. The run completed in 126198 ms. Snapshot latency was p50 14215 ms, p95 36661 ms, p99 43493 ms, max 47329 ms; connection latency was p50 8572 ms, p95 28284 ms, p99 36551 ms, max 45479 ms; subscription latency was p50 1245 ms, p95 16175 ms, p99 26956 ms, max 44243 ms. The backend reached approximately 99% CPU and one snapshot failed after its SQLAlchemy connection pool reached 40 pooled plus 35 overflow connections and timed out after 45 seconds. A second snapshot returned a presentation-not-found response, and two message-namespace connections timed out. This is a near-capacity stress result, not a verified 500-user service level.

The current verified target is therefore 200 concurrent simulated users and 600 Socket.IO connections under the tested burst. The 500-user run completed more than 99% of its snapshot, connection, and subscription operations, showing that practical capacity is close to 500 users, but it crossed the single-backend-replica reliability boundary. Increasing the database connection pool alone is not the preferred remedy because the backend CPU was already saturated and PostgreSQL load also rose substantially.

Before enabling multiple backend replicas, retain the Redis Socket.IO manager for cross-replica rooms and events and verify connection routing for the complete Engine.IO handshake and upgrade path. WebSocket connections remain attached to the replica that accepted them, but transports that use multiple HTTP requests require session affinity or WebSocket-only operation. Scale-out must also account for the database connection budget: each backend replica owns a separate SQLAlchemy pool, so multiplying replicas with the current pool limits can exceed PostgreSQL's connection capacity.

## Boundaries

The snapshot cursor covers entity mutation replay through the access log. Access-policy and hierarchy state can be included where a consumer requires it, but their handoff is not represented as a unified durable change stream. External and third-party data-transfer contracts are outside this internal contract and belong in a separate data-transfer documentation area.
