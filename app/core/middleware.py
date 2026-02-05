"""
Middleware FastAPI: request_id e log strutturato JSON per ogni request/response.
Propagazione X-Request-ID: se il client invia l'header, viene riutilizzato (correlazione distribuita).
Contesto: request_id in contextvar per log applicativi e errori (debugging distribuito, tracing).
"""

from __future__ import annotations

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
    Genera o riutilizza request_id (header X-Request-ID), espone in response, logga request/response.
    Imposta request_id nel contextvar per tutta la richiesta (log applicativi e errori correlati).
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id
        set_request_id(request_id)
        path = request.url.path
        method = request.method
        try:
            LOG.info(
                "request_start",
                extra={"request_id": request_id, "path": path, "method": method},
            )
            response = await call_next(request)
            status_code = response.status_code
            LOG.info(
                "request_end",
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "status_code": status_code,
                },
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_id()
