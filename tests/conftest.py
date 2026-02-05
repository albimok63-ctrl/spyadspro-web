"""
Pytest fixtures. TestClient senza server reale.
DB test: UNA SOLA Base, tabelle create a import time (prima di qualsiasi test).
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import item_orm  # noqa: F401 – registra tutti i modelli su Base prima di create_all
from app.db.models.item_orm import ItemORM

# Inizializzazione DB di test a import time, PRIMA di importare app (tabelle pronte per override).
# SQLite :memory: senza cache=shared crea un DB diverso per connessione; con file:...&cache=shared
# tutte le connessioni condividono lo stesso DB in-memory.
TEST_ENGINE = create_engine(
    "sqlite:///file:testdb?mode=memory&cache=shared&uri=true",
    connect_args={"check_same_thread": False},
)
Base.metadata.create_all(bind=TEST_ENGINE)
TEST_SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

from app.main import app
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService

# Override a import time: l'app usa il DB di test (TEST_ENGINE) per gli endpoint items.
def _yield_item_service():
    db = TEST_SESSION_FACTORY()
    try:
        yield ItemService(repository=ItemRepository(db))
    finally:
        db.close()
from app.core.dependencies import get_item_service
app.dependency_overrides[get_item_service] = _yield_item_service


@pytest.fixture(scope="session")
def test_engine():
    """Engine di test (tabelle già create a import time). Base unica condivisa."""
    return TEST_ENGINE


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Sessionmaker sul DB di test (tabelle già create a import time)."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session(test_session_factory) -> Generator[Session, None, None]:
    """Sessione DB di test per repository/service tests (una per test)."""
    db = test_session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _override_db() -> Generator[None, None, None]:
    """Assicura tabelle su TEST_ENGINE prima di ogni test (override già impostati a import time)."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield


@pytest.fixture(autouse=True)
def _clean_items(test_session_factory) -> Generator[None, None, None]:
    """Isolamento: svuota la tabella items prima di ogni test."""
    db = test_session_factory()
    try:
        db.execute(delete(ItemORM))
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def client() -> TestClient:
    """HTTP client per test API. Non avvia server."""
    return TestClient(app)
