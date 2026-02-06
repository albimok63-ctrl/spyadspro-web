"""
Test API Key Usage Tracking: richiesta con API key valida crea record in api_usage;
senza API key non crea record; endpoint continua a rispondere 200.
"""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models.api_key_orm import ApiKeyORM
from app.db.models.api_usage_orm import ApiUsageORM
from app.main import app
from app.core.dependencies import (
    get_api_key,
    get_current_user,
    get_db,
    rate_limit_dependency,
)


TEST_API_KEY = "test-api-key"


def _yield_test_db() -> Generator[Session, None, None]:
    """Fornisce una sessione sul DB di test."""
    from tests.conftest import TEST_SESSION_FACTORY

    db = TEST_SESSION_FACTORY()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_api_key_in_db(db_session: Session) -> ApiKeyORM:
    """Inserisce la API key di test e restituisce il record."""
    existing = db_session.query(ApiKeyORM).filter(ApiKeyORM.key == TEST_API_KEY).first()
    if existing:
        return existing
    row = ApiKeyORM(key=TEST_API_KEY, name="Test API Key", is_active=True)
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


@pytest.fixture
def clean_usage_table(db_session: Session) -> Generator[None, None, None]:
    """Svuota api_usage prima del test per isolamento."""
    db_session.execute(delete(ApiUsageORM))
    db_session.commit()
    yield


def test_request_with_valid_api_key_creates_usage_record(
    client: TestClient,
    test_api_key_in_db: ApiKeyORM,
    clean_usage_table: None,
) -> None:
    """Una richiesta con API key valida crea un record in api_usage."""
    from tests.conftest import TEST_SESSION_FACTORY

    orig_api_key = app.dependency_overrides.pop(get_api_key, None)
    orig_user = app.dependency_overrides.pop(get_current_user, None)
    orig_rate = app.dependency_overrides.pop(rate_limit_dependency, None)
    orig_get_db = app.dependency_overrides.pop(get_db, None)
    try:
        app.dependency_overrides[get_db] = _yield_test_db
        with patch("app.core.usage_tracker.SessionLocal", TEST_SESSION_FACTORY):
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
        db = TEST_SESSION_FACTORY()
        try:
            count = db.query(ApiUsageORM).count()
            assert count == 1
            row = db.query(ApiUsageORM).first()
            assert row is not None
            assert row.api_key_id == test_api_key_in_db.id
            assert row.endpoint == "/api/v1/items"
            assert row.method == "GET"
            assert row.status_code == 200
        finally:
            db.close()
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


def test_request_without_api_key_does_not_create_usage_record(
    client: TestClient,
    clean_usage_table: None,
) -> None:
    """Una richiesta senza API key (endpoint che non richiede key) non crea record in api_usage."""
    from tests.conftest import TEST_SESSION_FACTORY

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    db = TEST_SESSION_FACTORY()
    try:
        count = db.query(ApiUsageORM).count()
        assert count == 0
    finally:
        db.close()


def test_endpoint_continues_to_respond_200(
    client: TestClient,
    test_api_key_in_db: ApiKeyORM,
) -> None:
    """L'endpoint con API key e auth continua a rispondere 200."""
    orig_api_key = app.dependency_overrides.pop(get_api_key, None)
    orig_get_db = app.dependency_overrides.pop(get_db, None)
    try:
        from tests.conftest import TEST_SESSION_FACTORY

        app.dependency_overrides[get_db] = _yield_test_db
        with patch("app.core.usage_tracker.SessionLocal", TEST_SESSION_FACTORY):
            response = client.get(
                "/api/v1/items",
                headers={"X-API-Key": TEST_API_KEY},
            )
        assert response.status_code == 200
    finally:
        if orig_api_key is not None:
            app.dependency_overrides[get_api_key] = orig_api_key
        if orig_get_db is not None:
            app.dependency_overrides[get_db] = orig_get_db
        else:
            app.dependency_overrides.pop(get_db, None)
