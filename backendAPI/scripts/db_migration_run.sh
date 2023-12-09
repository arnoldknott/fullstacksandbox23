#!/bin/sh

cd ../src
alembic upgrade head
# docker compose run -T --rm backend_api sh -c "alembic upgrade head"