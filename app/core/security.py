"""
JWT: creazione e validazione token. Integrazione API key: salvataggio oggetto validato su request.state.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import Settings


def set_api_key_on_request(request: Any, api_key_object: Any) -> None:
    """Salva l'oggetto API key validata su request.state per usage tracking e middleware."""
    request.state.api_key = api_key_object

ALGORITHM = "HS256"
SUB_KEY = "sub"


def create_access_token(data: dict, settings: Settings | None = None) -> str:
    """Crea un JWT a partire da un dict (es. {\"sub\": \"user_id\"}); aggiunge exp da settings."""
    if settings is None:
        from app.core.dependencies import get_settings
        settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {**data, "exp": expire}
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def verify_token(token: str, settings: Settings | None = None) -> dict:
    """Valida il JWT e restituisce il payload. Solleva jwt.PyJWTError se invalido o scaduto."""
    if settings is None:
        from app.core.dependencies import get_settings
        settings = get_settings()
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )
