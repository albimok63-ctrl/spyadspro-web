"""
Health repository – data access only. No HTTP, no FastAPI.
Returns plain data structures (e.g. dict or dataclass).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthRecord:
    """Raw data from persistence layer (mock or DB)."""

    status: str
    version: str


class HealthRepository:
    """Data access for health checks. Mock implementation."""

    def get_status(self) -> HealthRecord:
        """Fetch health status from storage. No HTTP semantics."""
        return HealthRecord(status="ok", version="1.0.0")
