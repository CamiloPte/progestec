"""merge_expense_and_invoices

Revision ID: d4ddc8e938f0
Revises: 17ab84ac99cc, a1b2c3d4e5f6
Create Date: 2025-11-27 06:16:45.871588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4ddc8e938f0'
down_revision: Union[str, None] = ('17ab84ac99cc', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
