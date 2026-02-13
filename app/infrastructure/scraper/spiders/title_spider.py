"""Spider per estrarre title e meta description da HTML. Implementa BaseSpider."""

from bs4 import BeautifulSoup

from app.infrastructure.scraper.base_spider import BaseSpider
from app.infrastructure.scraper.models import ScrapeResult


class TitleSpider(BaseSpider):
    """Estrae <title> e meta name='description' da una risposta HTML."""

    def parse(self, response: str) -> ScrapeResult:
        soup = BeautifulSoup(response, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_description = None
        if meta_desc and meta_desc.get("content"):
            meta_description = meta_desc["content"].strip()
        return ScrapeResult(
            source="title_spider",
            url="",
            data={
                "title": title,
                "meta_description": meta_description,
            },
        )

    def run(self, url: str) -> ScrapeResult:
        """Restituisce ScrapeResult con url impostato."""
        result = super().run(url)
        return ScrapeResult(source=result.source, url=url, data=result.data)
