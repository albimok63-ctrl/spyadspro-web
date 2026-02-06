"""
Logging strutturato JSON. Solo standard library.
Output machine-readable (ELK / Loki). Stdout per Docker.
Campi: timestamp, level, service_name, message, request_id, path, method, status_code, duration_ms (quando disponibili).
Livello: INFO di default, DEBUG se LOG_LEVEL=DEBUG o DEBUG=true.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any


def _log_level_from_env() -> int:
    """Livello da ENV: LOG_LEVEL (INFO|DEBUG) o DEBUG=true."""
    level = os.getenv("LOG_LEVEL", "").upper()
    if level == "DEBUG":
        return logging.DEBUG
    if os.getenv("DEBUG", "false").lower() in ("true", "1"):
        return logging.DEBUG
    return logging.INFO

# Contextvar per correlazione: iniettato in ogni log durante la richiesta (middleware setta/cleara).
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str | None) -> None:
    """Imposta il request_id nel contesto della richiesta (chiamato dal middleware)."""
    _request_id_ctx.set(request_id)


def clear_request_id() -> None:
    """Rimuove il request_id dal contesto (fine richiesta)."""
    try:
        _request_id_ctx.set(None)
    except LookupError:
        pass


def get_request_id() -> str | None:
    """Restituisce il request_id del contesto corrente (per log/correlazione)."""
    try:
        return _request_id_ctx.get()
    except LookupError:
        return None


class RequestIdFilter(logging.Filter):
    """Inietta request_id dal contextvar in ogni LogRecord (log contestuali)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "request_id", None) is None:
            rid = get_request_id()
            if rid is not None:
                record.request_id = rid
        return True


def _safe_iso_timestamp(record: logging.LogRecord) -> str:
    """UTC ISO timestamp from record.created."""
    dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
    return dt.isoformat()


class JsonFormatter(logging.Formatter):
    """
    Formatta ogni record come una singola riga JSON.
    Campi: timestamp, level, service_name, message, request_id, path, method, status_code, duration_ms (se presenti).
    """

    def __init__(self, service_name: str = "app") -> None:
        super().__init__()
        self._service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_dict: dict[str, Any] = {
            "timestamp": _safe_iso_timestamp(record),
            "level": record.levelname,
            "service_name": self._service_name,
            "message": record.getMessage(),
        }
        if getattr(record, "event", None) is not None:
            log_dict["event"] = record.event
        if getattr(record, "request_id", None) is not None:
            log_dict["request_id"] = record.request_id
        if getattr(record, "path", None) is not None:
            log_dict["path"] = record.path
        if getattr(record, "method", None) is not None:
            log_dict["method"] = record.method
        if getattr(record, "status_code", None) is not None:
            log_dict["status_code"] = record.status_code
        if getattr(record, "duration_ms", None) is not None:
            log_dict["duration_ms"] = record.duration_ms
        if getattr(record, "user_id", None) is not None:
            log_dict["user_id"] = record.user_id
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_dict, ensure_ascii=False)


def get_logger(name: str = "app", service_name: str | None = None) -> logging.Logger:
    """
    Restituisce il logger dell'app con output JSON su stdout.
    Configura il logger alla prima chiamata (handler + JsonFormatter).
    """
    logger = logging.getLogger(name)
    for h in logger.handlers:
        if isinstance(h.formatter, JsonFormatter):
            return logger
    try:
        from app.core.dependencies import get_settings
        svc = service_name or get_settings().app_name
    except Exception:
        svc = service_name or "app"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service_name=svc))
    handler.addFilter(RequestIdFilter())
    logger.addHandler(handler)
    logger.setLevel(_log_level_from_env())
    logger.propagate = False
    return logger
