# fmt: off
# ruff: noqa
"""""

Revision ID: 4c9b010de752
Revises: a16bba0ff83e
Create Date: 2024-02-16 14:55:01.182791+01:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4c9b010de752'
down_revision: Union[str, None] = 'a16bba0ff83e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('azuregroup',
    sa.Column('azure_tenant_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('azure_group_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('azure_group_id')
    )
    op.create_index(op.f('ix_azuregroup_azure_group_id'), 'azuregroup', ['azure_group_id'], unique=False)
    op.create_table('category',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_table('tag',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tag_id')
    )
    op.create_table('user',
    sa.Column('azure_tenant_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('azure_user_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_azure_user_id'), 'user', ['azure_user_id'], unique=True)
    op.create_table('azuregroupuserlink',
    sa.Column('azure_group_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('azure_user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['azure_group_id'], ['azuregroup.azure_group_id'], ),
    sa.ForeignKeyConstraint(['azure_user_id'], ['user.azure_user_id'], ),
    sa.PrimaryKeyConstraint('azure_group_id', 'azure_user_id')
    )
    op.create_table('demoresource',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('language', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('demo_resource_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_updated_at', sa.DateTime(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.category_id'], ),
    sa.PrimaryKeyConstraint('demo_resource_id')
    )
    op.create_table('demoresourcetaglink',
    sa.Column('demo_resource_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['demo_resource_id'], ['demoresource.demo_resource_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ),
    sa.PrimaryKeyConstraint('demo_resource_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('demoresourcetaglink')
    op.drop_table('demoresource')
    op.drop_table('azuregroupuserlink')
    op.drop_index(op.f('ix_user_azure_user_id'), table_name='user')
    op.drop_table('user')
    op.drop_table('tag')
    op.drop_table('category')
    op.drop_index(op.f('ix_azuregroup_azure_group_id'), table_name='azuregroup')
    op.drop_table('azuregroup')
    # ### end Alembic commands ###

# fmt: on
