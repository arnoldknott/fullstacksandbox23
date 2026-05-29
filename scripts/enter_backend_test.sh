#!/bin/sh

if [ ! -f versions.env ]; then
    echo "Missing versions.env in repository root."
    exit 1
fi

# Export image/tool version variables used by compose.yml and Dockerfiles.
set -a
. ./versions.env
set +a

# Handy tool to spped up tests - assunes the test environment is already built
# to start all over pre-commit hookl might be handy!
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env up -d
docker compose -f compose.yml -f compose.override.test.yml --env-file backend/src/tests/.env exec backend_api sh -c "/bin/sh"
# just run `pytest -v` in the container