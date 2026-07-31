#!/bin/sh

set -eu

# Output only the master password value for pgAdmin's hook contract.
printf '%s\n' "${PGADMIN_MASTER_PASSWORD:-}"