"""Servizio scraper: layer tra API e spider. Delega a http_client e registry spider."""

import hashlib
from datetime import date

from app.infrastructure.database import get_db
from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.models import ScrapeResult
from app.infrastructure.scraper.spider_registry import SpiderRegistry
from app.infrastructure.scraper.spiders.meta_title_spider import MetaTitleSpider
from app.infrastructure.scraper.spiders.title_spider import TitleSpider
from app.models.ad_analysis import AdAnalysisRead
from app.repositories.ad_repository import AdRepository


def _scrape_result_to_ad_data(result: dict | ScrapeResult) -> dict:
    """Mappa il risultato dello spider in ad_data per AdRepository.save_ad."""
    if isinstance(result, ScrapeResult):
        source = result.source
        url = result.url or ""
        data = result.data or {}
        title = data.get("title") or ""
        ad_copy = data.get("meta_description") or title or None
    else:
        source = result.get("source", "meta")
        url = result.get("url") or ""
        data = result.get("data") or result
        title = data.get("title") or result.get("title") or ""
        ad_copy = data.get("meta_description") or data.get("description") or title or None
    ad_id = hashlib.sha256(url.encode()).hexdigest()[:64] if url else "unknown"
    return {
        "ad_id": ad_id,
        "platform": source,
        "status": "active",
        "start_date": date.today(),
        "end_date": None,
        "ad_copy": ad_copy,
        "creative_url": None,
        "landing_page_url": url or None,
        "days_active": 0,
        "is_winning_ad": False,
        "performance_score": 0.0,
    }


class ScraperService:
    """Separa API dalla logica di scraping: fetch_html, scrape_title o scrape(spider_name, url)."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        self.registry = SpiderRegistry()
        self.registry.register("title", TitleSpider)
        self.registry.register("meta", MetaTitleSpider)

    def scrape(self, spider_name: str, url: str) -> dict:
        """Ottiene lo spider dal registry, crea istanza, esegue run(url). Solleva ValueError se spider non trovato."""
        spider_class = self.registry.get(spider_name)
        if spider_class is None:
            raise ValueError(f"Spider '{spider_name}' not found")
        spider = spider_class(self._http_client)
        return spider.run(url)

    def fetch_html(self, url: str) -> str:
        """Delega al http_client la GET; restituisce il corpo della risposta come stringa."""
        return self._http_client.get(url)

    def scrape_title(self, url: str) -> dict:
        """Ottiene spider 'title' dal registry, crea istanza, esegue run(url), persiste su DB e restituisce il risultato."""
        spider_class = self.registry.get("title")
        if spider_class is None:
            raise ValueError("Spider 'title' not found")
        spider = spider_class(self._http_client)
        result = spider.run(url)
        # Persistenza: sessione DB e save tramite AdRepository
        for db in get_db():
            ad_data = _scrape_result_to_ad_data(result)
            AdRepository().save_ad(db, ad_data)
            break
        # Restituisce il risultato come prima (comportamento API invariato)
        if isinstance(result, ScrapeResult):
            return {"source": result.source, "url": result.url, "data": result.data}
        return result
