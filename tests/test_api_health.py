"""
Tests for health API endpoint. Use TestClient only – no business logic, no real server.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """GET /api/v1/health returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_shape(client: TestClient) -> None:
    """Health response has status and version."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["status"] == "ok"
    assert isinstance(data["version"], str)
