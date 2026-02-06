"""Endpoint GET /scrape/title tramite ScraperService. Nessun DB, nessun repository."""

from fastapi import APIRouter

from app.services.scraper_service import ScraperService


router = APIRouter(tags=["scraper"])


@router.get("/scrape/title")
def get_scrape_title(url: str) -> dict:
    """
    Estrae il contenuto del tag <title> dalla pagina indicata.
    Query: url (str).
    """
    service = ScraperService()
    parser = service.fetch_and_parse(url)
    title = parser.get_title()
    return {"title": title}
