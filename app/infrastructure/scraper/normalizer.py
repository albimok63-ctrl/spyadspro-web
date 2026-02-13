"""Normalizzazione standard dei dati restituiti dagli spider. Schema comune per multi-fonte."""

from datetime import datetime


class ScraperNormalizer:
    """Normalizza l'output degli spider in struttura standard per Meta Ads, TikTok Ads, landing, ecc."""

    def normalize(self, data: dict, source: str) -> dict | None:
        """Restituisce un dict con source, title, description, url, fetched_at. Se data è None restituisce None."""
        if data is None:
            return None
        return {
            "source": source,
            "title": data.get("title"),
            "description": data.get("description"),
            "url": data.get("url"),
            "fetched_at": datetime.utcnow().isoformat(),
        }
