#!/bin/sh

cd ../src
alembic check
# docker compose run -T --rm backend_api sh -c "alembic check"