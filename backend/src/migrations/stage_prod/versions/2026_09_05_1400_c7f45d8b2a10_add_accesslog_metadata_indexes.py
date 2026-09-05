# fmt: off
# ruff: noqa
# isort:skip_file
"""add_accesslog_metadata_indexes

Revision ID: c7f45d8b2a10
Revises: 79fcc94dd0a4
Create Date: 2026-09-05 14:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7f45d8b2a10"
down_revision: Union[str, None] = "79fcc94dd0a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_accesslog_created_resource_time",
        "accesslog",
        ["resource_id", "time"],
        unique=False,
        postgresql_where=sa.text("action = 'own' AND status_code = 201"),
    )
    op.create_index(
        "ix_accesslog_modified_resource_time",
        "accesslog",
        ["resource_id", "time"],
        unique=False,
        postgresql_where=sa.text("action = 'write' AND status_code = 200"),
    )


def downgrade() -> None:
    op.drop_index("ix_accesslog_modified_resource_time", table_name="accesslog")
    op.drop_index("ix_accesslog_created_resource_time", table_name="accesslog")

# fmt: on
