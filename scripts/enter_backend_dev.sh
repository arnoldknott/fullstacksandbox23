#!/bin/sh


# Handy tool to enter backend API container
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
docker compose up -d
docker compose exec backend_api sh -c "/bin/sh"