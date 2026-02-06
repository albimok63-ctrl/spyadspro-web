"""Test fetch_page senza chiamate HTTP reali (requests-mock)."""

import pytest
import requests
import requests_mock

from app.infrastructure.scraper.http_client import fetch_page


def test_fetch_page_returns_html_on_200() -> None:
    """Simula risposta 200 e verifica che venga restituito l'HTML."""
    url = "https://example.com/page"
    html = "<html><body><h1>Hello</h1></body></html>"
    with requests_mock.Mocker() as m:
        m.get(url, text=html, status_code=200)
        result = fetch_page(url)
    assert result == html


def test_fetch_page_raises_http_error_on_404() -> None:
    """Simula 404 e verifica che venga sollevata HTTPError."""
    url = "https://example.com/missing"
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404, text="Not Found")
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            fetch_page(url)
        assert exc_info.value.response.status_code == 404
