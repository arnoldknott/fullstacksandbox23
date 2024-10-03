#!/bin/bash

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR/infrastructure

docker compose build
# docker compose up

docker compose down --remove-orphans

# can be used to copy files from inside the container to the host:
# docker compose run --name testcontainername tofu
# docker cp testcontainername:/code/hello.txt hello_local.txt

# Run each of those as a single step in the CI/CD job  and use variables to pass the secrets to the script:
echo ""
# docker compose run --rm tofu --version
./scripts/version.sh

echo ""
# docker compose run --rm tofu --help
./scripts/help.sh

echo ""

# docker compose run --rm tofu --version > tofu_version.txt