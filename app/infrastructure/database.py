"""
Configurazione database SQLite – solo infrastruttura, nessuna logica business.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


SQLITE_URL = "sqlite:///./data/spyadspro.db"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Fornisce una sessione DB; chiude in finally."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
