"""
Health API – routing and response model only. No business logic.
/health = liveness (Kubernetes). Delegates to service via dependency injection.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_health_service
from app.core.metrics import record_health_check
from app.services.health_service import HealthService


class HealthResponse(BaseModel):
    """Response model for health endpoint."""

    status: str
    version: str


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    """Liveness probe: processo up. Kubernetes livenessProbe."""
    result = service.get_health()
    record_health_check("liveness", "success")
    return HealthResponse(status=result.status, version=result.version)
