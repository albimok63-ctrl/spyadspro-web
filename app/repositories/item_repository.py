"""
Item repository – persistenza su DB (SQLAlchemy) con cache-aside opzionale.
Unico layer che conosce DB e cache. Nessuna logica HTTP, nessuna dipendenza FastAPI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.db.models.item_orm import ItemORM
from app.models.item import ItemCreate, ItemModel

if TYPE_CHECKING:
    from app.cache.redis_client import RedisCacheClient

CACHE_KEY_PREFIX = "item:"
CACHE_TTL_SECONDS = 300


class ItemRepository:
    """Persistenza Items su database con cache-aside (Redis opzionale, degradabile)."""

    def __init__(self, db: Session, cache_client: RedisCacheClient | None = None) -> None:
        self._db = db
        self._cache = cache_client

    def _cache_key(self, item_id: int) -> str:
        return f"{CACHE_KEY_PREFIX}{item_id}"

    def _get_from_cache(self, item_id: int) -> ItemModel | None:
        if not self._cache or not self._cache.is_available:
            return None
        raw = self._cache.get(self._cache_key(item_id))
        if raw is None:
            return None
        try:
            return ItemModel.model_validate_json(raw)
        except Exception:
            return None

    def _set_cache(self, item: ItemModel) -> None:
        if not self._cache or not self._cache.is_available:
            return
        try:
            self._cache.set(self._cache_key(item.id), item.model_dump_json(), ttl_seconds=CACHE_TTL_SECONDS)
        except Exception:
            pass

    def _invalidate_item(self, item_id: int) -> None:
        if self._cache and self._cache.is_available:
            try:
                self._cache.delete(self._cache_key(item_id))
            except Exception:
                pass

    def add(self, name: str, description: str) -> ItemModel:
        """Persiste un nuovo item; assegna id. Restituisce l'item come ItemModel."""
        orm = ItemORM(name=name, description=description)
        self._db.add(orm)
        self._db.commit()
        self._db.refresh(orm)
        return ItemModel(id=orm.id, name=orm.name, description=orm.description)

    def create_item(self, item: ItemCreate) -> ItemModel:
        """Persiste un nuovo item da ItemCreate. Scrive su DB e invalida cache per l'id creato."""
        created = self.add(name=item.name, description=item.description)
        self._invalidate_item(created.id)
        return created

    def get_all(self) -> list[ItemModel]:
        """Restituisce tutti gli item (no cache per lista)."""
        rows = self._db.query(ItemORM).order_by(ItemORM.id).all()
        return [ItemModel(id=r.id, name=r.name, description=r.description) for r in rows]

    def get_all_items(self) -> list[ItemModel]:
        """Restituisce tutti gli item (alias per get_all)."""
        return self.get_all()

    def get_by_id(self, item_id: int) -> ItemModel | None:
        """Restituisce item per id o None se non trovato. Cache-aside: hit → return, miss → DB + set cache."""
        cached = self._get_from_cache(item_id)
        if cached is not None:
            return cached
        orm = self._db.get(ItemORM, item_id)
        if orm is None:
            return None
        model = ItemModel(id=orm.id, name=orm.name, description=orm.description)
        self._set_cache(model)
        return model

    def get_item_by_id(self, item_id: int) -> ItemModel:
        """Restituisce item per id. Solleva ValueError se l'item non esiste."""
        result = self.get_by_id(item_id)
        if result is None:
            raise ValueError("Item not found")
        return result

    def delete_by_id(self, item_id: int) -> bool:
        """Rimuove item per id. True se rimosso, False se non trovato. Invalida cache."""
        orm = self._db.get(ItemORM, item_id)
        if orm is None:
            return False
        self._db.delete(orm)
        self._db.commit()
        self._invalidate_item(item_id)
        return True
