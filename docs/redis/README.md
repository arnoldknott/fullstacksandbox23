# Redis

Redis supports cached sessions and tokens, Socket.IO message coordination, and Celery transport. Runtime configuration and access-control-list templates live in [cache](../../cache/), while service wiring and environment-specific settings are defined by the application and Docker Compose configuration.

Planned authentication-cache encryption and compatibility rollout are described in the [LinkedIn authentication and account-linking implementation plan](../architecture/security/linkedin-account-linking-plan.md#f-compatible-encrypted-cache-persistence). Session JSON path access is retained; provider credentials and necessary sensitive subdocuments are encrypted at the application boundary.
