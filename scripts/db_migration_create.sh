#!/bin/sh

docker compose run -T --rm backend_api sh -c "alembic revision --autogenerate -m \"$1\"