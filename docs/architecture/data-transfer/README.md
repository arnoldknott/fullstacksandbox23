# Data transfer

This section describes how application state moves between services. The current documented contract is internal: REST supplies authorized initial entity snapshots, then Socket.IO handles authorized subscriptions, replay, and incremental mutations.

- [Internal data transfer](internal/README.md) — overview of the REST-to-Socket.IO flow.
- [REST snapshots and incremental Socket.IO](internal/rest-snapshot-incremental-socketio.md) — cursor, subscription, authorization, and load-test details.

This section does not define third-party provider responses or their retention rules. The [security data-storage policy](../security/README.md#data-storage-policy) governs that data and prohibits persistent storage of authorized third-party resource responses.
