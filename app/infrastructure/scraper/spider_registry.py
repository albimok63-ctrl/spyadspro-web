"""Registry centrale degli spider disponibili. Supporto multi-spider senza modifiche future."""

from app.infrastructure.scraper.spiders.title_spider import TitleSpider


class SpiderRegistry:
    """Registro degli spider: get_spider(name) restituisce la classe o solleva ValueError."""

    def __init__(self) -> None:
        self.spiders = {
            "title": TitleSpider,
        }

    def get_spider(self, spider_name: str):
        """Restituisce la classe spider corrispondente. Solleva ValueError se non esiste."""
        spider_class = self.spiders.get(spider_name)
        if spider_class is None:
            raise ValueError("Spider not found")
        return spider_class

    def get(self, name: str):
        """Restituisce la classe spider o None. Preferire get_spider per errore esplicito."""
        return self.spiders.get(name)
