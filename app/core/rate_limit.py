"""
Rate limiting per endpoint API protetti. Basato su user_id dal JWT, counter Redis.
Finestra fissa 60s, limite configurabile (default 60 req/min). Health e metrics non limitati.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.cache.redis_client import get_client
from app.core.logging import get_logger

LOG = get_logger("app")

REDIS_KEY_PREFIX = "rate_limit:"


def check_rate_limit(user_id: str) -> None:
    """
    Incrementa il counter Redis per user_id, imposta TTL alla prima richiesta nella finestra.
    Se il numero di richieste supera il limite, logga e solleva HTTP 429.
    Se Redis non è disponibile, fail-open (nessun blocco).
    """
    from app.core.config import get_settings

    client = get_client()
    if client is None:
        return
    settings = get_settings()
    key = f"{REDIS_KEY_PREFIX}{user_id}"
    window = settings.rate_limit_window_seconds
    max_requests = settings.rate_limit_max_requests
    try:
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        results = pipe.execute()
        count = results[0]
        ttl = results[1]
        if ttl == -1:
            client.expire(key, window)
        if count > max_requests:
            LOG.warning(
                "Rate limit exceeded",
                extra={"user_id": user_id, "count": count, "limit": max_requests},
            )
            raise HTTPException(
                status_code=429,
                detail="Too many requests; try again later.",
            )
    except HTTPException:
        raise
    except Exception as e:
        LOG.warning("Rate limit check failed, allowing request", extra={"error": str(e)})
