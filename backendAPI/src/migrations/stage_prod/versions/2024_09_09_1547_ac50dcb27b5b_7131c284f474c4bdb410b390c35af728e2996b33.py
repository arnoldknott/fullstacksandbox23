# fmt: off
# ruff: noqa
# isort:skip_file
""""7131c284f474c4bdb410b390c35af728e2996b33"

Revision ID: ac50dcb27b5b
Revises: a127d6490978
Create Date: 2024-09-09 15:47:05.748422+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ac50dcb27b5b'
down_revision: Union[str, None] = 'a127d6490978'
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