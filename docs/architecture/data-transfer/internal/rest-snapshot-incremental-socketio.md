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

The backend validates identifiers, filters the requested entity query through the same read authorization used by CRUD operations, and enters only authorized `resource:<UUID>` rooms. When a cursor is supplied, mutation logs newer than that cursor are read for the namespace entity type. Active authorized entities are emitted through `transferred`; snapshot entities deleted after the cursor are emitted through `deleted`. Normal create, update, delete, share, link, and unlink events continue over Socket.IO after subscription.

## Security invariants

Client-provided entity identifiers are subscription requests and never grant room membership. Snapshot reads, room subscriptions, replay reads, parent-room entry, and explicit single-entity reads remain access-controlled. Public namespace behavior and authenticated guard behavior continue to use their configured policy and guard paths.

First-party query parameter names and serialized values use kebab-case. Python and TypeScript identifiers remain idiomatic, and externally defined protocol parameters retain their external spelling.

## Load-test protocol

The stage load test in [socketio-load.mjs](../../../../frontend_svelte/tests/stage-stress/socketio-load.mjs) models the production sequence: fetch REST snapshots, read entity identifiers and `X-Entity-Cursor`, connect with `snapshot-subscription=true`, subscribe in batches, wait for acknowledgements, hold connections, and report latency percentiles. It accepts `--users`, `--ramp`, `--hold`, `--timeout`, `--frontend-only`, and `--backend-only`.

Measured stage results on 2026-09-09:

- 200 users over a 30-second ramp: 200/200 snapshot groups succeeded, 600/600 sockets connected, 600/600 subscriptions were acknowledged, and no errors occurred. Snapshot latency was p50 297 ms, p95 976 ms, p99 1162 ms; connection latency was p50 197 ms and p95 1039 ms; subscription latency was p50 100 ms and p95 523 ms.
- 500 users over a 30-second ramp: 500/500 snapshot groups succeeded, 1500/1500 sockets connected, 1500/1500 subscriptions were acknowledged, and no errors occurred. Latency increased as arrivals exceeded immediate processing capacity.
- 200 users after adding 100 Numerical rows: 200/200 snapshot groups succeeded, 600/600 sockets connected, 600/600 subscriptions were acknowledged, and no errors occurred. Snapshot latency was p50 1046 ms, p95 1515 ms, p99 1641 ms, max 1675 ms; connection latency was p50 214 ms and p95 329 ms; subscription latency was p50 167 ms and p95 292 ms.

## Boundaries

The snapshot cursor covers entity mutation replay through the access log. Access-policy and hierarchy state can be included where a consumer requires it, but their handoff is not represented as a unified durable change stream. External and third-party data-transfer contracts are outside this internal contract and belong in a separate data-transfer documentation area.
