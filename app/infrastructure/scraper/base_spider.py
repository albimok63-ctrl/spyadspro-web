"""Classe base astratta per spider: contratto parse(response) -> dict. Nessun fetch né parsing qui."""

from abc import ABC, abstractmethod

from app.infrastructure.scraper.http_client import HttpClient


class BaseSpider(ABC):
    """Contratto per spider: riceve http_client, espone parse(response) da implementare."""

    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    def run(self, url: str) -> dict:
        """Esegue fetch con http_client e delega a parse(html). Restituisce dati strutturati."""
        html = self.http_client.get(url)
        return self.parse(html)

    @abstractmethod
    def parse(self, response: str) -> dict:
        """Da implementare negli spider concreti. Riceve il corpo della risposta, restituisce dati strutturati."""
        ...
