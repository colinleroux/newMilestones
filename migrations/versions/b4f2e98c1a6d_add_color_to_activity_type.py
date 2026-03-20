"""add color to activity type

Revision ID: b4f2e98c1a6d
Revises: 9a2d7c13b4e1
Create Date: 2026-03-20 17:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b4f2e98c1a6d"
down_revision = "9a2d7c13b4e1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("activity_type", schema=None) as batch_op:
        batch_op.add_column(sa.Column("color", sa.String(length=20), nullable=True))

    op.execute("UPDATE activity_type SET color = '#0f766e' WHERE color IS NULL")

    with op.batch_alter_table("activity_type", schema=None) as batch_op:
        batch_op.alter_column("color", existing_type=sa.String(length=20), nullable=False)


def downgrade():
    with op.batch_alter_table("activity_type", schema=None) as batch_op:
        batch_op.drop_column("color")
