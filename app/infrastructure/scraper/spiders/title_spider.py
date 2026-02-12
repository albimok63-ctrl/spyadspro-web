"""Spider per estrarre title e meta description da HTML. Implementa BaseSpider."""

from bs4 import BeautifulSoup

from app.infrastructure.scraper.base_spider import BaseSpider


class TitleSpider(BaseSpider):
    """Estrae <title> e meta name='description' da una risposta HTML."""

    def parse(self, response: str) -> dict:
        soup = BeautifulSoup(response, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = None
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"].strip()
        return {"title": title, "description": description}

    def run(self, url: str) -> dict:
        """Restituisce dict standardizzato: url, title, description, source."""
        parsed = super().run(url)
        return {
            "url": url,
            "title": parsed["title"],
            "description": parsed["description"],
            "source": "title_spider",
        }
