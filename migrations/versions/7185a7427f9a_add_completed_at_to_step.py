"""add completed_at to step

Revision ID: 7185a7427f9a
Revises: 
Create Date: 2026-03-17 13:34:36.221802

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7185a7427f9a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('step', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completed_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('step', schema=None) as batch_op:
        batch_op.drop_column('completed_at')
