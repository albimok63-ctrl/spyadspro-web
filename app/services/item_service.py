"""
Item service – business logic only. No FastAPI, no HTTP.
Depends only on repository, models and domain exceptions. Solleva ItemNotFoundError se l'item non esiste (API → 404).
"""

from app.core.exceptions import ItemNotFoundError
from app.models.item import ItemModel
from app.repositories.item_repository import ItemRepository


class ItemService:
    """Business logic for Items. No knowledge of FastAPI or HTTP."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def create_item(self, name: str, description: str) -> ItemModel:
        """Create an item. Returns the created item with id."""
        return self._repository.add(name=name, description=description)

    def get_all_items(self) -> list[ItemModel]:
        """Return all items."""
        return self._repository.get_all()

    def get_item_by_id(self, item_id: int) -> ItemModel:
        """Return item by id. Raises ItemNotFoundError if not found (REST: 404)."""
        item = self._repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    def delete_item(self, item_id: int) -> None:
        """Remove item by id. Raises ItemNotFoundError if not found (REST: 404)."""
        if not self._repository.delete_by_id(item_id):
            raise ItemNotFoundError(item_id)
