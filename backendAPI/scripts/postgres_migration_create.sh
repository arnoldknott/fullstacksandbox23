#!/bin/sh

# apk add --no-cache git
cd /app/src
alembic revision --autogenerate -m \"$COMMIT_SHA\" > alembic_revision.log
MIGRATION_SCRIPT_FILENAME=$(cat alembic_revision.log | awk '/Generating /{print $2}')
echo $MIGRATION_SCRIPT_FILENAME
cat $MIGRATION_SCRIPT_FILENAME

# apk del git
# docker compose run -T --rm backend_api sh -c "alembic revision --autogenerate -m \"$1\"