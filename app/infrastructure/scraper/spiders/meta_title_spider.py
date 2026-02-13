"""Spider che estrae title e meta description da HTML. Seconda fonte dati compatibile con AdData."""

from app.infrastructure.scraper.base_spider import BaseSpider
from app.infrastructure.scraper.html_parser import HtmlParser


class MetaTitleSpider(BaseSpider):
    """Estrae <title> e meta name='description' dalla risposta HTML; output compatibile con AdData."""

    def parse(self, response: str) -> dict:
        parser = HtmlParser(response)
        title = parser.get_title()
        meta_tags = parser.find_all_by_attribute("meta", "name", "description")
        description = None
        if meta_tags and meta_tags[0].get("content"):
            description = meta_tags[0]["content"].strip()
        return {
            "source": "meta",
            "title": title,
            "description": description,
            "url": "",
        }

    def run(self, url: str) -> dict:
        """Esegue fetch e restituisce il dict con url impostato."""
        data = super().run(url)
        data["url"] = url
        return data
