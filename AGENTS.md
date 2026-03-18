# AGENTS.md

## Purpose

This repository is a full-stack sandbox for experimenting with:

- `frontend_svelte/`: SvelteKit frontend
- `backend/`: FastAPI backend with Socket.IO and Celery
- `infrastructure/`: OpenTofu and Azure infrastructure code
- Docker Compose driven local development and test workflows from the repository root

Use this file as the top-level guide for coding agents working in the repository. Keep edits focused, preserve existing patterns, and prefer small changes over broad refactors unless the task clearly calls for them.

## How To Work In This Repo

- Check the relevant app-specific instructions before making non-trivial changes:
  - Backend: `.github/instructions/backend.instructions.md`
  - Frontend: `.github/instructions/frontend.instructions.md`
  - Infrastructure: `.github/instructions/infrastructure.instructions.md`
- Treat `.github/copilot-instructions.md` as shared repository guidance, especially for branch and environment flow plus frontend/backend integration expectations.
- When a change affects shared contracts such as auth, sessions, REST endpoints, websockets, or environment variables, review both frontend and backend impact instead of treating one side in isolation.
- Prefer the existing tooling and command surfaces already used by the repo rather than introducing new scripts or alternate workflows.

## Repository Layout

- `frontend_svelte/`: SvelteKit app and frontend tests
- `backend/`: FastAPI app, backend tests, migrations, and Python project config
- `infrastructure/`: OpenTofu configuration, Azure-related setup, and infra container workflow
- `compose.yml` plus override files: main local development and test orchestration
- `.devcontainer/`: containerized development entrypoints for frontend and backend
- `hooks/`: local git hook examples used as guidance for formatting, linting, and testing

## Default Commands

Use the narrowest command that verifies your change.

**Note:** For interactive human use, convenience scripts exist under `scripts/` (e.g., `./scripts/enter_backend_test.sh`, `./scripts/enter_frontend_svelte_test.sh`, `./scripts/enter_infrastructure.sh`). These build, start, and enter the relevant container. The non-interactive commands below are preferred for CI and automated agents.

### Backend

Run from `backend/` unless you are explicitly mirroring the container workflow:

- Install/update dev environment: `uv sync --frozen --extra dev`
- Format check: `uv run black --check .`
- Lint: `uv run ruff check .`
- Full tests: `uv run pytest -v`
- Single test: `uv run pytest -v src/core/tests/test_security.py::test_get_azure_jwks`

### Frontend

Run from `frontend_svelte/`:

- Build: `bun run build`
- Format: `bun format`
- Lint: `bin lint`
- Check: `bin check`
- Unit tests: `bun test:unit`

### Infrastructure

Prefer the dedicated infrastructure container from the repository root:

- Build tool image: `docker compose -f infrastructure/compose.yml build tofu`
- Open shell: `docker compose -f infrastructure/compose.yml run --rm tofu /bin/sh`
- Format: `docker compose -f infrastructure/compose.yml run --rm tofu tofu fmt`

### Root Compose Workflow

- Local development: `docker compose build` then `docker compose up`
- Use `compose.override.test.yml` when you need to mirror the repository's test-oriented container setup

## Repo-Specific Expectations

- Use environment variables from local `.env` files in development and testing. If `AZURE_KEYVAULT_HOST` is set, the apps may load variables from Azure Key Vault.
- Do not hard-code secrets, tokens, or environment-specific values.
- Keep dependency usage aligned with versions and tooling already declared in `backend/pyproject.toml` and `frontend_svelte/package.json`.
- Preserve established architecture patterns:
  - Backend uses Base versions of each architectual layer `BaseModel` (for database SQLmodels) , `BaseCRUD` (from which all application CRUDs inherit), `BaseView` (inherited for all REST-API endpoint views), `BaseNamespace` (from which SocketIO namespaces inherit), guards (checking OAuth2 authorization), and generated model/schema patterns.
  - Frontend favors existing SvelteKit route-group auth, shared session handling, common MaterialDesign/FlyonUI theming, and backend API wrappers.
  - Infrastructure favors editing source `.tf` files and using the existing workspace model: `dev`, `stage`, `prod`.

## Branch And Environment Model

- Feature work should branch from `dev` and merge back into `dev`.
- Promotion flow is `dev` -> `stage` -> `main`.
- Environment mapping is:
  - `dev` branch for development
  - `stage` branch for staging
  - `main` branch for production

## Change Validation

- Run targeted tests, lint, or type checks for the area you changed whenever feasible.
- If existing baseline issues cause failures, note that clearly instead of silently ignoring them.
- When changing shared contracts or auth/session behavior, validate the affected frontend and backend paths together.
