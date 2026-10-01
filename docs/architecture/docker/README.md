# Docker

Docker Compose is the local orchestration layer for the application services. The root [compose.yml](../../../compose.yml) defines shared services; [compose.override.yml](../../../compose.override.yml) selects development behavior, while [compose.override.test.yml](../../../compose.override.test.yml) defines the isolated test stack. The [root devcontainer](../../../.devcontainer/devcontainer.json) provides the primary VS Code workspace.

Use the development stack for interactive work and the test stack for formatting, linting, type checks, and tests. The repository [README](../../../README.md#develop-and-validate) links to the supported lifecycle scripts. Infrastructure has its own Compose definition and container; see [infrastructure guidance](../../infrastructure/README.md).
