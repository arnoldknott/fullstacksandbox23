#!/bin/sh

cd /app/src
alembic -c alembic_stage_prod.ini upgrade head > alembic_upgrade.log
mv alembic_upgrade.log /data/migrations/stage_prod/logs
# docker compose run -T --rm backend_api sh -c "alembic upgrade head"