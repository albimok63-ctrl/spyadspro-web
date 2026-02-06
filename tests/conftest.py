"""
Pytest fixtures. TestClient senza server reale.
DB test: UNA SOLA Base, tabelle create a import time (prima di qualsiasi test).
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.pool import StaticPool
from starlette.requests import Request
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import api_key_orm  # noqa: F401 – registra ApiKeyORM su Base
from app.db.models import api_usage_orm  # noqa: F401 – registra ApiUsageORM su Base
from app.db.models import item_orm  # noqa: F401 – registra tutti i modelli su Base prima di create_all
from app.db.models.item_orm import ItemORM

# Inizializzazione DB di test a import time, PRIMA di importare app (tabelle pronte per override).
# SQLite in-memory condiviso tra tutte le sessioni di test (StaticPool).
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# Creare lo schema (items, api_keys, api_usage) prima di qualsiasi sessione.
Base.metadata.create_all(bind=TEST_ENGINE)
# Session factory solo dopo create_all, così le tabelle esistono già.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
TEST_SESSION_FACTORY = TestingSessionLocal

from app.main import app
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService
from app.db.session import get_db

# Sessione DB di test per le richieste: indipendente dalla sessione del middleware.
def override_get_db() -> Generator[Session, None, None]:
    """Fornisce una sessione dal DB di test; chiusa solo nel finally (lifecycle pytest/request)."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override get_db così i test usano solo la sessione dedicata (stesso engine del middleware).
app.dependency_overrides[get_db] = override_get_db

# Il middleware usage_tracker usa SessionLocal: in test deve usare lo stesso engine di test.
import app.core.usage_tracker as _usage_tracker_module
_usage_tracker_module.SessionLocal = TestingSessionLocal

# Override a import time: l'app usa il DB di test (TEST_ENGINE) per gli endpoint items.
def _yield_item_service():
    db = TEST_SESSION_FACTORY()
    try:
        yield ItemService(repository=ItemRepository(db))
    finally:
        db.close()
from app.core.dependencies import (
    get_api_key,
    get_current_user,
    get_item_service,
    rate_limit_dependency,
)

app.dependency_overrides[get_item_service] = _yield_item_service


def _mock_get_api_key() -> str:
    """Bypass API key negli test esistenti."""
    return "test-api-key"


app.dependency_overrides[get_api_key] = _mock_get_api_key
# JWT: bypass auth negli test esistenti (items richiedono token; override restituisce user fittizio).
def _mock_get_current_user(request: Request) -> str:
    return "test_user"

app.dependency_overrides[get_current_user] = _mock_get_current_user


def _mock_rate_limit() -> str:
    """Bypass rate limit negli test: nessun Redis richiesto."""
    return "test_user"


app.dependency_overrides[rate_limit_dependency] = _mock_rate_limit


@pytest.fixture(scope="session")
def test_engine() -> Generator:
    """Engine SQLite di test (sqlite:///:memory:). Tabelle create all'avvio, drop alla fine della sessione."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield TEST_ENGINE
    Base.metadata.drop_all(bind=TEST_ENGINE)


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


@pytest.fixture
def seeded_items(db_session: Session) -> ItemORM:
    """Inserisce un item di test nel DB; ogni test che lo usa ha dati isolati."""
    item = ItemORM(name="test item", description="")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture(autouse=True)
def _override_db() -> Generator[None, None, None]:
    """Esegue Base.metadata.create_all(bind=TEST_ENGINE) prima di ogni test; tabelle pronte prima del TestClient."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield


@pytest.fixture(autouse=True)
def _clean_items(_override_db: None, test_session_factory) -> Generator[None, None, None]:
    """Isolamento: svuota la tabella items prima di ogni test (dipende da _override_db)."""
    db = test_session_factory()
    try:
        db.execute(delete(ItemORM))
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def client(_override_db: None) -> TestClient:
    """HTTP client per test API. Tabelle create da _override_db prima della creazione del client."""
    return TestClient(app)
