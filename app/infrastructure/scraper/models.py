"""Struttura dati standard per l'output degli spider. Nessun DB né validazione complessa."""

from dataclasses import dataclass


@dataclass
class ScrapeResult:
    """Output standardizzato di uno spider: source, url, data."""

    source: str
    url: str
    data: dict
