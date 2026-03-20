"""add step activity fields

Revision ID: 9a2d7c13b4e1
Revises: 6f8f2c4b1a55
Create Date: 2026-03-20 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9a2d7c13b4e1"
down_revision = "6f8f2c4b1a55"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("step", schema=None) as batch_op:
        batch_op.add_column(sa.Column("log_activity", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("activity_type_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("duration_seconds", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("distance_m", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("weight_kg", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("sets", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("reps", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("activity_notes", sa.Text(), nullable=True))
        batch_op.create_foreign_key("fk_step_activity_type_id", "activity_type", ["activity_type_id"], ["id"])


def downgrade():
    with op.batch_alter_table("step", schema=None) as batch_op:
        batch_op.drop_constraint("fk_step_activity_type_id", type_="foreignkey")
        batch_op.drop_column("activity_notes")
        batch_op.drop_column("reps")
        batch_op.drop_column("sets")
        batch_op.drop_column("weight_kg")
        batch_op.drop_column("distance_m")
        batch_op.drop_column("duration_seconds")
        batch_op.drop_column("activity_type_id")
        batch_op.drop_column("log_activity")
