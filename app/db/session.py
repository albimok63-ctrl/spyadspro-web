"""
Engine e sessione SQLAlchemy 2.x. Fornitura sessione per dependency injection.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.base import Base
from app.db.models import api_key_orm  # noqa: F401 – registra ApiKeyORM in Base.metadata
from app.db.models import api_usage_orm  # noqa: F401 – registra ApiUsageORM in Base.metadata
from app.db.models import item_orm  # noqa: F401 – registra ItemORM in Base.metadata


def _get_engine():
    """Engine SQLite (o altro da config). Connect args per SQLite."""
    settings = Settings()
    connect_args = {} if not settings.database_url.startswith("sqlite") else {"check_same_thread": False}
    return create_engine(settings.database_url, connect_args=connect_args, echo=settings.debug)


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Crea le tabelle sul DB collegato a engine. Chiamato a startup o nei test."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield una sessione DB per request. Usata come FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
