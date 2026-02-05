"""
Modulo per background task. Funzioni eseguibili dopo la response HTTP (non bloccanti).
Compatibile con FastAPI BackgroundTasks. Nessuna logica di dominio.
"""

import asyncio

from app.core.logging import get_logger

logger = get_logger("app")


async def async_task_stub() -> None:
    """
    Task async di esempio. Nessuna logica di dominio reale.
    Utilizzabile come riferimento per future coroutine.
    """
    await asyncio.sleep(0)


def on_item_created(item_id: int, name: str) -> None:
    """
    Background task: eseguito dopo l'invio della response (es. log, warmup cache).
    Non blocca la risposta HTTP. Nessuna logica di business.
    """
    logger.info("Background: item created id=%s name=%s", item_id, name)
