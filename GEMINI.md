# Gemini CLI guidance

This file is a redirect. Authoritative repository guidance lives in [`AGENTS.md`](./AGENTS.md) at the repository root, with path-specific detail in nested `AGENTS.md` files:

- `AGENTS.md` — shared guidance (branching, test environment, cross-app integration)
- `backend/AGENTS.md` — backend (FastAPI + Socket.IO + Celery)
- `frontend_svelte/AGENTS.md` — frontend (SvelteKit)
- `infrastructure/AGENTS.md` — OpenTofu + Azure

Gemini CLI is configured via `.gemini/settings.json` to load `AGENTS.md` (and this file) hierarchically, so the nearest `AGENTS.md` to the file you are editing is applied automatically.
