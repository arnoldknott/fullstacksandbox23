# !/bin/bash


REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
COMPOSE_PROJECT_NAME=test-fssb23 docker compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env down