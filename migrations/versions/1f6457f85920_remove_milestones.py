"""remove milestones

Revision ID: 1f6457f85920
Revises: 7185a7427f9a
Create Date: 2026-03-17 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f6457f85920'
down_revision = '7185a7427f9a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.drop_column('milestones_enabled')

    with op.batch_alter_table('step', schema=None) as batch_op:
        batch_op.drop_column('milestone_id')

    op.drop_table('milestone')


def downgrade():
    op.create_table(
        'milestone',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('achieved', sa.Boolean(), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['goal_id'], ['goal.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    with op.batch_alter_table('step', schema=None) as batch_op:
        batch_op.add_column(sa.Column('milestone_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_step_milestone_id_milestone', 'milestone', ['milestone_id'], ['id'])

    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('milestones_enabled', sa.Boolean(), nullable=True))
