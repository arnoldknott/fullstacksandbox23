# fmt: off
# ruff: noqa
"""""

Revision ID: eee428d55a3b
Revises: a0c481964dcf
Create Date: 2023-12-19 12:43:52.768977+01:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'eee428d55a3b'
down_revision: Union[str, None] = 'a0c481964dcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('demoresource', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('demoresource', sa.Column('last_updated_at', sa.DateTime(), nullable=False))
    op.drop_column('demoresource', 'timezone')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('demoresource', sa.Column('timezone', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('demoresource', 'last_updated_at')
    op.drop_column('demoresource', 'created_at')
    # ### end Alembic commands ###

# fmt: on
