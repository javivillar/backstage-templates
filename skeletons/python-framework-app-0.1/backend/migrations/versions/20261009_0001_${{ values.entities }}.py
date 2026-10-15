"""${{ values.entities }}

Revision ID: 0001
Revises: -
"""
import sqlalchemy as sa
from alembic import op

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('${{ values.entity }}',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('category', sa.String(length=40), nullable=False),
    sa.Column('status', sa.Enum('active', 'pending', 'closed', name='${{ values.entity }}_status', native_enum=False, length=16), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_${{ values.entity }}')),
    sa.UniqueConstraint('name', name=op.f('uq_${{ values.entity }}_name'))
    )
    op.create_index(op.f('ix_${{ values.entity }}_category'), '${{ values.entity }}', ['category'], unique=False)
    op.create_index(op.f('ix_${{ values.entity }}_status'), '${{ values.entity }}', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_${{ values.entity }}_status'), table_name='${{ values.entity }}')
    op.drop_index(op.f('ix_${{ values.entity }}_category'), table_name='${{ values.entity }}')
    op.drop_table('${{ values.entity }}')
