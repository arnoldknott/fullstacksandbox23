#!/bin/sh
# after a commit the pre-commit hook will run and stops the test containers
# while developing tests, the backend container is usefull to have running

COMPOSE_PROJECT_NAME=test-fssb23 docker-compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env up -d  
COMPOSE_PROJECT_NAME=test-fssb23 docker-compose -f compose.yml -f compose.override.test.yml --env-file backendAPI/src/tests/.env exec backend_api sh -c "/bin/sh"