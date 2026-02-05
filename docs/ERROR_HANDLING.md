# Strategia di error handling REST – SpyAdsPro-Web

Gestione degli errori standardizzata per tutti i microservizi: coerenza, risposte sempre in JSON, nessuna logica HTTP nel Service.

---

## 1. Principi

- **Gli errori di dominio nascono nel Service:** il Service solleva `ValueError` o eccezioni custom di dominio (da `app.core.exceptions`). Non importa FastAPI.
- **I Router non gestiscono le eccezioni:** nessun try/except nel router; le eccezioni sono tradotte in HTTP dai **handler globali** in `main.py`.
- **Risposte di errore sempre in JSON:** formato standard `{"detail": "<messaggio>"}`.

---

## 2. Mappatura status code

| Status | Significato           | Quando |
|--------|------------------------|--------|
| **400** | Bad Request           | `ValueError` sollevata dal Service (input non valido a livello dominio). |
| **404** | Not Found            | Risorsa inesistente (es. `ItemNotFoundError`). |
| **409** | Conflict             | Conflitto (es. duplicati) – `ConflictError`. |
| **422** | Unprocessable Entity | Validazione request (path/body) – gestita da FastAPI/Pydantic o da `HTTPException` nel router. |
| **500** | Internal Server Error| Qualsiasi altra eccezione non gestita. |

---

## 3. Eccezioni di dominio (core)

Definite in **`app/core/exceptions.py`** (nessun import FastAPI):

| Eccezione            | Base        | Uso              | HTTP |
|----------------------|------------|------------------|------|
| `DomainError`        | `Exception`| Base per dominio | -    |
| `NotFoundError`      | `DomainError` | Risorsa non trovata (base) | 404 |
| `ItemNotFoundError`  | `NotFoundError` | Item inesistente | 404 |
| `ConflictError`      | `DomainError` | Conflitto (duplicati, ecc.) | 409 |

I Service importano da `app.core.exceptions` e sollevano queste eccezioni; **non** usano `HTTPException` né FastAPI.

---

## 4. Handler globali (main.py)

Registrati su `FastAPI` in `create_app()`:

1. **ItemNotFoundError** → `JSONResponse(404, {"detail": str(exc)})`
2. **ConflictError** → `JSONResponse(409, {"detail": str(exc)})`
3. **ValueError** → `JSONResponse(400, {"detail": str(exc)})`
4. **Exception** → `JSONResponse(500, {"detail": "Internal server error"})`

L’ordine è rilevante: handler più specifici prima, generico (`Exception`) per ultimo. Le risposte sono sempre JSON con chiave `detail`.

---

## 5. Applicazione al microservizio Items

- **ItemService** solleva `ItemNotFoundError` (da `app.core.exceptions`) in `get_item_by_id` e `delete_item` se l’item non esiste. Non fa try/except né importa FastAPI.
- **Router Items** non cattura eccezioni: delega al service; il 404 è gestito dall’handler globale. La validazione path (`item_id <= 0`) resta nel router con `HTTPException(422)` (bordo HTTP).
- **422** per body/path non validi resta di competenza di FastAPI e del router; **404** e **500** sono gestiti dagli handler globali.

---

## 6. Architettura non violata

- **Router:** solo HTTP (request/response, validazione bordo); nessuna logica di business, nessun try/except per eccezioni di dominio.
- **Service:** logica pura; solleva solo `ValueError` o eccezioni da `app.core.exceptions`; nessun import FastAPI.
- **Repository:** nessun cambiamento; non solleva eccezioni HTTP.
- **Core:** `exceptions.py` contiene solo tipi di eccezione; nessuna logica applicativa.

Flusso: **Service (raise DomainError) → propagazione → main (exception handler) → JSONResponse**.
