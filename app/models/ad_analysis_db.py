"""
Modello database per ads – schema SQLAlchemy separato dai modelli Pydantic.
"""

from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class AdAnalysisDB(Base):
    """Tabella 'ads': schema persistenza, nessuna logica business."""

    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ad_copy: Mapped[str | None] = mapped_column(String, nullable=True)
    creative_url: Mapped[str | None] = mapped_column(String, nullable=True)
    landing_page_url: Mapped[str | None] = mapped_column(String, nullable=True)
    days_active: Mapped[int] = mapped_column(Integer, nullable=False)
    is_winning_ad: Mapped[bool] = mapped_column(Boolean, nullable=False)
    performance_score: Mapped[float] = mapped_column(Float, nullable=False)
