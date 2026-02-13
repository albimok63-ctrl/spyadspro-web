"""Schema dati normalizzato per annunci SpyAdsPro, indipendente dalla fonte (meta/tiktok/google)."""

from dataclasses import dataclass
from datetime import datetime, timezone


def now_iso() -> str:
    """Restituisce datetime UTC in formato ISO8601 timezone-aware."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AdSchema:
    """Schema base minimo per un annuncio, normalizzato tra fonti."""

    source: str
    title: str | None
    description: str | None
    landing_url: str | None
    creative_url: str | None
    collected_at: str  # ISO8601

    def to_dict(self) -> dict:
        """Restituisce un dict serializzabile (es. per JSON)."""
        return {
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "landing_url": self.landing_url,
            "creative_url": self.creative_url,
            "collected_at": self.collected_at,
        }
