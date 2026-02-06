"""
Test autenticazione JWT: login, 401 senza token, 200 con token valido.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user, rate_limit_dependency


def test_login_ok(client: TestClient) -> None:
    """POST /api/v1/auth/login con admin/admin restituisce 200 e access_token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("token_type") == "bearer"
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_login_invalid_returns_401(client: TestClient) -> None:
    """POST /api/v1/auth/login con credenziali errate restituisce 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401


def test_items_without_token_returns_401(client: TestClient) -> None:
    """GET /api/v1/items senza Authorization header restituisce 401."""
    orig_user = app.dependency_overrides.pop(get_current_user, None)
    orig_rate = app.dependency_overrides.pop(rate_limit_dependency, None)
    try:
        response = client.get("/api/v1/items")
        assert response.status_code == 401
    finally:
        if orig_user is not None:
            app.dependency_overrides[get_current_user] = orig_user
        if orig_rate is not None:
            app.dependency_overrides[rate_limit_dependency] = orig_rate


def test_items_with_valid_token_returns_200(client: TestClient) -> None:
    """GET /api/v1/items con Bearer token valido restituisce 200."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    orig_user = app.dependency_overrides.pop(get_current_user, None)
    orig_rate = app.dependency_overrides.pop(rate_limit_dependency, None)
    try:
        with patch("app.core.rate_limit.check_rate_limit"):
            response = client.get(
                "/api/v1/items",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 200
    finally:
        if orig_user is not None:
            app.dependency_overrides[get_current_user] = orig_user
        if orig_rate is not None:
            app.dependency_overrides[rate_limit_dependency] = orig_rate
