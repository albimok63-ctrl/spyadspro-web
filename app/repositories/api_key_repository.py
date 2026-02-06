"""
ApiKey repository – persistenza chiavi API su DB. Nessuna logica HTTP.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.api_key_orm import ApiKeyORM


class ApiKeyRepository:
    """Accesso alle api_keys in database."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_key(self, key: str) -> ApiKeyORM | None:
        """Restituisce l'ApiKey con la chiave data, o None se non esiste."""
        return self._db.query(ApiKeyORM).filter(ApiKeyORM.key == key).first()

    def is_valid_key(self, key: str) -> bool:
        """True se esiste una api_key con la chiave data e is_active=True."""
        row = self.get_by_key(key)
        return row is not None and row.is_active
