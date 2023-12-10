#!/bin/sh

cd /app/src
alembic check > alembic_check.log || true
ALEMBIC_EXIT_CODE=$?
echo $ALEMBIC_EXIT_CODE > alembic_check_exit_code.log
cat alembic_check.log
echo "Alembic exit code: $ALEMBIC_EXIT_CODE"
exit $ALEMBIC_EXIT_CODE

# cd /app/src
# alembic check > alembic_check.log
# ALEMBIC_EXIT_CODE=$?
# echo $ALEMBIC_EXIT_CODE > alembic_check_exit_code.log
# cat alembic_check.log
# exit $ALEMBIC_EXIT_CODE

# docker compose run -T --rm backend_api sh -c "alembic check"