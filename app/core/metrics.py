"""
Metriche Prometheus custom: health check (liveness/readiness).
Metriche HTTP (request count, duration) gestite da prometheus-fastapi-instrumentator su /metrics.
"""

from __future__ import annotations

from prometheus_client import Counter

HEALTH_CHECKS_TOTAL = Counter(
    "health_checks_total",
    "Health check results (liveness, readiness)",
    ["type", "status"],
)


def record_health_check(check_type: str, status: str) -> None:
    """Registra l'esito di un health check (type=liveness|readiness, status=success|failure)."""
    HEALTH_CHECKS_TOTAL.labels(type=check_type, status=status).inc()
