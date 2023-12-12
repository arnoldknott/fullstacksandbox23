#!/bin/sh

LOGFILE_PATH="/data/migrations/stage_prod/logs"

cd /app/src
alembic -c alembic_stage_prod.ini upgrade \"$1\" > $LOGFILE_PATH/downgrade_$COMMIT_SHA.log
cat $LOGFILE_PATH/upgrade_$COMMIT_SHA.log
# docker compose run -T --rm backend_api sh -c "alembic upgrade head"