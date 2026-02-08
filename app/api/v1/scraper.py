"""Endpoint minimale per test scraper: GET /scrape/title, anteprima 200 caratteri HTML."""

from fastapi import APIRouter

from app.infrastructure.scraper.http_client import HttpClient
from app.services.scraper_service import ScraperService


http_client = HttpClient()
scraper_service = ScraperService(http_client)

router = APIRouter(prefix="/scrape", tags=["scraper"])


@router.get("/title")
def get_scrape_title(url: str) -> dict:
    """Test: GET della pagina, restituisce i primi 200 caratteri dell'HTML."""
    html = scraper_service.fetch_html(url)
    preview = html[:200]
    return {"preview": preview}
