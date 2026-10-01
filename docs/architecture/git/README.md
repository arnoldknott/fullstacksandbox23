# Git

Feature and fix branches start from `dev` and merge back into `dev`. Promote changes in order from `dev` to `stage`, then from `stage` to `main` after staging verification.

| Branch | Deployment environments |
| --- | --- |
| `dev` | `dev` and `test` |
| `stage` | `stage` |
| `main` | `prod` |

Local hook examples live in [hooks](../../../hooks/), and automation workflows live in [.github/workflows](../../../.github/workflows/). The root [AGENTS.md](../../../AGENTS.md#branch-and-environment-model) is authoritative for branch and environment policy; infrastructure work additionally follows its [workspace deployment flow](../../infrastructure/README.md#deployment-flow) and requires plan review before apply.
