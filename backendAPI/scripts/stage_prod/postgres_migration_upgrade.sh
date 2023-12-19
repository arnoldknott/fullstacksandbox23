#!/bin/sh

LOGFILE_PATH="/data/migrations/stage_prod/logs"

mkdir -p $LOGFILE_PATH
cd /app/src
alembic -c alembic_stage_prod.ini upgrade head > $LOGFILE_PATH/upgrade_$COMMIT_SHA.log
cat $LOGFILE_PATH/upgrade_$COMMIT_SHA.log
# mv alembic_upgrade.log /data/migrations/stage_prod/logs
# docker compose run -T --rm backend_api sh -c "alembic upgrade head"