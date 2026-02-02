"""add diescription to timelog

Revision ID: 363dd4b1757a
Revises: 9472985a205b
Create Date: 2026-01-16 17:46:51.538526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '363dd4b1757a'
down_revision: Union[str, Sequence[str], None] = '9472985a205b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
