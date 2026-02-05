"""
Test readiness probe /ready: verifica Redis, metriche e logging.
"""

import logging
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class RecordCaptureHandler(logging.Handler):
    """Handler che accumula i LogRecord emessi."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_ready_returns_503_when_redis_unavailable(client: TestClient) -> None:
    """GET /ready restituisce 503 quando Redis non è raggiungibile (mock: nessun flaky)."""
    with patch("app.main.get_redis_client", return_value=None):
        response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["redis"] == "unavailable"


def test_ready_returns_200_when_redis_available(client: TestClient) -> None:
    """GET /ready restituisce 200 quando Redis è raggiungibile (mock)."""
    with patch("app.main.get_redis_client") as m:
        m.return_value = object()  # client fittizio
        response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["redis"] == "ok"


def test_ready_logs_warning_on_failure(client: TestClient) -> None:
    """In caso di readiness failure viene emesso un log di warning."""
    logger = logging.getLogger("app")
    capture = RecordCaptureHandler()
    logger.addHandler(capture)
    try:
        with patch("app.main.get_redis_client", return_value=None):
            client.get("/ready")
        warnings = [r for r in capture.records if r.levelno >= logging.WARNING]
        assert any("Readiness failed" in r.getMessage() or "Redis" in r.getMessage() for r in warnings)
    finally:
        logger.removeHandler(capture)


def test_health_liveness_unchanged(client: TestClient) -> None:
    """GET /api/v1/health (liveness) invariato: 200 e shape backward compatible."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert "version" in data


def test_metrics_health_checks_total_after_health_and_ready(client: TestClient) -> None:
    """Dopo liveness e readiness (mock), /metrics espone health_checks_total con type e status (non flaky)."""
    client.get("/api/v1/health")  # liveness success
    with patch("app.main.get_redis_client", return_value=None):
        client.get("/ready")  # readiness failure
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "health_checks_total" in text
    assert "liveness" in text
    assert "readiness" in text
    assert "success" in text  # liveness
    assert "failure" in text  # readiness (Redis down)
