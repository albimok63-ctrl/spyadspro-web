# Items: esempio didattico vs versione production-ready

## Differenze principali

### 1. Stato condiviso nel router (VIETATO)

| Didattico (anti-pattern) | Production-ready |
|---------------------------|-------------------|
| Lista o dict a livello modulo nel file del router, es. `_items: list[Item] = []` | **Nessuna variabile globale né stato nel router.** Lo stato vive solo nel **Repository**, iniettato via DI. Il router non conosce né possiede dati. |
| Il router legge/scrive direttamente la lista | Il router chiama solo `service.create_item(...)`, `service.get_all_items()`, `service.get_item_by_id(id)` e restituisce il risultato. |

### 2. Logica mischiata (VIETATO)

| Didattico (anti-pattern) | Production-ready |
|---------------------------|-------------------|
| Nel router: generazione id, controlli “esiste già?”, formattazione risposta | **Router:** solo HTTP (request → dependency → response). Nessuna logica di business. |
| Nel router: `if not found: raise HTTPException(404)` dopo aver “cercato” in una lista | **Service:** contiene tutta la logica (creazione, recupero, “non trovato”). Solleva `ItemNotFoundError`. |
| Repository assente o usato dal router | **Repository:** unico strato che accede ai dati (in-memory o DB). Solo il **Service** usa il Repository; il Router non lo vede. |

### 3. Assenza di test (VIETATO)

| Didattico (anti-pattern) | Production-ready |
|---------------------------|-------------------|
| Nessun test o solo test manuali | **Test-first:** `test_items_api.py` (TestClient, nessun server reale) e `test_item_service.py` (unit test sul service con repository isolato). |
| Test che dipendono da stato globale o ordine di esecuzione | Test **deterministici:** ogni test service usa un `ItemRepository()` dedicato (fixture); nessuna lista in router da “pulire”. |

### 4. Vincoli rispettati in production-ready

- **Nessuna variabile globale:** configurazione e stato solo in `core` (config, DI) e nel repository iniettato.
- **Nessuna lista nel router:** il router non dichiara né modifica liste; riceve dati dal service e li restituisce come response.
- **Service e Repository separati:** Repository = persistenza; Service = regole di business; Router = HTTP.
- **Test-first:** API e Service coperti da test; refactoring sicuro.

---

## Flusso production-ready

```
Client HTTP
    → Router (api/v1/items.py)     [solo routing + validazione path/body]
    → Service (item_service.py)   [logica: create, get_all, get_by_id + ItemNotFoundError]
    → Repository (item_repository.py) [persistenza: add, get_all, get_by_id]
    → Model (models/item.py)      [ItemModel, ItemCreate]
```

- **404:** il Service solleva `ItemNotFoundError`; l’app converte in 404 tramite **exception handler** (nessun try/except nel router).
- **422:** path/body non validi (es. `item_id <= 0`, `name` vuoto) gestiti da FastAPI o da validazione esplicita al bordo.
