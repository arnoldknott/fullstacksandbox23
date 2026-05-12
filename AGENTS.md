# AGENTS.md

This file is the single source of truth for agent-facing repository guidance. Tool-specific adapters (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) delegate to this file.

## Purpose

This repository is a full-stack sandbox for experimenting with:

- `frontend_svelte/`: SvelteKit frontend
- `backend/`: FastAPI backend with Socket.IO and Celery
- `infrastructure/`: OpenTofu and Azure infrastructure code
- Docker Compose driven local development and test workflows from the repository root

Keep edits focused, preserve existing patterns, and prefer small changes over broad refactors unless the task clearly calls for them.

## Repository Layout

- `frontend_svelte/`: SvelteKit app and frontend tests — see [`frontend_svelte/AGENTS.md`](./frontend_svelte/AGENTS.md)
- `backend/`: FastAPI app, backend tests, migrations, and Python project config — see [`backend/AGENTS.md`](./backend/AGENTS.md)
- `infrastructure/`: OpenTofu configuration, Azure-related setup, and infra container workflow — see [`infrastructure/AGENTS.md`](./infrastructure/AGENTS.md)
- `compose.yml` plus override files: main local development and test orchestration
- `.devcontainer/`: devcontainer configuration for local and Codespaces development.
  Entrypoint: `.devcontainer/devcontainer.json`
- `.github/workflows`: Continuous Intgration / Continuous Deployment pipelines via github actions
- `hooks/`: local git hook examples used as guidance for formatting, linting, and testing

## How To Work In This Repo

- Before making non-trivial changes in an app directory, read the nearest nested `AGENTS.md` for path-specific commands and conventions.
- When a change affects shared contracts such as auth, sessions, REST endpoints, websockets, or environment variables, review both frontend and backend impact instead of treating one side in isolation.
- Use the existing tooling and command surfaces already used by the repo rather than introducing new scripts or alternate workflows. Ask for permisson to create new scripts and workflows.

## General Guidelines

- Follow software design principles: YAGNI, SOLID, KISS, DRY.
- Use the versions of dependencies specified in `backend/pyproject.toml` and `frontend_svelte/package.json` to find the documentation of the used packages online. If a version is not specified, pull the latest version matching the constraints in those files.
- Keep code independent on Azure, running terminal commands, or performing operations related to Azure. (GitHub Copilot users: the `@azure` tool trigger is documented in [`.github/copilot-instructions.md`](./.github/copilot-instructions.md).)
- Never use abbreviations without explaining them. For example, write "Application Programming Interface (API)" on first use before using "API" in the rest of the text.
- Do not hard-code secrets, tokens, or environment-specific values.
- Use environment variables from local `.env` files in development and testing. If `AZURE_KEYVAULT_HOST` is set, the apps may load variables from Azure Key Vault.
- For follow-up notes in code comments and workflows, prefer `TBD:` as the marker instead of `TODO:`.

## Shared Integration Guidance

- Keep frontend and backend auth/session behavior aligned. The frontend depends on backend session-backed auth flows and the `/api/v1`, `/socketio/v1`, and `/ws/v1` contracts.
- When you change a shared API, auth, websocket, or session contract, check both sides of the integration instead of treating either app in isolation.
- Containerized development and CI flows are driven from the repository root with `compose.yml` plus override files such as `compose.override.yml` and `compose.override.test.yml`.

## Architecture Patterns

Preserve established patterns:

- **Backend** uses Base versions of each architectural layer: `BaseModel` (for database SQLModels), `BaseCRUD` (from which all application CRUDs inherit), `BaseView` (inherited for all REST-API endpoint views), `BaseNamespace` (from which Socket.IO namespaces inherit), guards (checking OAuth2 authorization), and generated model/schema patterns.
- **Frontend** uses existing SvelteKit route-group auth, shared session handling, common Material Design / FlyonUI theming, and backend API wrappers.
- **Infrastructure** favors editing source `.tf` files and using the existing workspace model: `dev`, `stage`, `prod`.

