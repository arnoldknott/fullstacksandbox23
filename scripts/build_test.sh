#!/bin/sh
# Since containers are not built in the pre-commit hook any more, this script is used to build the test environment

COMPOSE_PROJECT_NAME=test-fssb23 docker-compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env build