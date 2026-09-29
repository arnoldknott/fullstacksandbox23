#!/bin/bash

set -euo pipefail

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
LOAD_ENV_FILE="$REPO_ROOT_DIR/frontend_svelte/tests/stage-stress/.env"

if [ ! -f "$LOAD_ENV_FILE" ]; then
    echo "Missing $LOAD_ENV_FILE"
    echo "Copy .env.example in the same directory and set the deployed URLs."
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$LOAD_ENV_FILE"
set +a

export HOST_WORKSPACE_FOLDER="${HOST_WORKSPACE_FOLDER:-$REPO_ROOT_DIR}"

docker compose \
    -f "$REPO_ROOT_DIR/compose.yml" \
    -f "$REPO_ROOT_DIR/compose.override.test.yml" \
    --env-file "$REPO_ROOT_DIR/backend/src/tests/.env" \
    run --rm --no-deps \
    -e STAGE_FRONTEND_URL \
    -e STAGE_BACKEND_URL \
    frontend_svelte \
    bun run test:stage:load -- "$@"
