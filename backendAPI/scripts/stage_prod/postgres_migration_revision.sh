#!/bin/sh

LOGFILE_PATH="/data/migrations/stage_prod/logs"
VERSIONSFILE_PATH="/data/migrations/stage_prod/versions"


# apk add --no-cache git

mkdir -p $VERSIONSFILE_PATH
cd /app/src
echo "=== COMMMIT_SHA: \"$COMMIT_SHA\" ==="
echo "=== LOGFILE_PATH: \"$LOGFILE_PATH\" ==="
# alembic -c alembic_stage_prod.ini revision --autogenerate -m \"$COMMIT_SHA\" > $LOGFILE_PATH/revision_$COMMIT_SHA.log
MIGRATION_GENERATION_LOG=$(alembic -c alembic_stage_prod.ini revision --autogenerate -m \"$COMMIT_SHA\")
echo $MIGRATION_GENERATION_LOG > $LOGFILE_PATH/revision_$COMMIT_SHA.log
echo "=== MIGRATION_GENERATION_LOG: \"$MIGRATION_GENERATION_LOG\" ==="
# MIGRATION_SCRIPT_FILENAME=$(cat $LOGFILE_PATH/revision_$COMMIT_SHA.log | awk '/Generating /{print $2}')
MIGRATION_SCRIPT_FILENAME=$(echo $MIGRATION_GENERATION_LOG | awk '/Generating /{print $2}')
echo "=== MIGRATION_SCRIPT_FILENAME: \"$MIGRATION_SCRIPT_FILENAME\" ==="
echo "=== VERSIONSFILE_PATH: \"$VERSIONSFILE_PATH\" ==="
cp $MIGRATION_SCRIPT_FILENAME $VERSIONSFILE_PATH
echo $MIGRATION_SCRIPT_FILENAME > $LOGFILE_PATH/revision_filename_$COMMIT_SHA.log
# mv $LOGFILE_PATH/revision_$COMMIT_SHA.log /data/migrations/stage_prod/logs
# Leave those outputs as they are, as the runner picks up the echo and recreates the file for pull request:
cat $MIGRATION_SCRIPT_FILENAME
echo $MIGRATION_SCRIPT_FILENAME

# apk del git
# docker compose run -T --rm backend_api sh -c "alembic revision --autogenerate -m \"$1\"