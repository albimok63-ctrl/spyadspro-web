"""
Ad repository – persistenza ads su DB. Separazione business logic da persistenza.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ad_analysis_db import AdAnalysisDB


class AdRepository:
    """Layer di accesso ai dati per la tabella ads (upsert e query winning)."""

    def save_ad(self, db: Session, ad_data: dict) -> AdAnalysisDB:
        """Upsert: se ad_id esiste → update, altrimenti → insert."""
        existing = db.execute(
            select(AdAnalysisDB).where(AdAnalysisDB.ad_id == ad_data["ad_id"])
        ).scalars().first()

        if existing:
            existing.platform = ad_data["platform"]
            existing.status = ad_data["status"]
            existing.start_date = ad_data["start_date"]
            existing.end_date = ad_data.get("end_date")
            existing.ad_copy = ad_data.get("ad_copy")
            existing.creative_url = ad_data.get("creative_url")
            existing.landing_page_url = ad_data.get("landing_page_url")
            existing.days_active = ad_data["days_active"]
            existing.is_winning_ad = ad_data["is_winning_ad"]
            existing.performance_score = ad_data["performance_score"]
            db.commit()
            db.refresh(existing)
            return existing

        row = AdAnalysisDB(
            ad_id=ad_data["ad_id"],
            platform=ad_data["platform"],
            status=ad_data["status"],
            start_date=ad_data["start_date"],
            end_date=ad_data.get("end_date"),
            ad_copy=ad_data.get("ad_copy"),
            creative_url=ad_data.get("creative_url"),
            landing_page_url=ad_data.get("landing_page_url"),
            days_active=ad_data["days_active"],
            is_winning_ad=ad_data["is_winning_ad"],
            performance_score=ad_data["performance_score"],
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    def get_winning_ads(self, db: Session) -> list[AdAnalysisDB]:
        """Ritorna tutti gli ads con is_winning_ad = True."""
        result = db.execute(select(AdAnalysisDB).where(AdAnalysisDB.is_winning_ad.is_(True)))
        return list(result.scalars().all())
