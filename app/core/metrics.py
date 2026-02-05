"""
Metriche Prometheus: traffico, latenza, errori.
Label: method, path, status_code (obbligatorie).
Middleware automatico: registra ogni richiesta (eccetto /metrics).
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Counter: numero totale di richieste HTTP.
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

# Histogram: durata richiesta in secondi (latenza).
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Counter: esiti health check (liveness / readiness) per probe Kubernetes.
HEALTH_CHECKS_TOTAL = Counter(
    "health_checks_total",
    "Health check results (liveness, readiness)",
    ["type", "status"],
)

METRICS_PATH = "/metrics"


def record_health_check(check_type: str, status: str) -> None:
    """Registra l'esito di un health check (type=liveness|readiness, status=success|failure)."""
    HEALTH_CHECKS_TOTAL.labels(type=check_type, status=status).inc()


def record_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    """Registra una richiesta HTTP per metriche Prometheus."""
    status = str(status_code)
    HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=status).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=method, path=path, status_code=status
    ).observe(duration_seconds)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware che registra per ogni richiesta (eccetto /metrics):
    - http_requests_total (counter)
    - http_request_duration_seconds (histogram)
    Label: method, path, status_code.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path == METRICS_PATH:
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_seconds=duration,
        )
        return response
