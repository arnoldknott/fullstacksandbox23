#!/usr/bin/env sh
set -eu

TEMPLATE_PATH=${TEMPLATE_PATH:-/users_template.acl}
ACL_PATH=${ACL_PATH:-/etc/redis/users.acl}
CONF_PATH=${CONF_PATH:-/redis.conf}

missing=""
[ -n "${REDIS_PASSWORD:-}" ] || missing="$missing REDIS_PASSWORD"
[ -n "${REDIS_SESSION_PASSWORD:-}" ] || missing="$missing REDIS_SESSION_PASSWORD"
[ -n "${REDIS_SOCKETIO_PASSWORD:-}" ] || missing="$missing REDIS_SOCKETIO_PASSWORD"
[ -n "${REDIS_WORKER_PASSWORD:-}" ] || missing="$missing REDIS_WORKER_PASSWORD"
if [ -n "$missing" ]; then
  echo "[redis entrypoint] ERROR: Missing required env vars:$missing" >&2
  exit 1
fi

if [ ! -f "$TEMPLATE_PATH" ]; then
  echo "[redis entrypoint] ERROR: Template not found at $TEMPLATE_PATH" >&2
  exit 1
fi

# Escape string for safe sed replacement
esc() { printf '%s' "$1" | sed -e 's/[\\&/]/\\&/g'; }

sed \
  -e "s/\\${REDIS_PASSWORD}/$(esc "${REDIS_PASSWORD}")/g" \
  -e "s/\\${REDIS_SESSION_PASSWORD}/$(esc "${REDIS_SESSION_PASSWORD}")/g" \
  -e "s/\\${REDIS_SOCKETIO_PASSWORD}/$(esc "${REDIS_SOCKETIO_PASSWORD}")/g" \
  -e "s/\\${REDIS_WORKER_PASSWORD}/$(esc "${REDIS_WORKER_PASSWORD}")/g" \
  "$TEMPLATE_PATH" \
  > "$ACL_PATH"

# Validate no unresolved placeholders remain
if grep -q '\${' "$ACL_PATH"; then
  echo "[redis entrypoint] ERROR: Unresolved placeholders remain in ACL file:" >&2
  echo "----- ACL BEGIN -----" >&2
  cat "$ACL_PATH" >&2
  echo "------ ACL END ------" >&2
  exit 1
fi
chmod 600 "$ACL_PATH"
echo "[redis entrypoint] Wrote ACL to $ACL_PATH (masked)"

# Start redis with provided config and explicit aclfile
if [ ! -f "$CONF_PATH" ]; then
  echo "[redis entrypoint] ERROR: Config not found at $CONF_PATH" >&2
  exit 1
fi
exec redis-server "$CONF_PATH" --aclfile "$ACL_PATH"
