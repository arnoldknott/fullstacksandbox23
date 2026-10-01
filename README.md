# Full-Stack Sandbox

This repository is a Docker Compose-based sandbox for a SvelteKit frontend, a FastAPI backend, PostgreSQL, Redis, and supporting services. GitHub Actions provides continuous integration and deployment. See the [documentation index](docs/README.md) for component guides and architecture references.

## Start developing

The default Codespaces and VS Code workspace uses the root devcontainer at [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json). From the repository root, start the development stack with:

```bash
docker compose build
docker compose up -d
```

Development uses app-local `.env` files. See [backend/src/.env.example](backend/src/.env.example) for the backend environment-variable surface; coordinate with the repository owner for any local values not represented there. If `AZURE_KEYVAULT_HOST` is set, the application loads configured values from that Key Vault, and the host running the development containers must have the required access. PostgreSQL container startup may also require local environment values.

The committed root [versions.env](versions.env) contains shared build-tool version pins for Docker and the devcontainer. The devcontainer initialize step links it as the root `.env` used for Compose interpolation. Keep secrets in app-local environment files or the configured secret store, never in `versions.env`.

The devcontainer is the primary workspace for the full Compose stack, shared scripts, and infrastructure tasks. It aligns the editor toolchain with the application container versions; the app containers remain the runtime source of truth. For the supported workspace setup, see [VS Code guidance](docs/architecture/vscode/README.md).

## Develop and validate

Use the development stack for interactive work. For automated validation, use the separate test Compose stack, not the development containers or host environment. The repository scripts provide convenient entry points:

| Task | Command |
| --- | --- |
| Build the test stack | `./scripts/build_test.sh` |
| Enter the backend test container | `./scripts/enter_backend_test.sh` |
| Enter the frontend test container | `./scripts/enter_frontend_svelte_test.sh` |
| Stop the test stack when validation is complete | `./scripts/stop_test.sh` |
| Enter the development backend or frontend | `./scripts/enter_backend_dev.sh` or `./scripts/enter_frontend_svelte_dev.sh` |
| Stop the development stack | `./scripts/stop_dev.sh` |

Test-container entry scripts start the test environment and open an interactive shell. Run the relevant formatter, linter, type check, or tests from that container. See [backend guidance](backend/AGENTS.md) and [frontend guidance](frontend_svelte/AGENTS.md) for exact commands and single-test examples. Do not stop a test stack that was already running before your work.

For infrastructure changes, use the dedicated OpenTofu container workflow in [infrastructure guidance](infrastructure/AGENTS.md); do not run infrastructure tooling directly on the host. Review the plan before any apply operation.

## Repository guidance

[AGENTS.md](AGENTS.md) is the shared source of truth for repository conventions, security boundaries, and environment workflow. Nested `AGENTS.md` files provide backend, frontend, and infrastructure details. The [documentation index](docs/README.md) links to the current architecture and component references.

## Hooks and CI

To install the example local hooks, run this from `.git/hooks`:

```bash
ln -s -f ../../hooks/* .
```

GitHub Actions also runs repository validation in CI. Local hooks are a convenience and do not replace the required test-environment checks.

## License

See the [license](LICENSE).