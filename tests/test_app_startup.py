"""
Test avvio app: importabilità senza errori, pronta per container Docker.
"""


def test_app_import() -> None:
    """L'app FastAPI è importabile senza ModuleNotFoundError o altri errori."""
    from app.main import app
    assert app is not None
