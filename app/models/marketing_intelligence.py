"""
Marketing Intelligence – schema Pydantic per analisi annunci con campi calcolati.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, computed_field, field_validator


class PlatformEnum(str, Enum):
    META = "meta"
    TIKTOK = "tiktok"
    GOOGLE = "google"


class AdIntelligence(BaseModel):
    """Schema per intelligence su singola inserzione con property calcolate (benchmark 2026)."""

    ad_id: str
    platform: PlatformEnum
    start_date: date
    copy_text: Optional[str] = None
    creative_url: Optional[str] = None

    @field_validator("start_date")
    @classmethod
    def start_date_not_future(cls, v: date) -> date:
        """Assicura che start_date non sia nel futuro."""
        if v > date.today():
            raise ValueError("start_date non può essere nel futuro")
        return v

    @computed_field
    @property
    def days_active(self) -> int:
        """Giorni trascorsi tra start_date e la data odierna (≥ 0)."""
        delta = date.today() - self.start_date
        return max(0, delta.days)

    @computed_field
    @property
    def is_winning_ad(self) -> bool:
        """True se days_active > 14 (indicatore ROI positivo, benchmark 2026)."""
        return self.days_active > 14

    @computed_field
    @property
    def confidence_score(self) -> float:
        """Float da 0 a 1 che aumenta proporzionalmente alla durata dell'annuncio."""
        days = self.days_active
        if days <= 0:
            return 0.0
        return min(1.0, days / 30.0)
