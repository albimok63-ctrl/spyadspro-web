"""Runner per esecuzione scraper: GET + HtmlParser + extract. Solo orchestrazione."""

from typing import Any

from app.infrastructure.scraper.base_scraper import BaseScraper
from app.infrastructure.scraper.html_parser import HtmlParser
from app.infrastructure.scraper.http_client import HttpClient


class ScraperRunner:
    """Esegue GET, crea parser, invoca scraper.extract(parser). Nessun DB, nessun endpoint."""

    def __init__(self, http_client: HttpClient, scraper: BaseScraper) -> None:
        self._http_client = http_client
        self._scraper = scraper

    def run(self, url: str) -> Any:
        """GET url, crea HtmlParser con l'HTML, chiama scraper.extract(parser) e restituisce il risultato."""
        html = self._http_client.get(url)
        parser = HtmlParser(html)
        result = self._scraper.extract(parser)
        return result