## Branch And Environment Model

There are 4 environments linked to 3 branches:

- `dev` branch — environments `dev` and `test`. Active development; feature branches (`feature/<description>` or `fix/<description>`) branch from `dev` and merge back into `dev`. The `test` environment runs the automated test suite.
- `stage` branch — environment `stage`. Deployed to Azure; pre-production testing that should closely mirror production. Manually verify the deployed staging servers before approving deployment to production.
- `main` branch — environment `prod`. Production deployment; stable and well-tested.

Merging order: `feature/<description>` or `fix/<description>` → `dev` → `stage` → `main`.

## Default Commands

Use the narrowest command that verifies your change. All formatting, linting, and testing MUST run inside the **test environment**, not in the dev environment or on the host.

### Start development environment

The dev environment is for interactive development and debugging, not validation. It is started automatically by the devcontainer (`docker compose up -d`), so you usually do not need to start it manually. Use the existing scripts under `scripts/` to open shells in the dev containers:

- Dev backend shell: `./scripts/enter_backend_dev.sh`
- Dev frontend shell: `./scripts/enter_frontend_svelte_dev.sh`
- Stop dev: `./scripts/stop_dev.sh`

### Test Environment Lifecycle

The test environment is a separate Docker Compose stack from the dev environment. Use the existing scripts under `scripts/` to manage it:

- **Build:** `./scripts/build_test.sh`
- **Enter backend container:** `./scripts/enter_backend_test.sh` (starts the stack and opens a shell)
- **Enter frontend container:** `./scripts/enter_frontend_svelte_test.sh` (starts the stack and opens a shell)
- **Stop:** `./scripts/stop_test.sh`

The test containers can be reused across runs — you do not need to stop and rebuild between each task. Only stop when the user asks or when you are done with all validation.

**Always show the output summary of the validation results in the same format as the called tool does.**

Per-app commands (format, lint, tests, containerized / non-interactive invocations) live in the nested guides — do not duplicate them here:

- Backend: [`backend/AGENTS.md`](./backend/AGENTS.md)
- Frontend: [`frontend_svelte/AGENTS.md`](./frontend_svelte/AGENTS.md)
- Infrastructure: [`infrastructure/AGENTS.md`](./infrastructure/AGENTS.md)

For CI-style, non-interactive invocations the GitHub Actions workflows `.github/workflows/backendAPI.yml` and `.github/workflows/frontend_svelte.yml` are the source of truth.

### Dev Environment

The dev environment is started automatically by the devcontainer (`docker compose up -d`). Do **not** use it for validation. It is for interactive development and browsing only.

- Dev backend shell: `./scripts/enter_backend_dev.sh`
- Dev frontend shell: `./scripts/enter_frontend_svelte_dev.sh`
- Stop dev: `./scripts/stop_dev.sh`

## Change Validation

- Run targeted tests, lint, or type checks for the area you changed whenever feasible.
- If existing baseline issues cause failures, note that clearly instead of silently ignoring them.
- When changing shared contracts or auth/session behavior, validate the affected frontend and backend paths together.

## Tool-Specific Adapters

This repository supports multiple AI coding tools via thin adapter files that delegate to this `AGENTS.md`:

- **GitHub Copilot**: [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) + [`.github/instructions/*.instructions.md`](./.github/instructions/) (path-specific via `applyTo` frontmatter).
- **Claude Code**: [`CLAUDE.md`](./CLAUDE.md) (imports this file via `@AGENTS.md`). Shared settings in `.claude/settings.json`.
- **Gemini CLI**: [`GEMINI.md`](./GEMINI.md). Shared settings in `.gemini/settings.json` configure hierarchical discovery of `AGENTS.md`.
- **Codex / Cursor / Aider / Windsurf / ForgeCode / others**: read `AGENTS.md` (root and nearest-nested) via the open [agents.md](https://agents.md) convention.

Personal overrides (`.claude/settings.local.json`, `.gemini/settings.local.json`, `CLAUDE.local.md`) are gitignored.
