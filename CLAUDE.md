# Claude Code guidance

This repository uses [`AGENTS.md`](./AGENTS.md) at the repository root as the single source of truth for agent-facing guidance. Nested `AGENTS.md` files under `backend/`, `frontend_svelte/`, and `infrastructure/` provide path-specific detail.

@AGENTS.md

## Path-specific context

When working inside an app subfolder, also load the nearest `AGENTS.md`:

- @backend/AGENTS.md
- @frontend_svelte/AGENTS.md
- @infrastructure/AGENTS.md

## Claude-specific notes

- Shared project settings live in `.claude/settings.json`. Personal overrides belong in `.claude/settings.local.json` (gitignored).
- Use `CLAUDE.local.md` for personal, uncommitted notes (gitignored).
