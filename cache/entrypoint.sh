#!/usr/bin/env sh
set -eu

readonly TEMPLATE_PATH="/data/users_template.acl"
readonly ACL_PATH="/data/users.acl"
readonly CONF_PATH="/data/redis-full.conf"

missing=""
[ -n "${REDIS_PASSWORD:-}" ] || missing="$missing REDIS_PASSWORD"
[ -n "${REDIS_SESSION_PASSWORD:-}" ] || missing="$missing REDIS_SESSION_PASSWORD"
[ -n "${REDIS_SOCKETIO_PASSWORD:-}" ] || missing="$missing REDIS_SOCKETIO_PASSWORD"
[ -n "${REDIS_CELERY_PASSWORD:-}" ] || missing="$missing REDIS_CELERY_PASSWORD"
if [ -n "$missing" ]; then
  echo "=== redis entrypoint - ERROR: Missing required env vars:$missing ===" >&2
  exit 1
fi

if [ ! -f "$TEMPLATE_PATH" ]; then
  echo "=== redis entrypoint - ERROR: Template not found at $TEMPLATE_PATH ===" >&2
  exit 1
fi

# Render template using awk literal replacements
awk \
  -v RP="${REDIS_PASSWORD}" \
  -v RSP="${REDIS_SESSION_PASSWORD}" \
  -v RSPIO="${REDIS_SOCKETIO_PASSWORD}" \
  -v RWP="${REDIS_CELERY_PASSWORD}" \
  '{
     gsub(/\$\{REDIS_PASSWORD\}/, RP);
     gsub(/\$\{REDIS_SESSION_PASSWORD\}/, RSP);
     gsub(/\$\{REDIS_SOCKETIO_PASSWORD\}/, RSPIO);
     gsub(/\$\{REDIS_CELERY_PASSWORD\}/, RWP);
     print
   }' "$TEMPLATE_PATH" > "$ACL_PATH"

# Validate no unresolved placeholders remain
if grep -q '\${' "$ACL_PATH"; then
  echo "🔥 🥞 redis entrypoint - ERROR: Unresolved placeholders remain in ACL file: ===" >&2
  exit 1
fi
chmod 600 "$ACL_PATH"
echo "🥞 👍 redis entrypoint - Wrote ACL to $ACL_PATH (masked)"

# Start redis with provided config and explicit aclfile
if [ ! -f "$CONF_PATH" ]; then
  echo " 🔥 🥞 redis entrypoint - ERROR: Config not found at $CONF_PATH ===" >&2
  exit 1
fi
exec redis-server "$CONF_PATH" \
  --bind "* -::*" \
  --port "$REDIS_PORT" \
  --aclfile "$ACL_PATH"
