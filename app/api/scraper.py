"""Endpoint di test per scraping title. Nessun DB, nessuna auth."""

from fastapi import APIRouter

from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.title_scraper import TitleScraper
from app.infrastructure.scraper.scraper_runner import ScraperRunner


router = APIRouter(tags=["scraper"])


@router.get("/scrape/title")
def get_scrape_title(url: str) -> dict:
    """
    Endpoint di test: estrae il <title> dalla pagina indicata.
    Query: url (string).
    """
    http_client = HttpClient()
    scraper = TitleScraper()
    runner = ScraperRunner(http_client, scraper)
    title = runner.run(url)
    return {"title": title}
