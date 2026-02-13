"""
Meta Spider – estrazione dati inserzioni Meta (Social Media Scraping 2026).
Usa RealisticSession, estrazione JSON da script (regex), mapping su AdIntelligence, pulizia copy.
"""

import json
import re
from datetime import date
from typing import Any

from app.infrastructure.scraper.base_spider import BaseSpider
from app.infrastructure.scraper.http_client import HttpClient
from app.models.marketing_intelligence import AdIntelligence, PlatformEnum


# Pattern per blocchi JSON nel sorgente HTML (invisibilità: nessun CSS fragile)
PATTERN_SHARED_DATA = re.compile(
    r"window\._sharedData\s*=\s*(\{.*?\});",
    re.DOTALL,
)
PATTERN_LD_JSON = re.compile(
    r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

# Emoji: blocchi Unicode comuni (emoji eccessive da ridurre)
EMOJI_PATTERN = re.compile(
    r"[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+",
    re.UNICODE,
)


def _clean_copy_text(text: str | None) -> str:
    """Pulisce il testo del copy: emoji eccessive e spazi bianchi superflui."""
    if not text or not isinstance(text, str):
        return ""
    # Normalizza spazi (multipli/newline/tab -> singolo spazio) e trim
    cleaned = re.sub(r"\s+", " ", text).strip()
    # Riduce sequenze di 3+ emoji a uno spazio (mantiene 1–2 emoji)
    cleaned = EMOJI_PATTERN.sub(lambda m: " " if len(m.group()) > 2 else m.group(), cleaned)
    # Nuova normalizzazione spazi dopo rimozione emoji
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _extract_json_blocks(html: str) -> list[dict[str, Any]]:
    """Cerca nel sorgente HTML blocchi JSON (window._sharedData o application/ld+json) via regex."""
    blocks: list[dict[str, Any]] = []
    # window._sharedData = {...};
    for match in PATTERN_SHARED_DATA.finditer(html):
        try:
            raw = match.group(1).strip()
            blocks.append(json.loads(raw))
        except (json.JSONDecodeError, IndexError):
            continue
    # <script type="application/ld+json">...</script>
    for match in PATTERN_LD_JSON.finditer(html):
        try:
            raw = match.group(1).strip()
            blocks.append(json.loads(raw))
        except (json.JSONDecodeError, IndexError):
            continue
    return blocks


def _find_in_nested(obj: Any, *keys: str) -> Any:
    """Cerca ricorsivamente una chiave in dict/list annidati; restituisce il primo valore trovato."""
    if isinstance(obj, dict):
        for key in keys:
            if key in obj:
                return obj[key]
        for v in obj.values():
            found = _find_in_nested(v, *keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_in_nested(item, *keys)
            if found is not None:
                return found
    return None


def _parse_date_from_value(value: Any) -> date | None:
    """Prova a ricavare una date da timestamp Unix, stringa ISO o 'YYYY-MM-DD'."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        try:
            from datetime import datetime

            return datetime.utcfromtimestamp(int(value)).date()
        except (ValueError, OSError):
            return None
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except (ValueError, TypeError):
            return None
    return None


def _map_blocks_to_ad_intelligence(blocks: list[dict[str, Any]]) -> AdIntelligence | None:
    """Estrae da uno o più blocchi JSON i campi di un'inserzione e mappa in AdIntelligence."""
    ad_id: str | None = None
    copy_text: str | None = None
    creative_url: str | None = None
    start_date: date | None = None

    for blob in blocks:
        if ad_id is None:
            ad_id = _find_in_nested(
                blob,
                "ad_id", "id", "adId", "ad_snapshot_id",
                "pk", "media_id", "campaign_id",
            )
            if isinstance(ad_id, (int, float)):
                ad_id = str(int(ad_id))
            elif ad_id is not None and not isinstance(ad_id, str):
                ad_id = str(ad_id)

        if copy_text is None:
            raw = _find_in_nested(
                blob,
                "copy_text", "copy", "caption", "text", "message", "body",
                "ad_copy", "ad_snapshot_body", "description",
            )
            if raw is not None and isinstance(raw, str):
                copy_text = _clean_copy_text(raw)

        if creative_url is None:
            raw = _find_in_nested(
                blob,
                "creative_url", "creative_url_url", "image_url", "video_url",
                "thumbnail_url", "display_url", "media_url",
            )
            if raw is not None and isinstance(raw, str):
                creative_url = raw

        if start_date is None:
            raw = _find_in_nested(
                blob,
                "start_date", "start_time", "created_time", "timestamp",
                "created_at", "startDate", "launch_date",
            )
            start_date = _parse_date_from_value(raw)

    ad_id = ad_id or "unknown"
    start_date = start_date or date.today()

    return AdIntelligence(
        ad_id=ad_id,
        platform=PlatformEnum.META,
        start_date=start_date,
        copy_text=copy_text or None,
        creative_url=creative_url,
    )


class MetaSpider(BaseSpider):
    """Spider per inserzioni Meta: RealisticSession, estrazione JSON da script (regex), output AdIntelligence."""

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)

    def parse(self, response: str) -> dict:
        """Estrae blocchi JSON dal HTML (window._sharedData / ld+json) e mappa in AdIntelligence."""
        blocks = _extract_json_blocks(response)
        ad_intelligence = _map_blocks_to_ad_intelligence(blocks)
        return {
            "ad_intelligence": ad_intelligence.model_dump() if ad_intelligence else None,
            "json_blocks_found": len(blocks),
        }
