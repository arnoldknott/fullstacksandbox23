# GitHub Copilot instructions

The authoritative repository guidance for all agents, including Copilot, lives in [`AGENTS.md`](../AGENTS.md). Path-specific detail lives in nested `AGENTS.md` files:

- [`backend/AGENTS.md`](../backend/AGENTS.md)
- [`frontend_svelte/AGENTS.md`](../frontend_svelte/AGENTS.md)
- [`infrastructure/AGENTS.md`](../infrastructure/AGENTS.md)

Path-specific Copilot instruction files (with required `applyTo` frontmatter) are under [`.github/instructions/`](./instructions/) and delegate to the corresponding `AGENTS.md`.

## Copilot-specific rules

- **@azure Rule — Use Azure Best Practices:** When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.

## Branch and environment quick reference

- Feature work branches from `dev` and merges back to `dev` (feature branches: `feature/<description>` or `fix/<description>`).
- Promotion flow: `dev` → `stage` → `main`.
- Environment mapping: `dev` branch → `dev` + `test` envs; `stage` branch → `stage`; `main` branch → `prod`.

See [`AGENTS.md`](../AGENTS.md) for the full description, command cheatsheet, and architecture patterns.
