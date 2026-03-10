"""changed to uuid

Revision ID: 8d6fc6da2ba7
Revises: 53552bee0564
Create Date: 2026-03-10 16:52:23.786216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d6fc6da2ba7'
down_revision: Union[str, Sequence[str], None] = '53552bee0564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
