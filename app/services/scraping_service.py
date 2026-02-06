"""Servizio scraping: orchestra HttpClient e HtmlParser. Nessun DB, nessun endpoint."""

from app.infrastructure.scraper.html_parser import HtmlParser
from app.infrastructure.scraper.http_client import HttpClient


class ScrapingService:
    """Orchestra fetch HTTP e parsing; dipendenze iniettate dal costruttore."""

    def __init__(self, http_client: HttpClient, html_parser_class: type[HtmlParser] = HtmlParser) -> None:
        self._http_client = http_client
        self._html_parser_class = html_parser_class

    def fetch_and_parse(self, url: str) -> HtmlParser:
        """Esegue GET tramite http_client, passa l'HTML a HtmlParser e restituisce l'istanza."""
        html = self._http_client.get(url)
        return self._html_parser_class(html)
