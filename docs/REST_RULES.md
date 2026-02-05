# Regole REST adottate – SpyAdsPro-Web

Regole obbligatorie e non negoziabili per coerenza, manutenibilità e scalabilità in architettura a microservizi.

---

## 1. Endpoint basati su risorse (nomi, non verbi)

- Gli URL identificano **risorse** (sostantivi), non azioni.
- **Vietato:** `/getItems`, `/createItem`. **Corretto:** `GET /items`, `POST /items`.

## 2. Nomi al plurale

- Collezioni e risorse collezione: sempre **plurale**.
- **Esempi:** `/items`, `/users`, `/orders`.

## 3. Metodi HTTP corretti

| Metodo  | Uso                | Idempotente |
|---------|--------------------|-------------|
| **GET** | Lettura            | Sì          |
| **POST**| Creazione          | No          |
| **PUT** | Sostituzione totale| Sì          |
| **PATCH** | Update parziale  | No          |
| **DELETE** | Rimozione       | Sì          |

## 4. API stateless

- Nessuno stato di sessione sul server tra una richiesta e l’altra.
- Ogni richiesta è autosufficiente (auth via header/token se necessario).

## 5. JSON come formato standard

- Request body e response body: **JSON**.
- Header: `Content-Type: application/json`, `Accept: application/json`.

## 6. Status code corretti

| Code | Significato        | Uso tipico                    |
|------|--------------------|--------------------------------|
| **200** | OK               | GET con body (lista o singolo) |
| **201** | Created         | POST creazione risorsa         |
| **204** | No Content      | DELETE (successo, nessun body) |
| **400** | Bad Request     | Dati invalidi (validazione)    |
| **404** | Not Found       | Risorsa inesistente            |
| **422** | Unprocessable Entity | Payload/parametri non validi |
| **500** | Internal Server Error | Errore server             |

## 7. Error handling esplicito e consistente

- Risposte di errore sempre in **JSON**.
- Struttura minima: `{"detail": "<messaggio>"}`.
- Il **Service** solleva eccezioni di dominio (es. `ItemNotFoundError`).
- Il **Router** (o exception handler in `main`) traduce in `HTTPException` / JSONResponse con status code appropriato.

## 8. Versioning via URL

- Tutte le API pubbliche sotto **`/api/v1`** (e future `v2` se necessario).
- **Esempio:** `GET /api/v1/items`, `POST /api/v1/items`.

---

## Applicazione su Items (REST-compliant)

| Metodo | Endpoint | Comportamento | Status |
|--------|----------|---------------|--------|
| **POST** | `/api/v1/items` | Crea un item; body: `name`, `description` | 201 Created |
| **GET** | `/api/v1/items` | Lista di tutti gli item | 200 OK |
| **GET** | `/api/v1/items/{item_id}` | Singolo item se esiste | 200 OK / 404 Not Found |
| **DELETE** | `/api/v1/items/{item_id}` | Rimuove l’item se esiste | 204 No Content / 404 Not Found |

- `item_id` non valido (es. ≤ 0): **422** Unprocessable Entity.
- Body non valido (es. `name` vuoto): **422** Unprocessable Entity.
