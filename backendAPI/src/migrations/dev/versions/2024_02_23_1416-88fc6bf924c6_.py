# fmt: off
# ruff: noqa
"""""

Revision ID: 88fc6bf924c6
Revises: 2cbbceed3055
Create Date: 2024-02-23 14:16:28.508404+01:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '88fc6bf924c6'
down_revision: Union[str, None] = '2cbbceed3055'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_accessed_at', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_accessed_at')
    # ### end Alembic commands ###

# fmt: on
