# Infrastructure

The [infrastructure](../../infrastructure/) directory contains OpenTofu configuration for Azure resources, organized into `dev`, `stage`, and `prod` workspaces. The repository maps the `dev`, `stage`, and `main` branches to those workspaces respectively.

Run local infrastructure tooling through the dedicated container and supported repository scripts, not directly on the host. See [infrastructure/AGENTS.md](../../infrastructure/AGENTS.md) for the container commands and environment setup.

## Deployment flow

The local [deployment script](../../scripts/deploy_infrastructure.sh) selects a workspace from the current branch, initializes OpenTofu, and produces a plan. It prompts before applying changes; review the plan and explicitly confirm before proceeding. The script rejects branches outside the three environment branches.

The [infrastructure workflow](../../.github/workflows/infrastructure.yml) runs on pushes to `dev`, `stage`, or `main` when infrastructure-owned files change. It creates and stores a plan, then applies it in a separate `infrastructure-apply` GitHub environment, which is the approval boundary for the automated deployment. Follow the plan output and environment protections when reviewing a deployment.

The tracked plan files and OpenTofu state in the infrastructure directory are generated artifacts, not configuration sources. Edit the `.tf` source files and follow the existing workspace workflow. See the [infrastructure README](../../infrastructure/README.md) for deployment setup and [application encryption rotation](../architecture/security/README.md#rotation-and-deployment) for the key-rotation deployment requirements.
