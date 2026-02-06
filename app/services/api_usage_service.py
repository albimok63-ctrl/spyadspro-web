"""
ApiUsage service – registrazione utilizzo API per chiave. Nessuna dipendenza FastAPI.
"""

from app.repositories.api_usage_repository import ApiUsageRepository


class ApiUsageService:
    """Registra ogni richiesta API associata a una API key valida."""

    def __init__(self, repository: ApiUsageRepository) -> None:
        self._repository = repository

    def record_usage(
        self,
        api_key_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Persiste un record di utilizzo."""
        self._repository.create_usage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
        )
