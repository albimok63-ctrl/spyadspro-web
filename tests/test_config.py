"""
Test caricamento configurazione centralizzata (app/core/config.py).
"""

import pytest

from app.core.config import Settings


def test_config_loads_with_defaults() -> None:
    """La configurazione si carica con valori di default (secret_key, access_token_expire_minutes, environment)."""
    settings = Settings()
    assert settings.secret_key is not None
    assert len(settings.secret_key) >= 1
    assert settings.access_token_expire_minutes >= 1
    assert isinstance(settings.environment, str)


def test_config_reads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le variabili SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ENVIRONMENT sono leggibili da env."""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-32-chars-long!!")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    monkeypatch.setenv("ENVIRONMENT", "production")
    # Ricarica Settings (get_settings è lru_cached, quindi creiamo Settings direttamente per il test).
    settings = Settings()
    assert settings.secret_key == "test-secret-key-32-chars-long!!"
    assert settings.access_token_expire_minutes == 120
    assert settings.environment == "production"


def test_config_single_source() -> None:
    """Tutti i moduli possono leggere la stessa configurazione tramite get_settings() (cached)."""
    from app.core.dependencies import get_settings
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2  # lru_cached
    assert s1.secret_key == s2.secret_key
    assert s1.access_token_expire_minutes == s2.access_token_expire_minutes
    assert s1.environment == s2.environment
