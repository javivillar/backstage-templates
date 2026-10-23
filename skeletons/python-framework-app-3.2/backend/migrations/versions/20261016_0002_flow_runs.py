"""flow runs (block flows: refresquito_fastapi.platform.flow_runs.FlowRun)

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
from alembic import op

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('flow_run',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('flow', sa.String(length=80), nullable=False),
    sa.Column('event', sa.String(length=120), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('detail', sa.Text(), nullable=True),
    sa.Column('started_by', sa.String(length=80), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_flow_run'))
    )
    op.create_index(op.f('ix_flow_run_flow'), 'flow_run', ['flow'], unique=False)
    op.create_index(op.f('ix_flow_run_status'), 'flow_run', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_flow_run_status'), table_name='flow_run')
    op.drop_index(op.f('ix_flow_run_flow'), table_name='flow_run')
    op.drop_table('flow_run')
