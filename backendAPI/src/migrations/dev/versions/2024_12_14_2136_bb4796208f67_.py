# fmt: off
# ruff: noqa
# isort:skip_file
"""""

Revision ID: bb4796208f67
Revises: 264046d1d607
Create Date: 2024-12-14 21:36:16.947612+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'bb4796208f67'
down_revision: Union[str, None] = '264046d1d607'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_publicAIuser', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_publicAIuser')
    # ### end Alembic commands ###

# fmt: on
