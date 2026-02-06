"""
Test API usage tracking: verifica che le richieste vengano processate correttamente
con il middleware UsageTracker attivo.
"""

import pytest
from fastapi.testclient import TestClient


def test_request_processed_with_usage_tracking(client: TestClient) -> None:
    """Una richiesta HTTP viene processata correttamente con il middleware di usage tracking attivo."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
