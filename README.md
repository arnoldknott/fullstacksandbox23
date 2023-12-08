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

use a local `.env` file for the environment variables in testing.
See the [pre commit hooks](hooks/pre-commit) to get inspiration on how to run code formating, linting and testing manually.

## Use hooks

In your `.git/hooks directory`, run `ln -s -f ../../hooks/* .` to install the hooks for your local repository.

The github actions workflow will run those things as well on commits.