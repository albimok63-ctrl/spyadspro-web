"""Endpoint per scraping multi-fonte: GET /scrape/title con parametro source."""

from fastapi import APIRouter, HTTPException

from app.infrastructure.scraper.engine import ScraperEngine
from app.infrastructure.scraper.http_client import HttpClient
from app.services.scraper_service import ScraperService
from app.services.scheduled_scraper_service import ScheduledScraperService


http_client = HttpClient()
engine = ScraperEngine(http_client)
scraper_service = ScraperService(http_client)
scheduled_service = ScheduledScraperService(http_client)

router = APIRouter(prefix="/scrape", tags=["scraper"])


@router.get("/title")
def get_scrape_title(url: str, source: str = "title") -> dict:
    """Esegue scraping con lo spider indicato da source (es. title, meta). Spider non trovato -> 404."""
    try:
        return scraper_service.scrape(source, url)
    except ValueError:
        raise HTTPException(status_code=404, detail="Spider not found")


@router.get("/results")
def get_results() -> list:
    """Restituisce i risultati accumulati dallo scraper (engine.result_store)."""
    return engine.result_store.all()


@router.post("/start")
def start_scheduled_scraping(url: str, interval_seconds: int = 30) -> dict:
    """Avvia lo scraping automatico periodico sull'url indicato."""
    scheduled_service.start_title_scraping(url=url, interval_seconds=interval_seconds)
    return {"status": "scheduler started"}
