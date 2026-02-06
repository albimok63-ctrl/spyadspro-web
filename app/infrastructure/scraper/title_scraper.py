"""Scraper per il tag <title>. Estende BaseScraper."""

from app.infrastructure.scraper.base_scraper import BaseScraper
from app.infrastructure.scraper.html_parser import HtmlParser


class TitleScraper(BaseScraper):
    """Estrae il contenuto del tag <title> da un HtmlParser."""

    def extract(self, parser: HtmlParser) -> str | None:
        """Restituisce il testo del tag <title> oppure None se assente."""
        return parser.get_title()
