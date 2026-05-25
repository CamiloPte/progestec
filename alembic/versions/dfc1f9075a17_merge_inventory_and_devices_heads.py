"""merge inventory and devices heads

Revision ID: dfc1f9075a17
Revises: 0e3f0f2d4e88, 21143437fbb7
Create Date: 2025-11-26 20:40:00.447331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfc1f9075a17'
down_revision: Union[str, None] = ('0e3f0f2d4e88', '21143437fbb7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
