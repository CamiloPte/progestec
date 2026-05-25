"""add inventory tables and columns

Revision ID: 0e3f0f2d4e88
Revises: 21fe7d6247a2
Create Date: 2025-11-25 19:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e3f0f2d4e88'
down_revision = '21fe7d6247a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('parts', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('parts', sa.Column('manufacturer', sa.String(length=100), nullable=True))
    op.add_column('parts', sa.Column('compatible_models', sa.Text(), nullable=True))
    op.add_column('parts', sa.Column('preferred_vendor', sa.String(length=150), nullable=True))
    op.add_column('parts', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('parts', sa.Column('stock_current', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('parts', sa.Column('stock_min', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('parts', sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default=sa.text('0')))

    op.create_table(
        'part_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('state', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), server_onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('document_ref', sa.String(length=100), nullable=True),
        sa.Column('movement_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('responsible_user_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['responsible_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_part_movements_part_id'), 'part_movements', ['part_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_part_movements_part_id'), table_name='part_movements')
    op.drop_table('part_movements')

    op.drop_column('parts', 'requires_approval')
    op.drop_column('parts', 'stock_min')
    op.drop_column('parts', 'stock_current')
    op.drop_column('parts', 'notes')
    op.drop_column('parts', 'preferred_vendor')
    op.drop_column('parts', 'compatible_models')
    op.drop_column('parts', 'manufacturer')
    op.drop_column('parts', 'category')
