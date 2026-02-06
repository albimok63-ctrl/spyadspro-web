"""
Alembic env.py: usa la Base ORM e l'engine/URL dell'applicazione.
Importa tutti i modelli ORM per autogenerate. SQLAlchemy 2.x.
"""

import sys
from pathlib import Path

# Aggiunge la root del progetto al path (come prepend_sys_path = .)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import Settings
from app.db.base import Base

# Import esplicito modelli ORM: registrano le tabelle su Base.metadata (obbligatorio per autogenerate)
from app.db.models import api_key_orm  # noqa: F401
from app.db.models import api_usage_orm  # noqa: F401
from app.db.models import item_orm  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """URL del DB dall'applicazione (config/env)."""
    return Settings().database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (solo SQL, senza connessione)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connessione all'engine esistente)."""
    url = get_url()
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(url, connect_args=connect_args)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
