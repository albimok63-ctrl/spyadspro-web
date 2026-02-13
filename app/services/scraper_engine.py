"""ScraperEngine: esecuzione spider tramite registry interno. Compatibile con architettura esistente."""

from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.spiders.title_spider import TitleSpider


class ScraperEngine:
    """Gestisce l'esecuzione degli spider tramite registry; supporto multi-spider senza modificare il resto."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        self.spiders = {
            "title": TitleSpider,
        }

    def run(self, spider_name: str, url: str):
        """Esegue lo spider indicato sulla url. Solleva ValueError se spider non registrato."""
        if spider_name not in self.spiders:
            raise ValueError("Spider non registrato")
        spider_class = self.spiders[spider_name]
        spider = spider_class(self._http_client)
        return spider.run(url)
