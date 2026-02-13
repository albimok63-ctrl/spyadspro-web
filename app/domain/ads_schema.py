"""Schema dati comune per tutti gli spider SpyAdsPro. Unificazione multi-fonte."""

from dataclasses import dataclass


@dataclass
class AdData:
    """Schema unico per unificare dati da fonti diverse (Meta, TikTok, Google, ecc.)."""

    source: str
    creative_text: str | None
    hook: str | None
    landing_url: str | None
    collected_at: str
    raw_data: dict

    def to_dict(self) -> dict:
        """Restituisce i dati come dizionario."""
        return {
            "source": self.source,
            "creative_text": self.creative_text,
            "hook": self.hook,
            "landing_url": self.landing_url,
            "collected_at": self.collected_at,
            "raw_data": self.raw_data,
        }
