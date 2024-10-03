#!/bin/bash

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR/infrastructure
docker run --rm -it --entrypoint /bin/sh infrastructure-opentofu