#!/bin/sh


# Handy tool to spped up tests - assunes the test environment is already built
# to start all over pre-commit hookl might be handy!
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
COMPOSE_PROJECT_NAME=test-fssb23 docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env up -d
COMPOSE_PROJECT_NAME=test-fssb23 docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env exec frontend_svelte sh -c "/bin/sh"
# just run `pytest -v` in the container