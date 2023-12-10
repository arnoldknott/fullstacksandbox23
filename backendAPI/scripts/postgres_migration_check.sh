#!/bin/sh

cd /app/src
alembic check > alembic_check.log
ALEMBIC_EXIT_CODE=$?
cat alembic_check.log
exit $ALEMBIC_EXIT_CODE
# docker compose run -T --rm backend_api sh -c "alembic check"