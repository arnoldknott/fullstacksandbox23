#!/bin/sh

cd /app/src
alembic -c alembic_stage_prod.ini upgrade head
# docker compose run -T --rm backend_api sh -c "alembic upgrade head"