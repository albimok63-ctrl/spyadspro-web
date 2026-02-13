"""Mapper: risultato TitleSpider → AdSchema normalizzato."""

from app.domain.schemas.ad_schema import AdSchema, now_iso


def map_title_to_ad_schema(data: dict) -> AdSchema:
    """Converte il dict prodotto da TitleSpider in AdSchema."""
    return AdSchema(
        source="generic_web",
        title=data.get("title"),
        description=data.get("meta_description") or data.get("description"),
        landing_url=data.get("url"),
        creative_url=None,
        collected_at=now_iso(),
    )
