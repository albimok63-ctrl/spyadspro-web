"""
ApiUsage repository – persistenza record di utilizzo API su DB.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.api_usage_orm import ApiUsageORM


class ApiUsageRepository:
    """Inserimento record api_usage."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_usage(
        self,
        api_key_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
    ) -> ApiUsageORM:
        """Crea un record di utilizzo e lo persiste."""
        row = ApiUsageORM(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row
