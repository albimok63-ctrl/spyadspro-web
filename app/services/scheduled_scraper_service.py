"""Servizio per scraping schedulato: collega SimpleScheduler a ScraperService."""

from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.result_collector import ResultCollector
from app.infrastructure.scheduler.simple_scheduler import SimpleScheduler
from app.services.scraper_service import ScraperService


class ScheduledScraperService:
    """Esegue scraping periodico tramite SimpleScheduler e ScraperService."""

    def __init__(self, http_client: HttpClient) -> None:
        self._scheduler = SimpleScheduler()
        self.scraper_service = ScraperService(http_client)
        self.collector = ResultCollector()

    def start_title_scraping(self, url: str, interval_seconds: int) -> None:
        """Avvia lo scraping periodico con spider 'title' sull'url dato."""

        def job() -> None:
            result = self.scraper_service.scrape_title(url)
            self.collector.add(result)

        self._scheduler.start(interval_seconds, job)
