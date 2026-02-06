"""
Inizializzazione schema database. Crea tutte le tabelle registrate su Base.
Import esplicito modelli ORM obbligatorio per registrazione in Base.metadata.
"""

from app.db.base import Base
from app.db.session import engine

# Import esplicito modelli ORM (obbligatorio: registra le tabelle su Base.metadata)
from app.models import api_key_orm  # noqa: F401
from app.models import api_usage_orm  # noqa: F401
from app.models import item_orm  # noqa: F401

def init_db() -> None:
    """Crea le tabelle (es. items) sul DB collegato a engine."""
    Base.metadata.create_all(bind=engine)
