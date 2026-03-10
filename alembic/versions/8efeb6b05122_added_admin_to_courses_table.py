"""added admin to courses table

Revision ID: 8efeb6b05122
Revises: dd9fa3a32cdd
Create Date: 2026-03-10 16:03:11.169000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8efeb6b05122'
down_revision: Union[str, Sequence[str], None] = 'dd9fa3a32cdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
