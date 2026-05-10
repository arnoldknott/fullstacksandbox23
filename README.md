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

Use a local `.env` file for the environment variables in development. If you specify a variable `AZURE_KEYVAULT_HOST`, the application will retrieve all variables from there. Make sure your app has access to this keyvault then from the host you are running the development containers on. You might still need to specify the necessary variables to start the postgres container.
Feel free to ask the repository owner for an example of the `.env` file.

Here's how you run the application locally in development:


```bash
docker compose build
docker compose up
```

## Devcontainer modes

This repository supports three devcontainer entry points:

- Orchestrator: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
- Backend editor: [.devcontainer/backend/devcontainer.json](.devcontainer/backend/devcontainer.json)
- Frontend editor: [.devcontainer/frontend/devcontainer.json](.devcontainer/frontend/devcontainer.json)

### What each mode is for

- Orchestrator mode uses Ubuntu 26.04 and is intended to control the full Docker Compose stack, shared scripts, and infrastructure-oriented tasks.
- Backend mode builds from [backend/Dockerfile](backend/Dockerfile) target `api_dev` so Python tooling in the editor stays aligned with backend runtime versions.
- Frontend mode builds from [frontend_svelte/Dockerfile](frontend_svelte/Dockerfile) target `setup` so Node and Bun tooling in the editor stays aligned with frontend runtime versions.

All three modes mount the same workspace path, so source code and Git state are shared.

### Working with modes

Use one mode as your primary workspace and open additional windows only when needed:

1. Open the repository in a Dev Container and select one of the three devcontainer configurations.
2. Use orchestrator mode for stack operations and shared scripts.
3. Use backend or frontend mode for focused code editing with runtime-aligned language tooling.
4. Open additional VS Code windows only for parallel cross-stack work.


## Testing:

use a local `.env` file for the environment variables in testing.
See the [pre commit hooks](hooks/pre-commit) to get inspiration on how to run code formating, linting and testing manually.

## Use hooks

In your `.git/hooks directory`, run `ln -s -f ../../hooks/* .` to install the hooks for your local repository.

The github actions workflow will run those things as well on commits.