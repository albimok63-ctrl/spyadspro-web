"""
Eccezioni di dominio – solo tipi, nessuna logica.
I Service sollevano queste eccezioni; i Router/exception handler le mappano in HTTP.
Nessun import FastAPI o HTTP in questo modulo.
"""


class DomainError(Exception):
    """Base per tutte le eccezioni di dominio. Mappata a 4xx/5xx dall'API."""

    pass


class NotFoundError(DomainError):
    """Risorsa non trovata. API → 404 Not Found."""

    pass


class ItemNotFoundError(NotFoundError):
    """Item non trovato. Sollevata dal ItemService."""

    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")


class ConflictError(DomainError):
    """Conflitto (es. duplicato). API → 409 Conflict."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
