"""
Test ItemRepository su DB SQLite temporaneo (in-memory). Isolati: engine e sessione dedicati, nessun TestClient/FastAPI.
"""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models.item_orm import ItemORM
from app.models.item import ItemCreate, ItemModel
from app.repositories.item_repository import ItemRepository


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Sessione su SQLite in-memory dedicata ai test. Schema creato su engine temporaneo."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repository(db_session: Session) -> ItemRepository:
    """ItemRepository con sessione di test (DB temporaneo)."""
    return ItemRepository(db_session)


def test_add_returns_item_with_id(repository: ItemRepository) -> None:
    """add persiste l'item e restituisce ItemModel con id."""
    item = repository.add(name="Alpha", description="First")
    assert isinstance(item, ItemModel)
    assert item.id >= 1
    assert item.name == "Alpha"
    assert item.description == "First"


def test_get_all_returns_added_items(repository: ItemRepository) -> None:
    """get_all restituisce tutti gli item aggiunti."""
    repository.add(name="A", description="")
    repository.add(name="B", description="b")
    items = repository.get_all()
    assert len(items) == 2
    names = {i.name for i in items}
    assert names == {"A", "B"}


def test_get_by_id_returns_item_when_exists(repository: ItemRepository) -> None:
    """get_by_id restituisce l'item quando esiste."""
    created = repository.add(name="X", description="y")
    found = repository.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == "X"


def test_get_by_id_returns_none_when_not_found(repository: ItemRepository) -> None:
    """get_by_id restituisce None quando l'item non esiste."""
    found = repository.get_by_id(99999)
    assert found is None


def test_delete_by_id_returns_true_when_exists(repository: ItemRepository) -> None:
    """delete_by_id restituisce True e rimuove l'item."""
    created = repository.add(name="ToRemove", description="")
    ok = repository.delete_by_id(created.id)
    assert ok is True
    assert repository.get_by_id(created.id) is None


def test_delete_by_id_returns_false_when_not_found(repository: ItemRepository) -> None:
    """delete_by_id restituisce False quando l'item non esiste."""
    ok = repository.delete_by_id(99999)
    assert ok is False


# --- Test interfaccia create_item / get_all_items / get_item_by_id (ValueError) ---


def test_create_item_persists_and_returns_with_id(repository: ItemRepository) -> None:
    """create_item persiste l'item e restituisce ItemModel con id."""
    item = ItemCreate(name="Alpha", description="First")
    created = repository.create_item(item)
    assert isinstance(created, ItemModel)
    assert created.id >= 1
    assert created.name == "Alpha"
    assert created.description == "First"


def test_get_all_items_returns_list(repository: ItemRepository) -> None:
    """get_all_items restituisce la lista degli item creati."""
    repository.create_item(ItemCreate(name="A", description=""))
    repository.create_item(ItemCreate(name="B", description="b"))
    items = repository.get_all_items()
    assert len(items) == 2
    assert {i.name for i in items} == {"A", "B"}


def test_get_item_by_id_returns_item_when_exists(repository: ItemRepository) -> None:
    """get_item_by_id restituisce l'item quando esiste."""
    created = repository.create_item(ItemCreate(name="X", description="y"))
    found = repository.get_item_by_id(created.id)
    assert found.id == created.id
    assert found.name == "X"
    assert found.description == "y"


def test_get_item_by_id_raises_value_error_when_not_found(repository: ItemRepository) -> None:
    """get_item_by_id solleva ValueError se l'item non esiste."""
    with pytest.raises(ValueError) as exc_info:
        repository.get_item_by_id(99999)
    assert "not found" in str(exc_info.value).lower()
