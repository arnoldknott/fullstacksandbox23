#!/bin/sh

if [ ! -f versions.env ]; then
    echo "Missing versions.env in repository root."
    exit 1
fi

# Export image/tool version variables used by compose.yml and Dockerfiles.
set -a
. ./versions.env
set +a

# Since containers are not built in the pre-commit hook any more, this script is used to build the test environment
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
docker compose -f compose.yml -f compose.override.test.yml --env-file versions.env --env-file backend/src/tests/.env build