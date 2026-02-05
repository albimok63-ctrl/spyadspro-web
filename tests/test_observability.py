"""
Suite pytest per osservabilità: logging, metrics, tracing (request_id).
Garantisce che non regrediscano. Mock controllati, nessun test flaky.
"""

import logging
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class RecordCaptureHandler(logging.Handler):
    """Handler che accumula i LogRecord emessi (mock controllato dei log)."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


# --- /metrics disponibile ---


def test_observability_metrics_available(client: TestClient) -> None:
    """GET /metrics è disponibile: 200, Content-Type Prometheus, metriche base presenti."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("Content-Type", "")
    text = response.text
    assert "http_requests_total" in text
    assert "http_request_duration_seconds" in text


def test_observability_metrics_expose_after_request(client: TestClient) -> None:
    """Dopo una richiesta, /metrics espone metriche con method e handler (instrumentator, non flaky)."""
    client.get("/api/v1/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "http_requests_total" in text or "http_request_duration_seconds" in text
    assert "GET" in text
    assert "/api/v1/health" in text


# --- request_id presente (tracing/correlazione) ---


def test_observability_request_id_present_in_response(client: TestClient) -> None:
    """Ogni response include X-Request-ID (correlazione, non flaky)."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    rid = response.headers.get("X-Request-ID")
    assert rid is not None
    assert len(rid) >= 1


def test_observability_request_id_present_in_logs(client: TestClient) -> None:
    """Almeno un log per richiesta contiene request_id (logging strutturato, mock capture)."""
    logger = logging.getLogger("app")
    capture = RecordCaptureHandler()
    logger.addHandler(capture)
    try:
        client.get("/api/v1/health")
        with_request_id = [r for r in capture.records if getattr(r, "request_id", None)]
        assert len(with_request_id) >= 1
        assert all(len(getattr(r, "request_id")) > 0 for r in with_request_id)
    finally:
        logger.removeHandler(capture)


def test_observability_request_id_propagation_client_sent(client: TestClient) -> None:
    """Se il client invia X-Request-ID, la response riporta lo stesso valore (mock controllato)."""
    incoming = "trace-observability-test-123"
    response = client.get("/api/v1/health", headers={"X-Request-ID": incoming})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == incoming


# --- readiness fallisce se Redis down (mock controllato, non flaky) ---


def test_observability_readiness_fails_when_redis_down(client: TestClient) -> None:
    """Readiness restituisce 503 e body not_ready quando Redis non è raggiungibile (mock)."""
    with patch("app.main.get_redis_client", return_value=None):
        response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data.get("status") == "not_ready"
    assert data.get("redis") == "unavailable"


def test_observability_readiness_succeeds_when_redis_up(client: TestClient) -> None:
    """Readiness restituisce 200 quando Redis è raggiungibile (mock)."""
    with patch("app.main.get_redis_client", return_value=object()):
        response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ready"
    assert data.get("redis") == "ok"
