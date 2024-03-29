"""Add table schemas

Revision ID: a92a5e428610
Revises: 0ae18914bccd
Create Date: 2020-02-28 03:02:09.991997

"""
from alembic import op
import sqlalchemy as sa

from app.settings import (
    DATABASE_CONFIG as DB,
    DATABASE_SCHEMAS as SCHEMAS
)


# revision identifiers, used by Alembic.
revision = 'a92a5e428610'
down_revision = '0ae18914bccd'
branch_labels = None
depends_on = None


def upgrade():
    for schema in SCHEMAS:
        op.execute(f'CREATE SCHEMA IF NOT EXISTS {schema} AUTHORIZATION {DB["user"]}')
        op.execute(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema} TO {DB["user"]}')

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_public_light_name'), 'light', ['name'], unique=True, schema='public')
    op.drop_index('ix_light_name', table_name='light')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_light_name', 'light', ['name'], unique=True)
    op.drop_index(op.f('ix_public_light_name'), table_name='light', schema='public')
    # ### end Alembic commands ###

    # XXX: Don't drop schemas on downgrade. You could end up destroying
    # more than you bargained for.
