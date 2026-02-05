# Comportamento in caso di failure (Docker Compose)

Questo documento rende esplicito come lo stack reagisce al fallimento di un servizio, applicando **self-healing** e **graceful degradation**. Redis resta **opzionale**: l’API non dipende dal suo avvio né dalla sua disponibilità continua.

---

## 1. API parte anche se Redis è down

- In **docker-compose.yml** il servizio `api` **non** ha `depends_on` su `redis`.
- L’avvio dell’API non è bloccato dall’assenza o dall’indisponibilità di Redis.
- Comportamento:
  - All’avvio, il client Redis (in-app) tenta la connessione; in caso di fallimento imposta `_client = None` e `_enabled = False` senza sollevare eccezioni.
  - La cache viene considerata non disponibile (`is_available` false): tutte le operazioni di cache sono no-op (get → None, set/delete → ignorati). Le richieste sono servite leggendo/scrivendo solo dal DB.
- **Verifica**: avviare solo l’API (es. `docker compose up api` con Redis spento o commentato) e chiamare `GET /api/v1/health` e `GET /api/v1/items` → risposte 200 senza errori.

---

## 2. API non crasha se Redis cade a runtime

- Il codice applicativo tratta Redis come **degradabile**:
  - **RedisCacheClient**: in `get`, `set`, `delete` ogni chiamata a Redis è in `try/except`; in caso di errore restituisce `None` o ignora (no raise verso il chiamante).
  - **ItemRepository**: prima di usare la cache verifica `if self._cache and self._cache.is_available`; le operazioni di cache sono già protette da try/except nel client.
- Se Redis diventa irraggiungibile dopo l’avvio (contenitore spento, rete, ecc.):
  - Le successive chiamate Redis (get/set/delete) possono fallire; le eccezioni sono catturate nel client e non propagano all’API.
  - L’API continua a rispondere usando il DB; la cache va in **graceful degradation** (solo miss, nessun crash).
- **Nessuna modifica alla logica applicativa**: il comportamento è già garantito dal codice esistente.

---

## 3. Docker restart policy gestisce i crash

- Entrambi i servizi hanno **`restart: unless-stopped`**:
  - Se un processo **crasha** (exit code non zero), Docker riavvia il container.
  - L’unica eccezione è se il container è stato fermato manualmente con `docker compose stop` (o equivalente); in quel caso non viene riavviato finché non si fa `docker compose start` o `up`.
- **API**: crash del processo uvicorn → restart automatico; le richieste in corso possono fallire, i client possono ritentare.
- **Redis**: crash del processo Redis → restart automatico; durante l’indisponibilità l’API degrada come al punto 2 (nessun crash, risposta da DB).

---

## 4. Healthcheck segnala stato reale

- **API**  
  - Comando: `curl -f http://127.0.0.1:8000/api/v1/health`  
  - Significato: il container è considerato **healthy** se il processo risponde con HTTP 200 su `/api/v1/health`.  
  - L’endpoint non dipende da Redis (usa solo HealthRepository/config); quindi “healthy” = processo up e in grado di servire richieste. Lo stato di Redis (up/down) **non** cambia l’esito del healthcheck: l’API può essere healthy anche con Redis down (degradazione cache).

- **Redis**  
  - Comando: `redis-cli ping`  
  - Significato: il container Redis è **healthy** se risponde al PING.  
  - Usabile da altri servizi con `depends_on: redis: condition: service_healthy` se in futuro si volesse un servizio che deve avere Redis disponibile all’avvio.

In sintesi: i healthcheck riflettono lo stato **reale** del singolo servizio (processo API risponde, processo Redis risponde al PING), senza mescolare con la disponibilità degli altri componenti.

---

## Riepilogo

| Scenario | Comportamento |
|----------|----------------|
| Redis down all’avvio | API parte ugualmente; cache non usata, risposta da DB. |
| Redis cade a runtime | API non crasha; cache in degradazione, risposta da DB. |
| Crash processo API | Docker riavvia il container (restart: unless-stopped). |
| Crash processo Redis | Docker riavvia Redis; API continua a rispondere senza cache. |
| Healthcheck API | Healthy = processo up e GET /api/v1/health 200 (indipendente da Redis). |
| Healthcheck Redis | Healthy = redis-cli ping OK. |

Lo stack è **resiliente** e la **failure** è gestita con restart automatico e degradazione graceful della cache, senza cambiare la logica applicativa e mantenendo Redis opzionale.
