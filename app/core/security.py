"""
JWT: creazione e validazione token. SECRET_KEY da env, HS256, scadenza configurabile.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request

from app.core.config import Settings
from app.core.dependencies import get_settings

ALGORITHM = "HS256"
SUB_KEY = "sub"  # user_id nel payload


def create_access_token(user_id: str, settings: Settings | None = None) -> str:
    """Crea un JWT con sub=user_id e scadenza da config."""
    settings = settings or get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {SUB_KEY: user_id, "exp": expire}
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_token(token: str, settings: Settings | None = None) -> dict:
    """Valida il JWT e restituisce il payload. Solleva jwt.PyJWTError se invalido."""
    settings = settings or get_settings()
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )


def get_current_user(request: Request) -> str:
    """
    Dependency: legge Authorization header, valida JWT, restituisce user_id (sub).
    Solleva 401 se header mancante o token invalido.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get(SUB_KEY)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return str(user_id)
