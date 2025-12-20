#!/bin/sh


# Handy tool to enter backend API container
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR
docker compose up -d
docker compose exec frontend_svelte sh -c "/bin/sh"