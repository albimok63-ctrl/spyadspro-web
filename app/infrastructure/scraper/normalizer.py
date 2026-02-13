"""Normalizzatore di output spider: garantisce chiavi standard (title, description, source_url)."""

STANDARD_KEYS = ("title", "description", "source_url")


class ScraperOutputNormalizer:
    """Normalizza un dict di output spider con chiavi title, description, source_url."""

    def normalize(self, data: dict) -> dict:
        """Restituisce un dict con title, description, source_url; valori mancanti impostati a None."""
        out = dict(data)
        for key in STANDARD_KEYS:
            if key not in out:
                out[key] = None
        return out
