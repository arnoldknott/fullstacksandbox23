#!/bin/sh

apk add --no-cache git
cd /app/src
alembic revision --autogenerate -m \"$COMMIT_SHA\"

# docker compose run -T --rm backend_api sh -c "alembic revision --autogenerate -m \"$1\"