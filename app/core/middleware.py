"""
Middleware FastAPI: request_id (uuid4), durata, log strutturato JSON.
Un solo evento "request_completed" per richiesta: service_name, request_id, method, path, status_code, duration_ms.
X-Request-ID in response; contextvar per log applicativi/errori.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import clear_request_id, get_logger, set_request_id

LOG = get_logger("app")
REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdAndLoggingMiddleware(BaseHTTPMiddleware):
    """
    Genera request_id (uuid4), misura durata, logga un evento request_completed in JSON.
    Nessun log duplicato: un solo evento a fine richiesta con duration_ms.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id
        set_request_id(request_id)
        path = request.url.path
        method = request.method
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            LOG.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_id()
