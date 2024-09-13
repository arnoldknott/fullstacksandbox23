# fmt: off
# ruff: noqa
# isort:skip_file
"""""

Revision ID: 3fa4ef096aa5
Revises: dfac770f790f
Create Date: 2024-09-13 10:12:27.575851+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3fa4ef096aa5'
down_revision: Union[str, None] = 'dfac770f790f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'identityhierarchy', ['parent_id', 'child_id'])
    op.create_unique_constraint(None, 'resourcehierarchy', ['parent_id', 'child_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'resourcehierarchy', type_='unique')
    op.drop_constraint(None, 'identityhierarchy', type_='unique')
    # ### end Alembic commands ###

# fmt: on
