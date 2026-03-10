"""added admin to courses table 2

Revision ID: c58ac5345de9
Revises: 8efeb6b05122
Create Date: 2026-03-10 16:04:07.444190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c58ac5345de9'
down_revision: Union[str, Sequence[str], None] = '8efeb6b05122'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
