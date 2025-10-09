#!/bin/sh

LOGFILE_PATH="/data/migrations/dev/logs"
VERSIONSFILE_PATH="/data/migrations/dev/versions"


mkdir -p $VERSIONSFILE_PATH
cd /app/src
alembic revision --autogenerate -m \"$COMMIT_SHA\" > $LOGFILE_PATH/revision_$COMMIT_SHA.log
MIGRATION_SCRIPT_FILENAME=$(cat $LOGFILE_PATH/revision_$COMMIT_SHA.log | awk '/Generating /{print $2}')
cp $MIGRATION_SCRIPT_FILENAME $VERSIONSFILE_PATH
echo $MIGRATION_SCRIPT_FILENAME > $LOGFILE_PATH/revision_filename_$COMMIT_SHA.log
# mv $LOGFILE_PATH/revision_$COMMIT_SHA.log /data/migrations/dev/logs
# Leave those outputs as they are, as the runner picks up the echo and recreates the file for pull request:
cat $MIGRATION_SCRIPT_FILENAME
echo $MIGRATION_SCRIPT_FILENAME

# apk del git
# docker compose run -T --rm backend_api sh -c "alembic revision --autogenerate -m \"$1\"