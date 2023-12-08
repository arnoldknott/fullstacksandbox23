#!/bin/sh

docker compose run -T --rm backend_api sh -c "alembic upgrade head"