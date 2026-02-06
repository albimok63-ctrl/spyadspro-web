"""HTTP client: GET con requests, headers custom, timeout. Nessun parsing."""

import requests


DEFAULT_TIMEOUT = 10


def fetch_page(url: str, headers: dict | None = None) -> str:
    """GET verso url; headers opzionali, timeout 10s. Restituisce response.text. RequestException propaga."""
    response = requests.get(url, headers=headers or {}, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.text


class HttpClient:
    """Esegue richieste HTTP GET; headers e timeout configurabili. RequestException non gestita."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None) -> None:
        self.timeout = timeout
        self._headers = dict(headers) if headers else {}

    def get(self, url: str) -> str:
        """GET verso url; restituisce response.text. Solleva RequestException in caso di errore."""
        response = requests.get(url, headers=self._headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text
