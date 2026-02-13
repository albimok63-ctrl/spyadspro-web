"""
Ad Analysis model – Pydantic schemas for Marketing Intelligence.
Stable data model for future business logic and ad intelligence.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class PlatformEnum(str, Enum):
    META = "meta"
    TIKTOK = "tiktok"
    GOOGLE = "google"


class AdStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AdAnalysisBase(BaseModel):
    """Base model for ad analysis – identification, lifecycle, intelligence and metrics."""

    # Identificazione
    ad_id: str
    platform: PlatformEnum
    status: AdStatusEnum

    # Lifecycle
    start_date: date
    end_date: Optional[date] = None

    # Intelligence fields
    ad_copy: Optional[str] = None
    creative_url: Optional[HttpUrl] = None
    landing_page_url: Optional[HttpUrl] = None

    # Raw metrics (necessarie per business logic futura)
    impressions: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None

    # Calculated fields
    days_active: int = 0
    is_winning_ad: bool = False


class AdAnalysisCreate(AdAnalysisBase):
    """Request/input model for creating an ad analysis."""

    pass


class AdAnalysisRead(AdAnalysisBase):
    """Response/read model for ad analysis with performance score."""

    performance_score: float
