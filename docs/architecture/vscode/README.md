# VS Code

The primary VS Code environment is defined by [.devcontainer/devcontainer.json](../../../.devcontainer/devcontainer.json). Repository-wide agent guidance lives in [AGENTS.md](../../../AGENTS.md), with tool adapters and path-specific instructions under [.github](../../../.github/) and the component-level `AGENTS.md` files.

## Python environment

The devcontainer uses the Python version in [versions.env](../../../versions.env).
Its post-create command exports [backend/uv.lock](../../../backend/uv.lock), including
the `dev` extra, and installs the locked dependencies and editable backend into
`/usr/local/bin/python`. It does not update the lockfile. No workspace virtual
environment is required for editor imports.

[Workspace settings](../../../.vscode/settings.json) default to this interpreter.
If an interpreter was previously selected manually, run **Python: Select Interpreter**,
choose **Enter Interpreter Path**, and enter `/usr/local/bin/python`. Changing the
default setting does not override an existing selection.

Use **Dev Containers: Rebuild Container** after changing the container's Python
version or image setup. A reload alone does not replace the running image.
For dependency-only updates, run **Dev Containers: Rebuild Container** or rerun
the backend dependency installation from the post-create command in the VS Code
devcontainer terminal. Backend application containers are separate: their builds
install locked dependencies into `/py` and do not supply Pylance's packages.

## What survives a rebuild

- The bind-mounted repository, including uncommitted changes and workspace-local
  environment files, remains on the host.
- Named volumes remain unless explicitly deleted. These include the frontend
  dependency volume, Codex data volume, Copilot session storage (`/root/.copilot`),
  and remote VS Code state (`/root/.vscode-server/data`) declared in
  [the devcontainer Compose configuration](../../../.devcontainer/compose.devcontainer.yml).
  Before the first rebuild that introduces these mounts, back up the existing
  directories outside the container and restore them into the mounted volumes
  afterward. Adding mounts does not migrate data from the old container.
  Do not delete these volumes (for example with `docker compose down -v`) if their
  contents are still needed.
- Application database and cache volumes are separate from the devcontainer.
  Rebuilding the devcontainer does not itself delete them.
- Files and manual package installations stored only in the old container's writable
  layer are lost, including temporary files, container-local home-directory data
  outside mounted volumes, and manually installed Python interpreters. Back up
  anything needed from those locations before rebuilding.
- Running terminals and processes in the devcontainer end. Save editor buffers
  before rebuilding.

Workspace virtual environments may remain on disk but reference an interpreter
removed with the old container. Use the rebuilt system interpreter instead.
