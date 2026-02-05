"""
Test ItemService – logica con repository reale su DB di test (stesso engine/sessione di conftest).
"""

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import ItemNotFoundError
from app.models.item import ItemModel
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService


@pytest.fixture
def repository(db_session: Session) -> ItemRepository:
    """Repository con sessione DB di test (tabelle create a import time in conftest)."""
    return ItemRepository(db_session)


@pytest.fixture
def service(repository: ItemRepository) -> ItemService:
    """ItemService con repository di test."""
    return ItemService(repository=repository)


def test_create_item_returns_item_with_id(service: ItemService) -> None:
    """create_item ritorna ItemModel con id assegnato."""
    item = service.create_item(name="Alpha", description="First")
    assert isinstance(item, ItemModel)
    assert item.id >= 1
    assert item.name == "Alpha"
    assert item.description == "First"


def test_get_all_items_returns_created_items(service: ItemService) -> None:
    """get_all_items ritorna tutti gli item creati."""
    service.create_item(name="A", description="")
    service.create_item(name="B", description="b")
    items = service.get_all_items()
    assert len(items) == 2
    names = {i.name for i in items}
    assert names == {"A", "B"}


def test_get_item_by_id_returns_item_when_exists(service: ItemService) -> None:
    """get_item_by_id ritorna l'item quando esiste."""
    created = service.create_item(name="X", description="y")
    found = service.get_item_by_id(created.id)
    assert found.id == created.id
    assert found.name == "X"
    assert found.description == "y"


def test_get_item_by_id_raises_item_not_found_when_not_found(service: ItemService) -> None:
    """get_item_by_id solleva ItemNotFoundError quando l'item non esiste (API → 404)."""
    with pytest.raises(ItemNotFoundError) as exc_info:
        service.get_item_by_id(99999)
    assert exc_info.value.item_id == 99999
    assert "not found" in str(exc_info.value).lower()


def test_delete_item_removes_when_exists(service: ItemService) -> None:
    """delete_item rimuove l'item quando esiste; get_item_by_id solleva ItemNotFoundError dopo."""
    created = service.create_item(name="ToRemove", description="")
    service.delete_item(created.id)
    with pytest.raises(ItemNotFoundError):
        service.get_item_by_id(created.id)


def test_delete_item_raises_item_not_found_when_not_found(service: ItemService) -> None:
    """delete_item solleva ItemNotFoundError quando l'item non esiste (API → 404)."""
    with pytest.raises(ItemNotFoundError) as exc_info:
        service.delete_item(99999)
    assert exc_info.value.item_id == 99999
