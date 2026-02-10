"""HTTP client: GET con requests, headers custom, timeout. Nessun parsing."""

import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1
RETRY_STATUS_CODES = (500, 502, 503, 504)

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENTS[0],
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


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
        self.session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=list(RETRY_STATUS_CODES),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.delay = 1.0
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0 Safari/537.36",
        ]

    def get(self, url: str) -> str:
        """GET verso url; restituisce response.text. Retry solo su 500/502/503/504 (max 3 tentativi, 1s tra tentativi)."""
        headers = {**DEFAULT_HEADERS, **self._headers}
        if "User-Agent" not in self._headers:
            headers["User-Agent"] = random.choice(self.user_agents)
        for attempt in range(MAX_RETRIES):
            time.sleep(self.delay)
            response = self.session.get(
                url, headers=headers, timeout=self.timeout, allow_redirects=True
            )
            if response.status_code in RETRY_STATUS_CODES:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            response.raise_for_status()
            time.sleep(0.5)
            return response.text
        raise RuntimeError("get() exhausted retries without returning")
