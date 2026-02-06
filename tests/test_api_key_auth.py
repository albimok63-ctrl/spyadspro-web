"""
Test autenticazione API Key: accesso senza chiave → 401, chiave non valida → 401, chiave valida → 200.
"""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.api_key_orm import ApiKeyORM
from app.main import app
from app.core.dependencies import (
    get_api_key,
    get_current_user,
    get_db,
    rate_limit_dependency,
)


TEST_API_KEY = "test-api-key"


def _yield_test_db():
    """Fornisce una sessione sul DB di test (stesso engine di conftest)."""
    from tests.conftest import TEST_SESSION_FACTORY

    db = TEST_SESSION_FACTORY()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def ensure_test_api_key_in_db(db_session: Session) -> Generator[None, None, None]:
    """Inserisce la API key di test nel DB se non esiste."""
    existing = db_session.query(ApiKeyORM).filter(ApiKeyORM.key == TEST_API_KEY).first()
    if not existing:
        row = ApiKeyORM(key=TEST_API_KEY, name="Test API Key", is_active=True)
        db_session.add(row)
        db_session.commit()
    yield


def test_access_without_api_key_returns_401(client: TestClient) -> None:
    """GET /api/v1/items senza header X-API-Key restituisce 401."""
    orig_api_key = app.dependency_overrides.pop(get_api_key, None)
    try:
        response = client.get("/api/v1/items")
        assert response.status_code == 401
        assert "X-API-Key" in response.json().get("detail", "")
    finally:
        if orig_api_key is not None:
            app.dependency_overrides[get_api_key] = orig_api_key


def test_access_with_invalid_api_key_returns_401(client: TestClient) -> None:
    """GET /api/v1/items con X-API-Key non valida restituisce 401."""
    orig_api_key = app.dependency_overrides.pop(get_api_key, None)
    try:
        response = client.get(
            "/api/v1/items",
            headers={"X-API-Key": "invalid-key"},
        )
        assert response.status_code == 401
        assert "Invalid" in response.json().get("detail", "") or "invalid" in response.json().get("detail", "").lower()
    finally:
        if orig_api_key is not None:
            app.dependency_overrides[get_api_key] = orig_api_key


def test_access_with_valid_api_key_returns_200(
    client: TestClient, ensure_test_api_key_in_db: None
) -> None:
    """GET /api/v1/items con X-API-Key valida e token JWT restituisce 200."""
    orig_api_key = app.dependency_overrides.pop(get_api_key, None)
    orig_user = app.dependency_overrides.pop(get_current_user, None)
    orig_rate = app.dependency_overrides.pop(rate_limit_dependency, None)
    orig_get_db = app.dependency_overrides.pop(get_db, None)
    try:
        app.dependency_overrides[get_db] = _yield_test_db
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        with patch("app.core.rate_limit.check_rate_limit"):
            response = client.get(
                "/api/v1/items",
                headers={
                    "X-API-Key": TEST_API_KEY,
                    "Authorization": f"Bearer {token}",
                },
            )
        assert response.status_code == 200
    finally:
        if orig_api_key is not None:
            app.dependency_overrides[get_api_key] = orig_api_key
        if orig_user is not None:
            app.dependency_overrides[get_current_user] = orig_user
        if orig_rate is not None:
            app.dependency_overrides[rate_limit_dependency] = orig_rate
        if orig_get_db is not None:
            app.dependency_overrides[get_db] = orig_get_db
        else:
            app.dependency_overrides.pop(get_db, None)
