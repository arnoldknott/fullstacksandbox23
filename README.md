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

Use a local `.env` file for the environment variables in development. If you specify a variable `AZURE_KEYVAULT_HOST`, the application will retrieve all variables from there - but you might still need to specify the necessary variables to start the postgres container.
feel free to ask for an example of the `.env` file.

```bash

`docker compose build`

## Run the containers:

`docker compose up`


## Build and run for testing:

use a local `.env` file for the environment variables in testing:

```bash

```bash
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env build
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run
```


Preferably run code format and linting in a pre-commit script `.git/hooks/pre-commit`:

```bash
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run -T --rm backend_api sh -c "black --check ."
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run -T --rm backend_api sh -c "ruff check ."
```


make sure you run code formatter, linting and testing before opening a pull request.
See the github actions workflow for more details.