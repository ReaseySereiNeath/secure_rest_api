"""legacy placeholder revision

Revision ID: ecfcfaa988c5
Revises: 69c21dc819d1
Create Date: 2025-10-29 15:18:01.540603
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


revision = "ecfcfaa988c5"
down_revision = "69c21dc819d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op legacy revision."""
    pass


def downgrade() -> None:
    """No-op legacy revision."""
    pass
