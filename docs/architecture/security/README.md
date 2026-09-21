# Security and OAuth

Security spans OAuth token validation, Redis-backed sessions, REST and Socket.IO guards, identity hierarchies, and resource access policies. The backend implementation is centered in [backend/src/core/security.py](../../../backend/src/core/security.py) and [backend/src/crud/access.py](../../../backend/src/crud/access.py), with shared integration rules in [AGENTS.md](../../../AGENTS.md).

## Implementation plans

- [LinkedIn authentication, account linking, and credential encryption](linkedin-account-linking-plan.md) — agreed guard policies, minimal identity storage, linking/merging, file mappings, dependencies, and validation criteria. This describes planned work, not implemented features.
