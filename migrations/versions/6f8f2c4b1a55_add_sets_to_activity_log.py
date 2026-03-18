"""add sets to activity log

Revision ID: 6f8f2c4b1a55
Revises: 3c7b0d1f2d44
Create Date: 2026-03-18 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "6f8f2c4b1a55"
down_revision = "3c7b0d1f2d44"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("activity_log", schema=None) as batch_op:
        batch_op.add_column(sa.Column("sets", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("activity_log", schema=None) as batch_op:
        batch_op.drop_column("sets")
