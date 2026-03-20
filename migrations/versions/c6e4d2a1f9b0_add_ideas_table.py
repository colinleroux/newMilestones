"""add ideas table

Revision ID: c6e4d2a1f9b0
Revises: b4f2e98c1a6d
Create Date: 2026-03-20 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c6e4d2a1f9b0"
down_revision = "b4f2e98c1a6d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "idea",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("idea")
