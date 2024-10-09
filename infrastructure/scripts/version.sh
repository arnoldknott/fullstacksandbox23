#!/bin/bash

echo "=== Running: ==="
echo "=== tofu - version ==="

# echo " TEST_VARIABLE:"
# docker compose run --entrypoint '/bin/sh -c "echo $TEST_VARIABLE"' tofu

docker compose run --rm -T tofu --version

echo "=== tofu - version ==="
echo "=== Done! ==="