"""HTTP client per scraping – richieste GET con timeout e User-Agent."""

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as RequestsConnectionError


DEFAULT_TIMEOUT = 10
DEFAULT_USER_AGENT = "SpyAdsPro-Web/1.0 (scraper)"


class HttpClient:
    """Client HTTP base per fetching di pagine (es. scraping)."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self._headers = {"User-Agent": self.user_agent}

    def get(self, url: str) -> str:
        """
        Esegue una GET verso url e restituisce il corpo della risposta come testo.

        :param url: URL da richiedere.
        :return: Contenuto della risposta (es. HTML).
        :raises requests.exceptions.RequestException: In caso di errore di rete, timeout o HTTP 4xx/5xx.
        """
        try:
            response = requests.get(
                url,
                headers=self._headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.text
        except (Timeout, RequestsConnectionError, RequestException):
            raise
