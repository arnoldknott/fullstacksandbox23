# PostgreSQL

PostgreSQL stores application entities, hierarchies, access policies, and access logs. The backend accesses it through asynchronous SQLModel and SQLAlchemy sessions, manages schema changes through the Alembic trees under [backend/src/migrations](../../backend/src/migrations/), and configures local and test services through the root Docker Compose files.
