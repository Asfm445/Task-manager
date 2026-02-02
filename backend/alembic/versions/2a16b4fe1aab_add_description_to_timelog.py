"""add description to timelog

Revision ID: 2a16b4fe1aab
Revises: 363dd4b1757a
Create Date: 2026-01-16 19:02:45.047374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a16b4fe1aab'
down_revision: Union[str, Sequence[str], None] = '363dd4b1757a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
