"""legacy placeholder revision

Revision ID: 234d22297607
Revises: ecfcfaa988c5
Create Date: 2025-10-29 15:21:52.085804
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


revision = "234d22297607"
down_revision = "ecfcfaa988c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op legacy revision."""
    pass


def downgrade() -> None:
    """No-op legacy revision."""
    pass
