"""add expense tables

Revision ID: a1b2c3d4e5f6
Revises: dfc1f9075a17
Create Date: 2025-11-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'dfc1f9075a17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear tabla expense_categories
    op.create_table(
        'expense_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('state', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Crear tabla expenses
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_method', sa.String(30), nullable=False),
        sa.Column('reference', sa.String(100), nullable=True),
        sa.Column('expense_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('part_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('supplier_name', sa.String(150), nullable=True),
        sa.Column('supplier_rut', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('state', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['expense_categories.id'], onupdate='CASCADE', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], onupdate='CASCADE', ondelete='SET NULL'),
    )
    
    # Índices
    op.create_index('ix_expenses_category_id', 'expenses', ['category_id'])
    op.create_index('ix_expenses_part_id', 'expenses', ['part_id'])
    op.create_index('ix_expenses_expense_date', 'expenses', ['expense_date'])
    
    # Insertar categorías por defecto
    op.execute("""
        INSERT INTO expense_categories (name, description, icon) VALUES 
        ('Compras de inventario', 'Compra de repuestos y materiales', 'inventory'),
        ('Servicios', 'Luz, agua, internet, alquiler', 'receipt'),
        ('Nómina', 'Pago de salarios y comisiones', 'people'),
        ('Transporte', 'Combustible, envíos, domicilios', 'local_shipping'),
        ('Herramientas', 'Compra de herramientas y equipos', 'build'),
        ('Marketing', 'Publicidad y promoción', 'campaign'),
        ('Otros', 'Gastos varios', 'more_horiz')
    """)


def downgrade() -> None:
    op.drop_index('ix_expenses_expense_date', table_name='expenses')
    op.drop_index('ix_expenses_part_id', table_name='expenses')
    op.drop_index('ix_expenses_category_id', table_name='expenses')
    op.drop_table('expenses')
    op.drop_table('expense_categories')
