"""
Items API – REST best practices. Solo nomi di risorse (/items), metodi HTTP corretti, status code REST.
Response model espliciti; 404 quando la risorsa non esiste. API stateless, versioning /api/v1.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.core.dependencies import get_item_service
from app.core.security import get_current_user
from app.models.item import ItemCreate, ItemRead
from app.services.item_service import ItemService
from app.tasks.background import on_item_created


router = APIRouter(prefix="/items", tags=["items"])

# Documentazione OpenAPI per risposte di errore (Swagger)
RESPONSE_404 = {"description": "Risorsa non trovata", "content": {"application/json": {"example": {"detail": "Item 1 not found"}}}}
RESPONSE_422 = {"description": "Parametri non validi", "content": {"application/json": {"example": {"detail": "item_id must be a positive integer"}}}}


def _require_positive_item_id(item_id: int) -> int:
    """Path validation: item_id must be positive. Router layer only."""
    if item_id <= 0:
        raise HTTPException(status_code=422, detail="item_id must be a positive integer")
    return item_id


# --- POST /api/v1/items → 201 Created ---
@router.post(
    "",
    response_model=ItemRead,
    status_code=201,
    responses={422: RESPONSE_422},
)
def create_item(
    body: ItemCreate,
    background_tasks: BackgroundTasks,
    service: ItemService = Depends(get_item_service),
    _user_id: str = Depends(get_current_user),
) -> ItemRead:
    """Crea un item. Body: name (obbligatorio), description. Restituisce l'item creato con id."""
    created = service.create_item(name=body.name, description=body.description)
    background_tasks.add_task(on_item_created, created.id, created.name)
    return ItemRead(id=created.id, name=created.name, description=created.description)


# --- GET /api/v1/items → 200 OK ---
@router.get(
    "",
    response_model=list[ItemRead],
    responses={200: {"description": "Lista di item"}},
)
def list_items(
    service: ItemService = Depends(get_item_service),
    _user_id: str = Depends(get_current_user),
) -> list[ItemRead]:
    """Elenco di tutti gli item."""
    items = service.get_all_items()
    return [ItemRead(id=i.id, name=i.name, description=i.description) for i in items]


# --- GET /api/v1/items/{id} → 200 OK / 404 Not Found ---
@router.get(
    "/{item_id}",
    response_model=ItemRead,
    responses={404: RESPONSE_404, 422: RESPONSE_422},
)
def get_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
    _user_id: str = Depends(get_current_user),
) -> ItemRead:
    """Restituisce un item per id. 404 se la risorsa non esiste."""
    _require_positive_item_id(item_id)
    found = service.get_item_by_id(item_id)
    return ItemRead(id=found.id, name=found.name, description=found.description)


# --- DELETE /api/v1/items/{id} → 204 No Content / 404 Not Found ---
@router.delete(
    "/{item_id}",
    status_code=204,
    responses={404: RESPONSE_404, 422: RESPONSE_422},
)
def delete_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
    _user_id: str = Depends(get_current_user),
) -> None:
    """Rimuove l'item. 204 se rimosso; 404 se la risorsa non esiste."""
    _require_positive_item_id(item_id)
    service.delete_item(item_id)
