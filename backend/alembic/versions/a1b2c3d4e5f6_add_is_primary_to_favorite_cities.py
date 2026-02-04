"""Add is_primary to favorite cities

Revision ID: a1b2c3d4e5f6
Revises: 23286db355d2
Create Date: 2026-02-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '23286db355d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_primary column to favorite_cities table
    op.add_column('favorite_cities', sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_primary column from favorite_cities table
    op.drop_column('favorite_cities', 'is_primary')
