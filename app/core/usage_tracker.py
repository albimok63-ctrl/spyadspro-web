"""
API usage tracking: middleware che registra ogni richiesta HTTP per analisi, rate limiting avanzato e billing.
Log in console + persistenza su DB quando è presente una API key valida (request.state.api_key).
Non blocca la request in caso di errore salvataggio.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.repositories.api_usage_repository import ApiUsageRepository
from app.services.api_usage_service import ApiUsageService

LOG = get_logger("app")


class UsageTrackerMiddleware(BaseHTTPMiddleware):
    """
    Intercetta ogni request, misura il tempo di esecuzione, logga l'evento e, se request.state.api_key
    è impostata (API key validata), persiste un record in api_usage. Non blocca in caso di errore DB.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        method = request.method
        path = request.url.path
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        LOG.info(
            "api_usage",
            extra={
                "event": "api_usage",
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        api_key_obj = getattr(request.state, "api_key", None)
        api_key_id: int | None = None
        if api_key_obj is not None and hasattr(api_key_obj, "id"):
            try:
                api_key_id = int(api_key_obj.id)
            except (TypeError, ValueError, AttributeError, Exception):
                pass
        if api_key_id is not None:
            db = SessionLocal()
            try:
                usage_service = ApiUsageService(ApiUsageRepository(db))
                usage_service.record_usage(
                    api_key_id=api_key_id,
                    endpoint=path,
                    method=method,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )
            except Exception as e:
                LOG.warning("Api usage persist failed (request unchanged)", extra={"error": str(e)})
            finally:
                db.close()
        return response
