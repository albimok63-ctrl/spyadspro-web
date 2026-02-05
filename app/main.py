"""
Bootstrap: create app, wire routers and global exception handlers only.
No business logic, no route handlers here.
Error handling: dominio (Service) → handler globale (main) → JSON + status code.

Versioning: tutti gli endpoint sono sotto /api/v1 (URL). Nessun endpoint fuori versione.
Vedi docs/API_VERSIONING.md.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import health as health_v1
from app.api.v1 import items as items_v1
from app.cache.redis_client import get_client as get_redis_client
from app.core.config import Settings
from app.core.dependencies import get_settings
from app.core.exceptions import ConflictError, ItemNotFoundError
from app.core.logging import get_logger
from app.core.metrics import record_health_check
from app.core.middleware import RequestIdAndLoggingMiddleware
from app.db.init_db import init_db

LOG = get_logger("app")

# Schema DB creato prima dell'istanza FastAPI (compatibile pytest, no startup/lifespan).
init_db()

# Prefix ufficiale API: versioning tramite URL. /v1 è stabile. Struttura pronta per /v2.
API_V1_PREFIX = "/api/v1"


def _error_json(message: str) -> dict:
    """Risposta di errore standard REST: sempre JSON con detail."""
    return {"detail": message}


def create_app() -> FastAPI:
    """Build FastAPI app, attach routers and global REST error handlers."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version, debug=settings.debug)
    Instrumentator().instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )
    LOG.info("Prometheus metrics enabled at /metrics")

    @app.exception_handler(ItemNotFoundError)
    def not_found_handler(_request: object, exc: ItemNotFoundError) -> JSONResponse:
        """404 Not Found – risorsa inesistente."""
        return JSONResponse(status_code=404, content=_error_json(str(exc)))

    @app.exception_handler(ConflictError)
    def conflict_handler(_request: object, exc: ConflictError) -> JSONResponse:
        """409 Conflict – es. duplicati."""
        return JSONResponse(status_code=409, content=_error_json(str(exc)))

    @app.exception_handler(ValueError)
    def bad_request_handler(_request: object, exc: ValueError) -> JSONResponse:
        """400 Bad Request – input non valido dal dominio."""
        return JSONResponse(status_code=400, content=_error_json(str(exc)))

    @app.exception_handler(Exception)
    def internal_error_handler(_request: object, exc: Exception) -> JSONResponse:
        """500 Internal Server Error – errore non gestito."""
        LOG.error("Internal server error: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content=_error_json("Internal server error"))

    app.add_middleware(RequestIdAndLoggingMiddleware)

    @app.get("/ready")
    def ready() -> JSONResponse:
        """Readiness probe: verifica Redis. Kubernetes readinessProbe. 503 se Redis non raggiungibile."""
        redis_ok = get_redis_client() is not None
        if redis_ok:
            record_health_check("readiness", "success")
            return JSONResponse(
                status_code=200,
                content={"status": "ready", "redis": "ok"},
            )
        record_health_check("readiness", "failure")
        LOG.warning("Readiness failed: Redis unavailable")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "redis": "unavailable"},
        )

    # Tutti i router sotto API_V1_PREFIX: nessun endpoint fuori versione.
    app.include_router(health_v1.router, prefix=API_V1_PREFIX)
    app.include_router(items_v1.router, prefix=API_V1_PREFIX)
    return app


app = create_app()
