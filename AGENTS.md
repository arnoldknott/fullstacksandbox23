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
- `.devcontainer/`: devcontainer configuration for local and Codespaces development
- `hooks/`: local git hook examples used as guidance for formatting, linting, and testing

## Default Commands

Use the narrowest command that verifies your change. All formatting, linting, and testing
MUST run inside the **test environment**, not in the dev environment or on the host.

### Test Environment Lifecycle

The test environment is a separate Docker Compose stack from the dev environment.
Use the existing scripts under `scripts/` to manage it:

- **Build:** `./scripts/build_test.sh`
- **Enter backend container:** `./scripts/enter_backend_test.sh` (starts the stack and opens a shell)
- **Enter frontend container:** `./scripts/enter_frontend_svelte_test.sh` (starts the stack and opens a shell)
- **Stop:** `./scripts/stop_test.sh`

The test containers can be reused across runs — you do not need to stop and rebuild
between each task. Only stop when the user asks or when you are done with all validation.

### Backend (inside test backend container)

After entering via `./scripts/enter_backend_test.sh`, run:

- Format: `black --check .`
- Lint: `ruff check .`
- Full tests: `pytest -v`
- Single test: `pytest -v src/core/tests/test_security.py::test_get_azure_jwks`

### Frontend (inside test frontend container)

After entering via `./scripts/enter_frontend_svelte_test.sh`, run:

- Format: `bun format`
- Lint: `bun lint`
- Check: `bun check`
- Unit tests: `bun test:unit`

### Non-interactive alternative

For non-interactive or CI-style execution, refer to the GitHub Actions workflows
`.github/workflows/backendAPI.yml` and `.github/workflows/frontend_svelte.yml` —
they are the source of truth for how to run formatting, linting, and testing
against the test compose stack without an interactive shell.

### Infrastructure

Prefer the dedicated infrastructure container from the repository root:

- Build tool image: `docker compose -f infrastructure/compose.yml build tofu`
- Open shell: `docker compose -f infrastructure/compose.yml run --rm tofu /bin/sh`
- Format: `docker compose -f infrastructure/compose.yml run --rm tofu tofu fmt`

### Dev Environment

The dev environment is started automatically by the devcontainer (`docker compose up -d`).
Do **not** use it for validation. It is for interactive development and browsing only.

- Dev backend shell: `./scripts/enter_backend_dev.sh`
- Dev frontend shell: `./scripts/enter_frontend_svelte_dev.sh`
- Stop dev: `./scripts/stop_dev.sh`

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
