# Versioning REST API – SpyAdsPro-Web

Regola architetturale ufficiale: tutte le API pubbliche sono versionate tramite URL. Nessun endpoint fuori versione.

---

## 1. Versioning adottato

- **Tipo:** versioning tramite **URL** (non header).
- **Prefix attuale:** `/api/v1`.
- **Stato di v1:** considerata **stabile**; gli endpoint sotto `/api/v1` non subiscono breaking change senza una nuova versione (es. v2).

**Regole obbligatorie:**

| Regola | Descrizione |
|--------|-------------|
| Tutti gli endpoint sotto versione | Ogni route pubblica deve essere sotto `/api/v1` (o future `/api/v2`). |
| Nessun endpoint fuori versione | Non esistono route API tipo `/health` o `/items` senza prefisso di versione. |
| Un solo punto di configurazione | Il prefix è definito in `main.py` come `API_V1_PREFIX` e usato per tutti i router. |

**Endpoint attuali (v1):**

- `GET  /api/v1/health`
- `POST /api/v1/items`
- `GET  /api/v1/items`
- `GET  /api/v1/items/{item_id}`
- `DELETE /api/v1/items/{item_id}`

---

## 2. Implementazione in main.py

- Costante **`API_V1_PREFIX = "/api/v1"** in `app/main.py`.
- Ogni `include_router(..., prefix=API_V1_PREFIX)` per i router di v1.
- Nessun router incluso senza prefix (nessuna route “nuda” a livello app).

La struttura è già pronta per future versioni: si potranno aggiungere `app.api.v2` e `API_V2_PREFIX` senza toccare v1.

---

## 3. Linee guida per future versioni (es. v2)

Quando servirà una nuova versione API (breaking change o evoluzione controllata):

1. **Non modificare v1:** i router in `app.api.v1` e i relativi service/repository restano invariati per gli endpoint esistenti.
2. **Nuovo package:** creare `app.api.v2` (e relativi moduli, es. `health.py`, `items.py`) invece di modificare i file v1.
3. **Nuovo prefix in main:** definire `API_V2_PREFIX = "/api/v2"` e registrare i router v2 con `app.include_router(..., prefix=API_V2_PREFIX)`.
4. **Riuso logica:** i **service** e i **repository** possono essere riusati da v2; solo i router (e eventuali DTO/schema) sono specifici per versione. Evitare duplicazione di business logic.
5. **Deprecation (opzionale):** per deprecare v1, aggiungere header di risposta (es. `X-API-Deprecated: true`) o documentazione, senza rimuovere v1 finché i client non siano migrati.

In questo modo il versioning resta URL-based, esplicito in `main.py`, e senza breaking change su v1.
