# fmt: off
# ruff: noqa
"""""

Revision ID: 8a72b9e643e9
Revises: 52a27a4fcaea
Create Date: 2023-12-20 21:31:33.715445+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8a72b9e643e9'
down_revision: Union[str, None] = '52a27a4fcaea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

# fmt: on