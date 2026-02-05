"""
Unit tests for HealthService. Pure service test with mock repository – no HTTP, no server.
"""

import pytest

from app.repositories.health_repository import HealthRecord, HealthRepository
from app.services.health_service import HealthResult, HealthService


class MockHealthRepository(HealthRepository):
    """Mock repository for testing. Overrides get_status only."""

    def __init__(self, record: HealthRecord) -> None:
        self._record = record

    def get_status(self) -> HealthRecord:
        return self._record


def test_health_service_returns_result_from_repository() -> None:
    """Service maps repository record to HealthResult."""
    record = HealthRecord(status="ok", version="2.0.0")
    repo = MockHealthRepository(record)
    service = HealthService(repository=repo)
    result = service.get_health()
    assert isinstance(result, HealthResult)
    assert result.status == "ok"
    assert result.version == "2.0.0"


def test_health_service_propagates_repository_status() -> None:
    """Service does not add logic – it propagates repository data."""
    record = HealthRecord(status="degraded", version="1.0.0")
    repo = MockHealthRepository(record)
    service = HealthService(repository=repo)
    result = service.get_health()
    assert result.status == "degraded"
    assert result.version == "1.0.0"
