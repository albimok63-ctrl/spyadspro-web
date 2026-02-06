"""Classe base astratta per scraper. Contratto senza logica né DB."""

from abc import ABC, abstractmethod

from app.infrastructure.scraper.html_parser import HtmlParser


class BaseScraper(ABC):
    """Contratto per gli scraper: estrazione dati da HtmlParser già inizializzato."""

    @abstractmethod
    def extract(self, parser: HtmlParser):
        """
        Riceve un HtmlParser già inizializzato
        e restituisce dati estratti.
        """
        pass
