"""added admin to courses table 3

Revision ID: 53552bee0564
Revises: c58ac5345de9
Create Date: 2026-03-10 16:04:51.587774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53552bee0564'
down_revision: Union[str, Sequence[str], None] = 'c58ac5345de9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
