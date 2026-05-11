# Purpose

Sandbox to experiment with a full stack applications using
- Svelte for frontend
- FastAPI for backend
- Postgres for database
- Redis for caching
- docker compose for containerization
- github actions for CI/CD

# License

see [license file](LICENSE)

# Contributing

## Development:

The repository root [versions.env](versions.env) is committed and only stores shared build-tool version pins for Docker and the devcontainer.

Use app-local `.env` files for the environment variables in development. If you specify a variable `AZURE_KEYVAULT_HOST`, the application will retrieve all variables from there. Make sure your app has access to this keyvault then from the host you are running the development containers on. You might still need to specify the necessary variables to start the postgres container.
Feel free to ask the repository owner for an example of the `.env` file.

Here's how you run the application locally in development:


```bash
docker compose build
docker compose up
```

The default Codespaces and VS Code devcontainer entry point is the root devcontainer in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json). Its initialize step links `.env` to [versions.env](versions.env) so Docker Compose interpolation and build arguments use the same pinned Python, Node, Bun, Alpine, and `uv` values as the app containers.

Use this file only for shared image/tool version pins. Do not put secrets there.

## Devcontainer modes

This repository uses a single primary devcontainer entry point [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json).

### What it is for

- The devcontainer is intended to control the full Docker Compose stack, shared scripts, and infrastructure-oriented tasks.
- It keeps the editor toolchain aligned with the app container versions while leaving the app containers themselves as the runtime source of truth.

### Working with it

Use the devcontainer as the primary workspace and open additional windows only when needed:

1. Open the repository in a Dev Container and select the devcontainer configuration.
2. Start the Compose stack manually in the first window with `docker compose up`.
3. Open additional VS Code windows for other branches, worktrees, or focused edits when needed.
4. Keep the running stack in the first window if you want real-time logs and manual control over startup and shutdown.


## Testing:

use a local `.env` file for the environment variables in testing.
See the [pre commit hooks](hooks/pre-commit) to get inspiration on how to run code formating, linting and testing manually.

## Use hooks

In your `.git/hooks directory`, run `ln -s -f ../../hooks/* .` to install the hooks for your local repository.

The github actions workflow will run those things as well on commits.