"""add api_keys table and seed test key

Revision ID: 002
Revises: 001
Create Date: 2025-02-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(key)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_api_keys_key ON api_keys (key)
        """
    )
    # Dati di test: API key "test-api-key" (insert solo se non esiste)
    op.execute(
        """
        INSERT OR IGNORE INTO api_keys (key, name, is_active, created_at)
        VALUES ('test-api-key', 'Test API Key', 1, CURRENT_TIMESTAMP)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS api_keys")
