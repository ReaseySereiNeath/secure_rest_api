"""legacy no-op revision

Revision ID: 69c21dc819d1
Revises:
Create Date: 2025-10-29 14:43:27.743678
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


revision = "69c21dc819d1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op legacy revision."""
    pass


def downgrade() -> None:
    """No-op legacy revision."""
    pass
