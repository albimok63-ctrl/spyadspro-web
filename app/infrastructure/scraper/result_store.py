"""Memorizzazione temporanea in memoria dei risultati di scraping. Nessun DB, cache o filesystem."""


class ResultStore:
    """Accumula risultati di scraping in una lista in memoria per la sessione di scraping."""

    def __init__(self) -> None:
        self._results: list = []

    def add(self, data: dict) -> None:
        """Aggiunge data alla lista solo se non è None."""
        if data is not None:
            self._results.append(data)

    def all(self) -> list:
        """Restituisce la lista completa dei risultati."""
        return self._results

    def clear(self) -> None:
        """Svuota la lista."""
        self._results.clear()
