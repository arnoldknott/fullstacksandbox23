#!/bin/bash

echo "=== Running: ==="
echo "=== tofu - init ==="

echo "=== tofu - init - 1st input variable to intit script ==="
echo $1

echo "=== tofu - init - 2nd input variable to intit script ==="
echo $2

echo "=== tofu - init - @ input variables to intit script ==="
echo $@

# echo "=== tofu - init - ${AZ_RESOURCE_GROUP_NAME} ==="
# echo $AZ_RESOURCE_GROUP_NAME

echo "=== tofu - init - AZ_STORAGE_ACCOUNT_NAME in container ==="
docker compose run --entrypoint '/bin/sh -c "echo $AZ_STORAGE_ACCOUNT_NAME"' tofu

echo "=== tofu - init - AZ_STORAGE_ACCOUNT_NAME in container - command passed by script ==="
docker compose run --entrypoint '/bin/sh -c "$@"' tofu

echo "=== tofu - init ==="
echo "=== Done! ==="