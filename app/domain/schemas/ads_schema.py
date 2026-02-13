"""Schema dati comune per annunci da qualsiasi fonte di scraping (Facebook, TikTok, Google, ecc.)."""

from pydantic import BaseModel


class AdData(BaseModel):
    """Schema comune per normalizzare dati provenienti da fonti diverse."""

    source: str | None = None
    title: str | None = None
    description: str | None = None
    url: str | None = None
    image_url: str | None = None
    created_at: str | None = None
