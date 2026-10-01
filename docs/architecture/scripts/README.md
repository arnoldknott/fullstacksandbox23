# Scripts

Repository-level automation lives under [scripts](../../../scripts/). Use these entry points to manage the application Compose environments:

| Purpose | Entry point |
| --- | --- |
| Build the test environment | [`build_test.sh`](../../../scripts/build_test.sh) |
| Enter backend/frontend test containers | [`enter_backend_test.sh`](../../../scripts/enter_backend_test.sh), [`enter_frontend_svelte_test.sh`](../../../scripts/enter_frontend_svelte_test.sh) |
| Enter backend/frontend development containers | [`enter_backend_dev.sh`](../../../scripts/enter_backend_dev.sh), [`enter_frontend_svelte_dev.sh`](../../../scripts/enter_frontend_svelte_dev.sh) |
| Stop a stack | [`stop_test.sh`](../../../scripts/stop_test.sh), [`stop_dev.sh`](../../../scripts/stop_dev.sh) |
| Run the Socket.IO load test | [`socketio_load.sh`](../../../scripts/socketio_load.sh) |
| Deploy infrastructure locally | [`deploy_infrastructure.sh`](../../../scripts/deploy_infrastructure.sh) |

Infrastructure tooling runs in its own container; the infrastructure entry points are described in [infrastructure guidance](../../infrastructure/README.md). Component-specific automation stays beside its owner, such as PostgreSQL migration scripts under [backend/scripts](../../../backend/scripts/). See the [root README](../../../README.md#develop-and-validate) and component `AGENTS.md` files for environment and validation requirements.
