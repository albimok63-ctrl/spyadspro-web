"""
Test esposizione metriche Prometheus: endpoint /metrics e label method, path, status_code.
"""

import pytest
from fastapi.testclient import TestClient


def test_metrics_endpoint_returns_200(client: TestClient) -> None:
    """GET /metrics restituisce 200."""
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_endpoint_exposes_prometheus_format(client: TestClient) -> None:
    """GET /metrics espone http_requests_total e http_request_duration_seconds."""
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "http_requests_total" in text
    assert "http_request_duration_seconds" in text


def test_metrics_content_type(client: TestClient) -> None:
    """GET /metrics ha Content-Type per Prometheus (text/plain)."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("Content-Type", "")


def test_metrics_record_after_request(client: TestClient) -> None:
    """Dopo una richiesta a /api/v1/health, le metriche includono method, path, status_code."""
    client.get("/api/v1/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    # Deve esserci almeno una riga con le label della richiesta appena fatta
    assert "http_requests_total" in text
    assert "method=\"GET\"" in text or "method='GET'" in text
    assert "/api/v1/health" in text
    assert "status_code=\"200\"" in text or "status_code='200'" in text
