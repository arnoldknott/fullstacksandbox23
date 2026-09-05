#!/bin/sh

set -eu

BRANCH=${1:?Usage: create_worktree.sh <branch>}

COMMON_GIT_DIR=$(git rev-parse --path-format=absolute --git-common-dir)
PRIMARY_ROOT=$(dirname "$COMMON_GIT_DIR")

NAME=$(printf '%s' "$BRANCH" | tr '/' '-')
WORKTREE="$PRIMARY_ROOT/.worktrees/$NAME"

git show-ref --verify --quiet "refs/heads/$BRANCH" || {
    git switch -c "$WORKTREE"
}

git worktree add "$WORKTREE" "$BRANCH"

ln -sf versions.env "$WORKTREE/.env"

for ENV_FILE in backend/src/.env backend/src/tests/.env frontend_svelte/src/.env
do
    if [ -f "$PRIMARY_ROOT/$ENV_FILE" ]; then
        cp "$PRIMARY_ROOT/$ENV_FILE" "$WORKTREE/$ENV_FILE"
    fi
done

code --new-window "$WORKTREE"