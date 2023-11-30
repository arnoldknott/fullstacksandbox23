# Purpose

Sandbox to experiment with a full stack applications using
- Svelte for frontend
- FastAPI for backend
- Postgres for database
- Redis for caching
- docker compose for containerization
- github actions for CI/CD

# Documentation

## Build the containers:

`docker compose build`

## Run the containers:

`docker compose up`

# License

see [license file](LICENSE)

# Contributing

## Build and run for testing:

```bash
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env build
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run
```


Connect .git/hooks/pre-commit:

```bash
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run -T --rm backend_api sh -c "black --check ."
docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env run -T --rm backend_api sh -c "ruff check ."
```bash


make sure you run code formatter, linting and testing before opening a pull request.
See the github actions workflow for more details.