"""
Test request_id e logging strutturato: X-Request-ID in response e request_id nei log.
"""

import logging

import pytest
from fastapi.testclient import TestClient


class RecordCaptureHandler(logging.Handler):
    """Handler che accumula i LogRecord emessi."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_response_includes_x_request_id(client: TestClient) -> None:
    """La response include header X-Request-ID (correlazione client)."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-request-id" in (h.lower() for h in response.headers)
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None
    assert len(request_id) > 0


def test_request_id_present_in_logs(client: TestClient) -> None:
    """Almeno un log emesso per la richiesta contiene request_id (log strutturato)."""
    logger = logging.getLogger("app")
    capture = RecordCaptureHandler()
    logger.addHandler(capture)
    try:
        client.get("/api/v1/health")
        records_with_request_id = [
            r for r in capture.records if getattr(r, "request_id", None) is not None
        ]
        assert len(records_with_request_id) >= 1
        for r in records_with_request_id:
            assert getattr(r, "request_id") is not None
            assert len(getattr(r, "request_id")) > 0
    finally:
        logger.removeHandler(capture)


def test_x_request_id_propagation_client_sent(client: TestClient) -> None:
    """Se il client invia X-Request-ID, la response riporta lo stesso valore (correlazione distribuita)."""
    incoming_id = "my-trace-id-abc123"
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": incoming_id},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == incoming_id


def test_x_request_id_propagation_generated_when_absent(client: TestClient) -> None:
    """Se il client non invia X-Request-ID, il server ne genera uno e lo restituisce."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    rid = response.headers.get("X-Request-ID")
    assert rid is not None
    assert len(rid) == 32  # uuid4().hex
