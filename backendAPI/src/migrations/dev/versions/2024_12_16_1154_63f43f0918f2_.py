# fmt: off
# ruff: noqa
# isort:skip_file
"""""

Revision ID: 63f43f0918f2
Revises: bb4796208f67
Create Date: 2024-12-16 11:54:56.278643+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '63f43f0918f2'
down_revision: Union[str, None] = 'bb4796208f67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'is_publicAIuser',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'is_publicAIuser',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###

# fmt: on
