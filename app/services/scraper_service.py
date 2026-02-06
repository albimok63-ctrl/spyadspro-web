"""Servizio scraper: orchestratore tra HttpClient e HtmlParser. Nessun DB né endpoint."""

from app.infrastructure.scraper.html_parser import HtmlParser
from app.infrastructure.scraper.http_client import HttpClient


class ScraperService:
    """Recupera HTML via HttpClient e restituisce il risultato del parsing (HtmlParser)."""

    def fetch_and_parse(self, url: str) -> HtmlParser:
        """Ottiene l'HTML dalla URL tramite HttpClient e restituisce un HtmlParser pronto per l'uso."""
        client = HttpClient()
        html = client.get(url)
        return HtmlParser(html)
