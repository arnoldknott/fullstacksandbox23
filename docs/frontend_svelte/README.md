# Frontend Svelte

The [frontend_svelte](../../frontend_svelte/) application uses SvelteKit for server-rendered routes and browser interactions. Server loads use shared backend API wrappers, route groups enforce session requirements, and `EntityContainer` with the Socket.IO client combines initial REST snapshots with incremental updates; development guidance is maintained in [frontend_svelte/AGENTS.md](../../frontend_svelte/AGENTS.md).
