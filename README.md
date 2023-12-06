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


## Testing:

use a local `.env` file for the environment variables in testing:

```bash

```bash
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env --remove-orphans build
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run backend_api sh -c "black ."
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run backend_api sh -c "ruff format ."
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run backend_api sh -c "pytest"
```


Preferably run code format and linting in a pre-commit script `.git/hooks/pre-commit`:

```bash
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env --remove-orphans run -T --rm backend_api sh -c "black ."
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run -T --rm backend_api sh -c "ruff format ."
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run -T --rm backend_api sh -c "pytest -v"
```

Ideally you run code formatter, linting and testing before opening a pull request.
See the github actions workflow for more details.