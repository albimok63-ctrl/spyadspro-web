"""
Base dichiarativa SQLAlchemy 2.x. Nessuna logica, solo definizione base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base per tutti i modelli ORM."""

    pass
