#!/bin/bash

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
BRANCH_NAME=$(git branch --show-current)

cd $REPO_ROOT_DIR/infrastructure


docker compose build
# docker compose up

docker compose down --remove-orphans

cd scripts

# can be used to copy files from inside the container to the host:
# docker compose run --name testcontainername tofu
# docker cp testcontainername:/code/hello.txt hello_local.txt

# Run each of those as a single step in the CI/CD job  and use variables to pass the secrets to the script:
echo "=== Tofu Version ==="
# docker compose run --rm tofu --version
./version.sh

echo "=== Tofu Help ==="
# docker compose run --rm tofu --help
./help.sh

echo "=== Tofu Select Workspace ==="
if [ "$BRANCH_NAME" == "dev" ]; then
    docker compose run --rm tofu workspace select dev
elif [ "$BRANCH_NAME" == "stage" ]; then
    docker compose run --rm tofu workspace select stage
elif [ "$BRANCH_NAME" == "prod" ]; then
    docker compose run --rm tofu workspace select prod
else
    echo "Branch name not recognized"
    exit 1
fi

echo "=== Tofu Init ==="
./init.sh --my-variable=123

# docker compose run --rm tofu --version > tofu_version.txt