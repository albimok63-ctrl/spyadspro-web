"""
Dependency injection. Wiring only – no business logic.
Flow: api → services → repositories. Sessione DB fornita ai repository.
"""

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.cache.redis_client import RedisCacheClient, get_redis_client
from app.core.config import Settings
from app.db.session import get_db
from app.repositories.health_repository import HealthRepository
from app.repositories.item_repository import ItemRepository
from app.services.health_service import HealthService
from app.services.item_service import ItemService


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


def get_health_repository() -> HealthRepository:
    """Factory for health repository (data access layer)."""
    return HealthRepository()


def get_health_service() -> HealthService:
    """Factory for health service (business layer). Depends on repository."""
    return HealthService(repository=get_health_repository())


def get_redis_cache() -> RedisCacheClient:
    """Client Redis per cache-aside (opzionale, degradabile)."""
    settings = get_settings()
    return get_redis_client(
        host=settings.redis_host,
        port=settings.redis_port,
        enabled=settings.cache_enabled,
    )


def get_item_repository(
    db: Session = Depends(get_db),
    cache_client: RedisCacheClient = Depends(get_redis_cache),
) -> ItemRepository:
    """Repository Items con sessione DB e cache opzionale."""
    return ItemRepository(db, cache_client=cache_client)


def get_item_service(repository: ItemRepository = Depends(get_item_repository)) -> ItemService:
    """Factory per item service. Dipende da repository (a sua volta da get_db)."""
    return ItemService(repository=repository)
