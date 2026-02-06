"""
Dependency injection. Wiring only – no business logic.
Flow: api → services → repositories. Sessione DB fornita ai repository.
"""

import jwt
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.cache.redis_client import RedisCacheClient, get_redis_client
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.core.security import set_api_key_on_request, verify_token
from app.db.session import get_db
from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.health_repository import HealthRepository
from app.repositories.item_repository import ItemRepository
from app.services.api_key_service import ApiKeyService
from app.services.health_service import HealthService
from app.services.item_service import ItemService

LOG = get_logger("app")


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


def get_api_key_repository(db: Session = Depends(get_db)) -> ApiKeyRepository:
    """Repository per api_keys."""
    return ApiKeyRepository(db)


def get_api_key_service(
    repository: ApiKeyRepository = Depends(get_api_key_repository),
) -> ApiKeyService:
    """Service per validazione API key."""
    return ApiKeyService(repository=repository)


def get_api_key(
    request: Request,
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    service: ApiKeyService = Depends(get_api_key_service),
) -> str:
    """
    Legge header X-API-Key, valida tramite ApiKeyService. Salva l'oggetto ApiKey in request.state.api_key.
    Solleva 401 se mancante o non valida.
    """
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header")
    key = x_api_key.strip()
    if not service.validate_api_key(key):
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    api_key_object = service.get_api_key_record(key)
    if api_key_object is not None:
        set_api_key_on_request(request, api_key_object)
    return key


def get_current_user(request: Request) -> str:
    """
    Legge Authorization: Bearer <token>, valida JWT con verify_token, restituisce user_id (sub).
    Rifiuta con 401 se header mancante o token invalido. Logga user_id estratto.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    try:
        payload = verify_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user_id = str(user_id)
    LOG.info("Authenticated user_id from token", extra={"user_id": user_id})
    return user_id


def rate_limit_dependency(user_id: str = Depends(get_current_user)) -> str:
    """
    Dipende da get_current_user; applica il rate limit per user_id e restituisce user_id.
    Da usare sugli endpoint protetti insieme o al posto di get_current_user.
    """
    from app.core.rate_limit import check_rate_limit

    check_rate_limit(user_id)
    return user_id
