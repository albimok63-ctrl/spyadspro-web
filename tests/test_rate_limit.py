"""
Test rate limiting: sotto limite → 200, oltre limite → 429.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import rate_limit_dependency


def test_rate_limit_under_limit_returns_200(client: TestClient) -> None:
    """Con rate limit sotto soglia le richieste restituiscono 200."""
    orig = app.dependency_overrides.pop(rate_limit_dependency, None)
    try:
        with patch("app.core.rate_limit.check_rate_limit"):
            response = client.get("/api/v1/items")
        assert response.status_code == 200
    finally:
        if orig is not None:
            app.dependency_overrides[rate_limit_dependency] = orig


def test_rate_limit_over_limit_returns_429(client: TestClient) -> None:
    """Quando il rate limit è superato la API restituisce 429."""
    from fastapi import HTTPException

    orig = app.dependency_overrides.pop(rate_limit_dependency, None)
    try:
        with patch("app.core.rate_limit.check_rate_limit") as m:
            m.side_effect = HTTPException(status_code=429, detail="Too many requests; try again later.")
            response = client.get("/api/v1/items")
        assert response.status_code == 429
        assert "Too many requests" in response.json().get("detail", "")
    finally:
        if orig is not None:
            app.dependency_overrides[rate_limit_dependency] = orig