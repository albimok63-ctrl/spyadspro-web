"""Servizio scraper: layer tra API e spider. Delega a http_client e registry spider."""

from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.spider_registry import SpiderRegistry


class ScraperService:
    """Separa API dalla logica di scraping: fetch_html, scrape_title o scrape(spider_name, url)."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        self.registry = SpiderRegistry()

    def scrape(self, spider_name: str, url: str) -> dict:
        """Ottiene lo spider dal registry, crea istanza, esegue run(url). Solleva ValueError se spider non trovato."""
        spider_class = self.registry.get_spider(spider_name)
        spider = spider_class(self._http_client)
        return spider.run(url)

    def fetch_html(self, url: str) -> str:
        """Delega al http_client la GET; restituisce il corpo della risposta come stringa."""
        return self._http_client.get(url)

    def scrape_title(self, url: str) -> dict:
        """Ottiene spider 'title' dal registry, esegue run(url) e restituisce il risultato."""
        spider_class = self.registry.get_spider("title")
        spider = spider_class(self._http_client)
        return spider.run(url)
