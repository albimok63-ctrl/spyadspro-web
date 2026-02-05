"""
Test dipendenze: pacchetti richiesti per il runtime e per la build Docker sono installabili.
"""


def test_core_dependencies_importable() -> None:
    """FastAPI, SQLAlchemy, Pydantic e pydantic_settings sono importabili (ambiente pronto)."""
    import fastapi
    import sqlalchemy
    import pydantic
    import pydantic_settings
    assert fastapi is not None
    assert sqlalchemy is not None
    assert pydantic is not None
    assert pydantic_settings is not None
