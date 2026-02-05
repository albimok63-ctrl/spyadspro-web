"""
Test struttura progetto: moduli app esistono e sono discoverable (importlib).
"""

import importlib.util


def test_main_module_exists() -> None:
    """Il modulo app.main esiste ed è importabile."""
    assert importlib.util.find_spec("app.main") is not None


def test_api_module_exists() -> None:
    """Il modulo app.api esiste ed è importabile."""
    assert importlib.util.find_spec("app.api") is not None


def test_core_module_exists() -> None:
    """Il modulo app.core esiste ed è importabile."""
    assert importlib.util.find_spec("app.core") is not None
