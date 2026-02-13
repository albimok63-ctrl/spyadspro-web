"""Pipeline dati tra engine e service. Deduplicazione in memoria per singola esecuzione."""


class ScraperPipeline:
    """Pipeline: process(data) con deduplicazione in memoria; restituisce None se duplicato."""

    def __init__(self) -> None:
        self._seen_hashes = set()

    def process(self, data: dict) -> dict | None:
        """Se il dato è già stato visto restituisce None, altrimenti lo registra e restituisce data."""
        key = str(data)
        if key in self._seen_hashes:
            return None
        self._seen_hashes.add(key)
        return data
