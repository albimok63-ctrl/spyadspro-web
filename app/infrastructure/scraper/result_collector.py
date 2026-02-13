"""Memorizzazione temporanea in memoria dei risultati di scraping."""


class ResultCollector:
    """Accumula risultati di scraping in una lista; per uso con scheduler prima di DB/Redis."""

    def __init__(self) -> None:
        self._results: list = []

    def add(self, data: dict) -> None:
        """Aggiunge data alla lista solo se non None."""
        if data is not None:
            self._results.append(data)

    def all(self) -> list:
        """Restituisce la lista dei risultati."""
        return self._results

    def clear(self) -> None:
        """Svuota la lista."""
        self._results.clear()
