# Copilot instructions for this repository

## General guidelines

- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.
- Follow software design principles such as YAGNI (You Aren't Gonna Need It), SOLID, KISS (Keep It Simple, Stupid), and DRY (Don't Repeat Yourself) to ensure maintainable and clean code.
- Use the versions of dependencies specified in `pyproject.toml` and `package.json` when generating code. If a version is not specified, pull the latest version matching the constraints in these files.
- Use Context7 to get the latest version of the documentation for the libraries and frameworks you are using.
- Do not use any abbreviations without explaining them For example, if you use "API", you should first write "Application Programming Interface (API)" before using "API" in the rest of the text.

## Repository structure

This repository contains the three main parts:

- `infrastructure/`: OpenTofu configuration and Azure-related setup
- `backend/`: FastAPI + Socket.IO + Celery backend
- `frontend_svelte/`: SvelteKit + MaterialDesign + FlyonUI frontend

Detailed app-specific guidance lives in the path-specific instruction files under `.github/instructions/`.

## Environments & branches

There are 4 main environments, which are linked to 3 branches to be aware of:

- `dev` branch: corresponding to environment `dev` - development environment - and `test` environment, which is used for active development and may be less stable. All development work should be done in feature branches off of `dev`, and then merged back into `dev` when ready. The `test` environment is used for testing new features and changes before they are merged into `stage`.
- `stage` branch: corresponding to environment `stage` - staging environment, which is deployed to Azure and is used for pre-production testing and should closely mirror the production environment. Manually check the deployed staging servers before approving deployment to production. When merging to `stage`, ensure that the staging environment is updated and tested before merging to `main`.
- `main` branch: corresponding to environment `prod` - the production environment, which is deployed to Azure and should be stable and well-tested.

All new features and bug fixes should be developed in feature branches off of `dev`. Feature branches are Called `feature/<description>` or `fix/<description>`. When a feature or bug fix is complete, it should be merged back into `dev`. When `dev` has accumulated enough changes and is stable, it can be merged into `stage` for staging testing. After staging testing is complete and the changes are verified, `stage` can be merged into `main` for production deployment.

Merging order: `feat/<description>` or `fix/<description>` -> `dev` -> `stage` -> `main`

## Shared integration guidance

- Keep frontend and backend auth/session behavior aligned. The frontend depends on backend session-backed auth flows and the `/api/v1`, `/socketio/v1`, and `/ws/v1` contracts.
- When you change a shared API, auth, websocket, or session contract, check both sides of the integration instead of treating either app in isolation.
- Containerized development and CI flows are driven from the repository root with `compose.yml` plus override files such as `compose.override.yml` and `compose.override.test.yml`.
- The devcontainer entrypoints are `.devcontainer/frontend/devcontainer.json` and `.devcontainer/backend/devcontainer.json`.
