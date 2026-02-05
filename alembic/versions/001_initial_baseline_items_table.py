"""initial baseline items table

Revision ID: 001
Revises:
Create Date: 2025-02-03 (baseline)

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Idempotente per SQLite: CREATE TABLE IF NOT EXISTS.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(1000) NOT NULL DEFAULT ''
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS items")
