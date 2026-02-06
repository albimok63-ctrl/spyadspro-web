"""
ApiKey service – validazione chiavi API. Nessuna dipendenza FastAPI.
"""

from __future__ import annotations

from app.db.models.api_key_orm import ApiKeyORM
from app.repositories.api_key_repository import ApiKeyRepository


class ApiKeyService:
    """Validazione API key. Dipende solo dal repository."""

    def __init__(self, repository: ApiKeyRepository) -> None:
        self._repository = repository

    def validate_api_key(self, key: str) -> bool:
        """True se la chiave è valida (presente e attiva)."""
        return self._repository.is_valid_key(key)

    def get_api_key_record(self, key: str) -> ApiKeyORM | None:
        """Restituisce il record ApiKey se esiste e è attivo, altrimenti None."""
        row = self._repository.get_by_key(key)
        return row if (row is not None and row.is_active) else None
