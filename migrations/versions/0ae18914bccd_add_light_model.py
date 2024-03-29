"""Add Light model

Revision ID: 0ae18914bccd
Revises:
Create Date: 2019-12-30 03:08:53.019423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ae18914bccd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('light',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=32), nullable=False),
        sa.Column('is_powered_on', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('length(name) >= 3 and length(name) <= 32')
    )
    op.create_index(op.f('ix_light_name'), 'light', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_light_name'), table_name='light')
    op.drop_table('light')
    # ### end Alembic commands ###
