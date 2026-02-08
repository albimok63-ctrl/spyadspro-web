"""Servizio scraper: delega a http_client per GET, restituisce HTML grezzo. Nessun parsing."""

from app.infrastructure.scraper.http_client import HttpClient


class ScraperService:
    """Esegue GET verso una URL tramite http_client e restituisce il contenuto HTML grezzo."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def fetch_html(self, url: str) -> str:
        """Delega al http_client la GET; restituisce il corpo della risposta come stringa."""
        return self._http_client.get(url)
