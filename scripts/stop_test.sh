# !/bin/bash


REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env down