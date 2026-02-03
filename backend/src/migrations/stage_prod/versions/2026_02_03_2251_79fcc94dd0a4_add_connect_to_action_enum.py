# fmt: off
# ruff: noqa
# isort:skip_file
"""add_connect_to_action_enum

Revision ID: 79fcc94dd0a4
Revises: 0ab37093b18c
Create Date: 2026-02-03 22:51:19.577336+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '79fcc94dd0a4'
down_revision: Union[str, None] = '0ab37093b18c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'connect' value to action enum
    op.execute("ALTER TYPE action ADD VALUE 'connect'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # You'd need to recreate the enum without 'connect'
    pass

# fmt: on
