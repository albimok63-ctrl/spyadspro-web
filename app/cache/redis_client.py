"""
Client Redis minimale e opzionale. Connessione via env (REDIS_HOST, REDIS_PORT), timeout breve.
get_client() restituisce il client se raggiungibile, None altrimenti. Nessuna dipendenza FastAPI.
"""

from __future__ import annotations

import os

# redis-py optional: import only when used
try:
    import redis
except ImportError:
    redis = None  # type: ignore[assignment]


DEFAULT_SOCKET_TIMEOUT = 2.0
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 6379


def get_client():
    """
    Restituisce un client Redis se disponibile e raggiungibile, altrimenti None.
    Configurazione via env: REDIS_HOST, REDIS_PORT. Timeout breve.
    """
    if redis is None:
        return None
    host = os.getenv("REDIS_HOST", DEFAULT_HOST)
    port = int(os.getenv("REDIS_PORT", str(DEFAULT_PORT)))
    try:
        client = redis.Redis(
            host=host,
            port=port,
            socket_timeout=DEFAULT_SOCKET_TIMEOUT,
            decode_responses=True,
        )
        client.ping()
        return client
    except Exception:
        return None


DEFAULT_TTL_SECONDS = 300


class RedisCacheClient:
    """
    Wrapper Redis per cache. Gestione errori: Redis non obbligatorio, fallback silenzioso.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        socket_timeout: float = DEFAULT_SOCKET_TIMEOUT,
        enabled: bool = True,
    ) -> None:
        self._enabled = enabled and redis is not None
        self._client: redis.Redis | None = None
        if self._enabled:
            try:
                self._client = redis.Redis(
                    host=host,
                    port=port,
                    socket_timeout=socket_timeout,
                    decode_responses=True,
                )
                self._client.ping()
            except Exception:
                self._client = None
                self._enabled = False

    def get(self, key: str) -> str | None:
        """Restituisce il valore in cache o None (miss/errore)."""
        if not self._enabled or not self._client:
            return None
        try:
            return self._client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        """Salva in cache con TTL. Ignora errori."""
        if not self._enabled or not self._client:
            return
        try:
            self._client.set(key, value, ex=ttl_seconds)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """Rimuove chiave dalla cache. Ignora errori."""
        if not self._enabled or not self._client:
            return
        try:
            self._client.delete(key)
        except Exception:
            pass

    @property
    def is_available(self) -> bool:
        """True se Redis è utilizzabile."""
        return self._enabled and self._client is not None


def get_redis_client(
    host: str,
    port: int,
    enabled: bool = False,
    socket_timeout: float = DEFAULT_SOCKET_TIMEOUT,
) -> RedisCacheClient:
    """Factory: restituisce client Redis (degradabile se connessione fallisce)."""
    return RedisCacheClient(
        host=host,
        port=port,
        socket_timeout=socket_timeout,
        enabled=enabled,
    )
