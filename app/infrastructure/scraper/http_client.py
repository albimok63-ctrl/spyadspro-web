"""HTTP client: GET con requests, headers custom, timeout. Nessun parsing.

Include RealisticSession (anti-fingerprinting 2026), retry 403/429 con
exponential backoff + jitter, e integrazione con HttpClient/fetch_page.
"""

import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1
RETRY_STATUS_CODES = (500, 502, 503, 504)
BLOCK_STATUS_CODES = (403, 429)
DELAY_BEFORE_REQUEST_MIN = 1.0
DELAY_BEFORE_REQUEST_MAX = 3.0
BACKOFF_BASE = 2
BACKOFF_JITTER_MAX = 2.0
BACKOFF_CAP_SEC = 60

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
)

# Headers anti-fingerprinting (standard 2026): Chrome 119+, Sec-Fetch-*, Accept-Language
ANTI_FINGERPRINT_HEADERS = {
    "User-Agent": USER_AGENTS[0],
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

DEFAULT_HEADERS = {
    **ANTI_FINGERPRINT_HEADERS,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# Headers di default per la sessione persistente (browser realistico)
SESSION_DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def _exponential_backoff_with_jitter(attempt: int) -> float:
    """Ritardo = min(cap, base^attempt) + jitter casuale (comportamento umano)."""
    base_delay = min(BACKOFF_CAP_SEC, BACKOFF_BASE**attempt)
    jitter = random.uniform(0, min(BACKOFF_JITTER_MAX, base_delay))
    return base_delay + jitter


def _human_delay(min_sec: float = DELAY_BEFORE_REQUEST_MIN, max_sec: float = DELAY_BEFORE_REQUEST_MAX) -> None:
    """Delay casuale per simulare comportamento umano (riduce rilevamento bot)."""
    time.sleep(random.uniform(min_sec, max_sec))


class RealisticSession:
    """Sessione HTTP persistente: cookie e stato in memoria, headers realistici, fetch_with_retry per 403/429."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self._user_agents = list(USER_AGENTS)
        self.session.headers["User-Agent"] = random.choice(self._user_agents)
        self.session.headers.update(SESSION_DEFAULT_HEADERS)
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=list(RETRY_STATUS_CODES),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @property
    def headers(self):
        """Espone gli headers della sessione (per compatibilità con fetch_page e HttpClient)."""
        return self.session.headers

    def _rotate_user_agent(self) -> None:
        self.session.headers["User-Agent"] = random.choice(self._user_agents)

    def get(
        self,
        url: str,
        headers: dict | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        allow_redirects: bool = True,
        **kwargs,
    ) -> requests.Response:
        """GET tramite sessione: headers di default + eventuali custom (sovrascrivono), timeout, redirect. Rilancia RequestException."""
        return self.session.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=allow_redirects,
            **kwargs,
        )

    def fetch_with_retry(
        self,
        url: str,
        max_retries: int = MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> requests.Response:
        """GET con retry su 403/429 usando exponential backoff con jitter (comportamento umano)."""
        for attempt in range(max_retries):
            self._rotate_user_agent()
            _human_delay(DELAY_BEFORE_REQUEST_MIN, DELAY_BEFORE_REQUEST_MAX)
            response = self.get(url, timeout=timeout, allow_redirects=True, **kwargs)
            if response.status_code == 200:
                time.sleep(random.uniform(0.3, 0.7))
                return response
            if response.status_code in BLOCK_STATUS_CODES:
                if attempt < max_retries - 1:
                    delay = _exponential_backoff_with_jitter(attempt)
                    time.sleep(delay)
                    continue
                response.raise_for_status()
            if response.status_code in RETRY_STATUS_CODES:
                if attempt < max_retries - 1:
                    time.sleep(_exponential_backoff_with_jitter(attempt))
                    continue
                response.raise_for_status()
            response.raise_for_status()
        raise RuntimeError("fetch_with_retry exhausted retries without returning")


def fetch_page(url: str, headers: dict | None = None) -> str:
    """GET verso url; headers opzionali (sovrascrivono DEFAULT_HEADERS), timeout 10s. Usa RealisticSession e retry."""
    session = RealisticSession()
    session.headers.update(headers or {})
    response = session.fetch_with_retry(url, timeout=DEFAULT_TIMEOUT)
    return response.text


class HttpClient:
    """Esegue richieste HTTP GET tramite RealisticSession; headers e timeout configurabili."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None) -> None:
        self.timeout = timeout
        self._headers = dict(headers) if headers else {}
        self.session: RealisticSession = RealisticSession()
        self.session.headers.update(self._headers)

    def get(self, url: str) -> str:
        """GET verso url tramite RealisticSession.fetch_with_retry; restituisce response.text."""
        for key, value in self._headers.items():
            self.session.headers[key] = value
        response = self.session.fetch_with_retry(url, timeout=self.timeout)
        return response.text
