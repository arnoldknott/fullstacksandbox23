#!/bin/sh

LOGFILE_PATH="/data/migrations/dev/logs"

cd /app/src
alembic downgrade $1 > $LOGFILE_PATH/downgrade_$COMMIT_SHA.log
cat $LOGFILE_PATH/upgrade_$COMMIT_SHA.log
# docker compose run -T --rm backend_api sh -c "alembic upgrade head"