---
applyTo: "infrastructure/**"
---

## Build, test, and validation commands

This directory manages infrastructure with OpenTofu and Azure Command-Line Interface.

Important: infrastructure work in this repository is also expected to run in its own dedicated Docker container. Prefer the `tofu` service from `infrastructure/compose.yml` instead of running OpenTofu or Azure Command-Line Interface directly on the host machine.

**Interactive shortcut for developers:** run `./scripts/enter_infrastructure.sh` from the repo root to build the infra image and drop into an interactive shell where you can run `tofu fmt`, `tofu init`, `tofu plan`, etc. directly.

From the repository root, use the dedicated infrastructure container non-interactively (used by CI and coding agents):

- Build the infrastructure tool image: `docker compose -f infrastructure/compose.yml build tofu`
- Open an interactive shell in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu /bin/sh`
- Run a simple OpenTofu command in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu tofu version`
- Format files in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu tofu fmt`
- Initialize the backend in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu tofu init -backend-config="resource_group_name=..." -backend-config="storage_account_name=..." -backend-config="container_name=..." -backend-config="key=..."`
- Select the environment workspace in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu tofu workspace select -or-create <dev|stage|prod>`
- Create a plan file in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu tofu plan -out=<workspace>_<sha>.tfplan ...`
- Apply a saved plan file in the infrastructure container: `docker compose -f infrastructure/compose.yml run --rm tofu tofu apply <workspace>_<sha>.tfplan`

Notes from the current setup:

- `infrastructure/Dockerfile` builds an Alpine image with standalone OpenTofu and Azure Command-Line Interface installed inside a Python virtual environment.
- `infrastructure/compose.yml` mounts the infrastructure directory into `/src`, mounts shared cache and PostgreSQL administration assets, and loads environment variables from `infrastructure/.env`.
- Continuous Integration and Continuous Delivery use OpenTofu directly in GitHub Actions, but local infrastructure work is organized around the dedicated Docker container.

## High-level architecture

- `infrastructure/main.tf` defines the provider setup, the Azure Resource Manager remote state backend, and shared top-level resources such as the resource group, budget, and service plan.
- The configuration is split across focused files such as `appRegistrations.tf`, `containerApps.tf`, `githubActions.tf`, `security.tf`, `virtualMachine.tf`, and `virtualNetwork.tf` rather than one large file.
- `variables.tf` is the central contract for environment-specific values passed from GitHub Actions or local environment variables.
- The remote state backend is intentionally configured at initialization time. The storage account, container, resource group, and key are supplied through `tofu init -backend-config=...` rather than committed as fixed values in Terraform files.
- GitHub Actions derive the workspace from the branch name and then run `tofu init`, `tofu workspace select`, `tofu plan`, and `tofu apply` in that order.
- `infrastructure/README.md` and `.github/workflows/infrastructure.yml` are the best references for the intended local and Continuous Integration and Continuous Delivery deployment flow.

## Key conventions

- Prefer editing the source `.tf` files, not generated or state artifacts. Do not hand-edit `.terraform/`, `.generated/`, `terraform.tfstate`, `*.tfplan`, or other generated lock or state byproducts unless the user explicitly asks.
- Keep workspace-specific behavior compatible with the existing `dev`, `stage`, and `prod` model. Resource naming already depends heavily on `terraform.workspace`.
- Preserve the split between provider and backend configuration in `main.tf` and feature-specific resources in the other `.tf` files.
- When changing backend initialization behavior, remember that the remote state container, storage account, resource group, and key are expected to come from `tofu init -backend-config=...`, not from committed Terraform values.
- Local runs rely on Azure Resource Manager environment variables named `ARM_*`, while GitHub Actions inject many values through workflow environment setup and explicit `-var` arguments. Keep both flows working.
- `variables.tf` includes several Redis database number defaults that need to stay aligned with the application stacks, especially the session, Socket.IO, Celery broker, and Celery result databases.
- The workflow commits `.terraform.lock.hcl` updates. Treat provider version changes as deliberate infrastructure changes and verify them carefully.
