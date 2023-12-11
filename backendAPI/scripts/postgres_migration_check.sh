#!/bin/sh

set +e

$LOGFILE_PATH="/data/migrations/stage_prod/logs"

# TBD: add $COMMIT_SHA to file names
mkdir -p $LOGFILE_PATH
cd /app/src
alembic -c alembic_stage_prod.ini check > $LOGFILE_PATH/check_$COMMIT_SHA.log
ALEMBIC_EXIT_CODE=$?
echo $ALEMBIC_EXIT_CODE > $LOGFILE_PATH/check_exit_code_$COMMIT_SHA.log
cat $LOGFILE_PATH/check_$COMMIT_SHA.log
echo "Alembic exit code: $ALEMBIC_EXIT_CODE"
exit $ALEMBIC_EXIT_CODE

# cd /app/src
# alembic check > alembic_check.log
# ALEMBIC_EXIT_CODE=$?
# echo $ALEMBIC_EXIT_CODE > alembic_check_exit_code.log
# cat alembic_check.log
# exit $ALEMBIC_EXIT_CODE

# docker compose run -T --rm backend_api sh -c "alembic check"