"""
Health service – business logic only. No FastAPI, no HTTP.
Depends only on repository (and optionally core/config).
"""

from dataclasses import dataclass

from app.repositories.health_repository import HealthRepository, HealthRecord


@dataclass(frozen=True)
class HealthResult:
    """Domain result of a health check. No HTTP/response types."""

    status: str
    version: str


class HealthService:
    """Business logic for health. No knowledge of FastAPI or HTTP."""

    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    def get_health(self) -> HealthResult:
        """Compute health result from repository data."""
        record: HealthRecord = self._repository.get_status()
        return HealthResult(status=record.status, version=record.version)
