"""
Test cache-aside sul repository Items. Mock Redis client, nessun Redis reale.
Verifica: cache hit, cache miss, fallback su DB.
"""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models.item_orm import ItemORM
from app.models.item import ItemModel
from app.repositories.item_repository import ItemRepository


class MockRedisCache:
    """Mock Redis: get/set/delete/is_available per test cache-aside."""

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self._store: dict[str, str] = {}
        self.get_calls: list[str] = []
        self.set_calls: list[tuple[str, str]] = []
        self.delete_calls: list[str] = []

    @property
    def is_available(self) -> bool:
        return self._available

    def get(self, key: str) -> str | None:
        self.get_calls.append(key)
        return self._store.get(key)

    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        self.set_calls.append((key, value))
        self._store[key] = value

    def delete(self, key: str) -> None:
        self.delete_calls.append(key)
        self._store.pop(key, None)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Sessione SQLite in-memory dedicata ai test cache."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_cache() -> MockRedisCache:
    """Mock cache client (Redis non richiesto)."""
    return MockRedisCache(available=True)


def test_get_by_id_cache_miss_then_hit(db_session: Session, mock_cache: MockRedisCache) -> None:
    """Cache miss: lettura da DB e salvataggio in cache; successiva lettura è cache hit."""
    repo = ItemRepository(db_session, cache_client=mock_cache)
    created = repo.add(name="Cached", description="Item")
    assert created.id >= 1

    mock_cache.get_calls.clear()
    mock_cache.set_calls.clear()

    first = repo.get_by_id(created.id)
    assert first is not None
    assert first.name == "Cached"
    assert mock_cache.get_calls == [f"item:{created.id}"]
    assert len(mock_cache.set_calls) == 1
    assert mock_cache.set_calls[0][0] == f"item:{created.id}"
    assert "Cached" in mock_cache.set_calls[0][1]

    mock_cache.get_calls.clear()
    mock_cache.set_calls.clear()

    second = repo.get_by_id(created.id)
    assert second is not None
    assert second.id == first.id
    assert mock_cache.get_calls == [f"item:{created.id}"]
    assert len(mock_cache.set_calls) == 0


def test_get_by_id_cache_hit_returns_from_cache(db_session: Session, mock_cache: MockRedisCache) -> None:
    """Cache hit: restituisce valore da cache senza leggere dal DB."""
    repo = ItemRepository(db_session, cache_client=mock_cache)
    cached_item = ItemModel(id=42, name="FromCache", description="Only")
    key = "item:42"
    mock_cache._store[key] = cached_item.model_dump_json()

    result = repo.get_by_id(42)
    assert result is not None
    assert result.id == 42
    assert result.name == "FromCache"
    assert result.description == "Only"
    assert mock_cache.get_calls == [key]


def test_get_by_id_fallback_when_cache_unavailable(db_session: Session) -> None:
    """Cache non disponibile: fallback su DB, nessun errore."""
    mock_cache = MockRedisCache(available=False)
    repo = ItemRepository(db_session, cache_client=mock_cache)
    created = repo.add(name="FromDB", description="Only")
    found = repo.get_by_id(created.id)
    assert found is not None
    assert found.name == "FromDB"
    assert len(mock_cache.get_calls) == 0


def test_get_by_id_fallback_when_cache_is_none(db_session: Session) -> None:
    """Repository senza cache: sempre lettura da DB."""
    repo = ItemRepository(db_session, cache_client=None)
    created = repo.add(name="NoCache", description="Item")
    found = repo.get_by_id(created.id)
    assert found is not None
    assert found.name == "NoCache"


def test_delete_by_id_invalidates_cache(db_session: Session, mock_cache: MockRedisCache) -> None:
    """delete_by_id invalida la voce in cache."""
    repo = ItemRepository(db_session, cache_client=mock_cache)
    created = repo.add(name="ToDelete", description="")
    repo.get_by_id(created.id)
    assert f"item:{created.id}" in mock_cache._store

    repo.delete_by_id(created.id)
    assert f"item:{created.id}" in mock_cache.delete_calls
    assert mock_cache._store.get(f"item:{created.id}") is None


# --- Scenari richiesti: cache miss → DB, cache hit → DB non chiamato, Redis assente → fallback DB ---


def test_cache_miss_uses_db(db_session: Session, mock_cache: MockRedisCache) -> None:
    """Cache miss: lettura da DB (nessun valore in cache, si legge DB e si salva in cache)."""
    repo = ItemRepository(db_session, cache_client=mock_cache)
    created = repo.add(name="OnlyInDb", description="x")
    assert mock_cache.get_calls == []
    assert mock_cache.set_calls == []

    result = repo.get_by_id(created.id)
    assert result is not None
    assert result.name == "OnlyInDb"
    assert mock_cache.get_calls == [f"item:{created.id}"]
    assert len(mock_cache.set_calls) == 1
    assert mock_cache.set_calls[0][0] == f"item:{created.id}"


def test_cache_hit_db_not_called(db_session: Session, mock_cache: MockRedisCache) -> None:
    """Cache hit: risposta da cache, DB non viene usato per quella lettura."""
    repo = ItemRepository(db_session, cache_client=mock_cache)
    cached = ItemModel(id=99, name="FromCache", description="y")
    mock_cache._store["item:99"] = cached.model_dump_json()

    result = repo.get_by_id(99)
    assert result is not None
    assert result.id == 99
    assert result.name == "FromCache"
    assert mock_cache.get_calls == ["item:99"]
    assert len(mock_cache.set_calls) == 0


def test_redis_unavailable_fallback_to_db(db_session: Session) -> None:
    """Redis non disponibile: fallback su DB, nessun errore."""
    mock_cache = MockRedisCache(available=False)
    repo = ItemRepository(db_session, cache_client=mock_cache)
    created = repo.add(name="FromDB", description="fallback")
    found = repo.get_by_id(created.id)
    assert found is not None
    assert found.name == "FromDB"
    assert len(mock_cache.get_calls) == 0
