"""
Test professionali per Marketing Intelligence: modello, MetaSpider parsing, resilienza HTTP.
Nessuna modifica al codice applicativo, nessuna connessione di rete reale.
"""

from datetime import date, timedelta

import pytest

from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.meta_spider import MetaSpider
from app.models.marketing_intelligence import AdIntelligence, PlatformEnum


# ---------------------------------------------------------------------------
# TEST 1 — MODELLO (Business Logic)
# ---------------------------------------------------------------------------


def test_ad_intelligence_is_winning_ad_when_days_active_gt_14() -> None:
    """Se days_active > 14 → is_winning_ad == True."""
    today = date.today()
    ad = AdIntelligence(
        ad_id="win-1",
        platform=PlatformEnum.META,
        start_date=today - timedelta(days=20),
    )
    assert ad.days_active > 14
    assert ad.is_winning_ad is True


def test_ad_intelligence_is_not_winning_ad_when_days_active_lt_14() -> None:
    """Se days_active < 14 → is_winning_ad == False."""
    today = date.today()
    ad = AdIntelligence(
        ad_id="loss-1",
        platform=PlatformEnum.META,
        start_date=today - timedelta(days=7),
    )
    assert ad.days_active < 14
    assert ad.is_winning_ad is False


def test_ad_intelligence_two_instances_minimal_valid_data() -> None:
    """Due istanze con dati minimi validi: una winning, una non winning."""
    today = date.today()
    winning = AdIntelligence(
        ad_id="w1",
        platform=PlatformEnum.META,
        start_date=today - timedelta(days=15),
    )
    not_winning = AdIntelligence(
        ad_id="n1",
        platform=PlatformEnum.META,
        start_date=today - timedelta(days=5),
    )
    assert winning.days_active == 15 and winning.is_winning_ad is True
    assert not_winning.days_active == 5 and not_winning.is_winning_ad is False


# ---------------------------------------------------------------------------
# TEST 2 — SPIDER PARSING (Mock HTML, nessuna HTTP reale)
# ---------------------------------------------------------------------------

# HTML di esempio con title, meta description e blocco ld+json per estrazione annuncio
MOCK_HTML_WITH_LD_JSON = """
<!DOCTYPE html>
<html>
<head>
  <title>Meta Ad Example - Campaign 2026</title>
  <meta name="description" content="Pagina di esempio per inserzione Meta con dati strutturati.">
</head>
<body>
  <div class="content">Placeholder</div>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Ad",
    "id": "ad-456",
    "start_date": "2024-01-01",
    "copy": "Test copy per annuncio."
  }
  </script>
</body>
</html>
"""


def test_meta_spider_parse_extracts_data_from_mock_html() -> None:
    """MetaSpider.parse() estrae correttamente i dati da HTML mock (nessuna chiamata HTTP)."""
    # Nessun HttpClient reale usato: chiamiamo solo parse() con HTML simulato
    client = HttpClient()
    spider = MetaSpider(client)
    result = spider.parse(MOCK_HTML_WITH_LD_JSON)
    assert "ad_intelligence" in result
    assert "json_blocks_found" in result
    assert result["json_blocks_found"] >= 1
    assert result["ad_intelligence"] is not None


def test_meta_spider_parse_returns_valid_intelligence_model() -> None:
    """Il risultato di parse() è un oggetto valido del modello di intelligence (dict validabile)."""
    client = HttpClient()
    spider = MetaSpider(client)
    result = spider.parse(MOCK_HTML_WITH_LD_JSON)
    ad_dict = result.get("ad_intelligence")
    assert ad_dict is not None
    # Ricostruisce il modello da dict: verifica che sia rappresentazione valida
    validated = AdIntelligence.model_validate(ad_dict)
    assert validated.ad_id == "ad-456"
    assert validated.platform == PlatformEnum.META
    assert validated.start_date == date(2024, 1, 1)
    assert validated.copy_text == "Test copy per annuncio."


def test_meta_spider_parse_does_not_return_none_ad_intelligence() -> None:
    """parse() con HTML contenente ld+json non ritorna ad_intelligence None."""
    client = HttpClient()
    spider = MetaSpider(client)
    result = spider.parse(MOCK_HTML_WITH_LD_JSON)
    assert result["ad_intelligence"] is not None


# ---------------------------------------------------------------------------
# TEST 3 — RESILIENZA HTTP CLIENT (mock 429, retry/backoff, eccezione dopo retry)
# ---------------------------------------------------------------------------


def test_http_client_429_retry_then_raises_after_exhaustion(mocker) -> None:
    """Simula 429: la sessione non crasha, esegue retry/backoff, solleva eccezione solo dopo i retry."""
    import requests_mock

    # Patch time.sleep per evitare attese reali (backoff simulato ma istantaneo in test)
    mocker.patch("app.infrastructure.scraper.http_client.time.sleep")
    mocker.patch("app.infrastructure.scraper.http_client._human_delay")

    url = "https://example.com/rate-limited"
    client = HttpClient()

    with requests_mock.Mocker() as rm:
        # Ogni richiesta restituisce 429 (Too Many Requests)
        rm.get(url, status_code=429, text="Too Many Requests")

        # La sessione non deve crashare: deve ritentare e poi sollevare dopo esaurimento retry
        with pytest.raises(Exception) as exc_info:
            client.get(url)

        # Eccezione corretta: HTTPError con status 429 (da raise_for_status dopo retry)
        exc = exc_info.value
        response = getattr(exc, "response", None)
        assert response is not None
        assert response.status_code == 429

    # Verifica che siano stati effettuati più tentativi (retry)
    assert len(rm.request_history) >= 2


def test_http_client_429_does_not_crash_and_raises_after_retries(mocker) -> None:
    """Con 429 persistente: nessun crash, eccezione sollevata solo dopo i retry previsti."""
    import requests_mock

    mocker.patch("app.infrastructure.scraper.http_client.time.sleep")
    mocker.patch("app.infrastructure.scraper.http_client._human_delay")

    url = "https://test.example.com/429"
    client = HttpClient()

    with requests_mock.Mocker() as rm:
        rm.get(url, status_code=429, text="Too Many Requests")
        with pytest.raises(Exception):
            client.get(url)
        # Almeno 2 chiamate (primo tentativo + almeno un retry)
        assert rm.called
        assert len(rm.request_history) >= 2
