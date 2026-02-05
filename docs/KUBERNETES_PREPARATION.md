# Preparazione al deploy Kubernetes

Questo documento allinea l’architettura attuale (Docker / Docker Compose) ai concetti Kubernetes **senza introdurre manifest o codice runtime**. Solo analisi e mappatura concettuale, in modo che in futuro il deploy su Kubernetes richieda **zero refactor** dell’applicazione.

---

## 1. Mappatura concettuale Docker Compose → Kubernetes

### 1.1 Immagine Docker API → Pod

| Oggi (Docker) | Futuro (Kubernetes) | Note |
|---------------|---------------------|------|
| Immagine buildata da `Dockerfile` (API FastAPI) | **Pod** esegue uno o più container; qui: un container per Pod (API) | Un Pod = unità di deploy minima. L’immagine attuale è già adatta: singolo processo (`uvicorn`), `EXPOSE 8000`, binding `0.0.0.0`. |
| `docker run` (o servizio `api` in Compose) | Il Pod viene gestito da un **Deployment** (repliche, rollout, rollback). | Nessun cambiamento al Dockerfile: stessa immagine usabile nel Pod. |

**Già pronto**: immagine single-process, no PID 1 custom, no binding a localhost interno. Il Pod eseguirà lo stesso `CMD` del Dockerfile.

---

### 1.2 Servizio docker-compose → Service (e Deployment)

| Oggi (Compose) | Futuro (Kubernetes) | Note |
|----------------|--------------------|------|
| Servizio `api` (rete `backend`, porta 8000) | **Service** (ClusterIP o LoadBalancer) espone i Pod dell’API su una porta stabile; **Deployment** gestisce i Pod (repliche, template). | Service discovery: in K8s si usa il nome del Service (es. `api`) come hostname; già oggi l’API usa nomi servizio (`REDIS_HOST=redis`), non IP. |
| Servizio `redis` (rete `backend`, porta 6379) | **Service** per Redis; eventuale **Deployment** o StatefulSet a seconda del modello di dati. | Stesso principio: risoluzione per nome. |
| `docker compose up --scale api=2` | **Deployment** con `replicas: 2` (o superiore). Il Service bilancia il traffico tra i Pod. | API già stateless e senza `container_name` fissi; scaling è solo configurazione. |

**Già pronto**: comunicazione solo per nome servizio (redis, api); nessun IP hardcoded. Il Service K8s fornirà lo stesso pattern (nome DNS interno).

---

### 1.3 `.env` → ConfigMap e Secret

| Oggi (Compose) | Futuro (Kubernetes) | Note |
|----------------|--------------------|------|
| File `.env` + `env_file: .env` e `environment:` in `docker-compose.yml` | **ConfigMap** per configurazione non sensibile (es. `APP_ENV`, `REDIS_HOST`, `REDIS_PORT`, `version`). **Secret** per dati sensibili (se presenti: password DB, token, ecc.). | L’app legge tutto da variabili d’ambiente (Pydantic `Settings` da `os.getenv` / `.env`). In K8s si iniettano le stesse variabili da ConfigMap/Secret nel Pod. |
| `Settings` in `app/core/config.py` | Stessi nomi di variabili: `REDIS_HOST`, `REDIS_PORT`, `DATABASE_URL`, `CACHE_ENABLED`, ecc. | Nessun refactor: l’app continua a leggere da env; solo la *sorgente* delle env cambia (ConfigMap/Secret invece di file `.env`). |

**Variabili attuali** (da `.env.example` e config):

- **ConfigMap (candidati)**: `APP_ENV`, `REDIS_HOST`, `REDIS_PORT`, `cache_enabled` (se esposto come env), `version` / `app_name` (se usati da config).
- **Secret (quando serviranno)**: eventuali `DATABASE_URL` con password, token API, chiavi crittografiche. Oggi con SQLite locale non ci sono secret; per un DB remoto si userà Secret.

**Già pronto**: single source of truth in env (`Settings`); nessuna lettura diretta di file di config da path fissi. Zero refactor per passare a ConfigMap/Secret.

---

### 1.4 Healthcheck Compose → liveness e readiness

| Oggi (Compose) | Futuro (Kubernetes) | Note |
|----------------|--------------------|------|
| `healthcheck` API: `curl -f http://127.0.0.1:8000/api/v1/health` (interval 10s, timeout 5s, retries 3, start_period 15s) | **livenessProbe**: stesso comando (o HTTP GET su `http://:8000/api/v1/health`). Se fallisce, K8s riavvia il container. **readinessProbe**: stesso endpoint; se fallisce, il Pod esce dal load balancing fino a ritorno healthy. | Un solo endpoint `/api/v1/health` può servire sia liveness che readiness (processo up e in grado di rispondere). |
| `healthcheck` Redis: `redis-cli ping` | **livenessProbe** (e opzionalmente readiness) per il container Redis. | Stessa semantica: processo risponde al PING. |

**Scelta consigliata** (senza toccare codice):

- **liveness**: HTTP GET `http://:8000/api/v1/health` (o comando curl equivalente nel container). Failure → restart del container.
- **readiness**: stesso endpoint. Failure → Pod non riceve traffico dal Service finché non torna healthy.
- **startupProbe** (opzionale): stesso endpoint con failureThreshold alto, per dare tempo all’app di avviarsi (equivalente a `start_period` in Docker).

**Già pronto**: endpoint GET `/api/v1/health` stabile, senza dipendenza da Redis (graceful degradation documentata in `DOCKER_FAILURE_BEHAVIOR.md`). Nessun refactor per esporre probe K8s.

---

## 2. Cosa è già pronto (zero refactor necessario)

### 2.1 API stateless

- **Nessuno stato in memoria condiviso** tra richieste: ogni request usa una sessione DB e un client cache iniettati; nessun dato globale mutabile.
- **Nessuna dipendenza da file locali** per stato applicativo: persistenza su DB (e cache Redis opzionale). In Compose il file SQLite è condiviso via volume; in K8s si userà un DB remoto o uno storage condiviso a seconda della scelta architetturale.
- **Service discovery per nome**: `REDIS_HOST=redis` (nome servizio); in K8s il Service `redis` fornirà lo stesso nome DNS.
- **Binding di rete**: l’app ascolta su `0.0.0.0:8000`; adatta a qualsiasi rete del Pod.

Quindi l’applicazione è **già stateless** e adatta a Deployment con più repliche; nessun codice da modificare per Kubernetes.

---

### 2.2 Health endpoint

- **GET /api/v1/health** ritorna 200 con payload strutturato (es. `status`, `version`).
- **Non dipende da Redis**: l’endpoint non verifica Redis; in caso di Redis down l’API resta healthy (degradazione cache, vedi `DOCKER_FAILURE_BEHAVIOR.md`).
- **Adatto a liveness e readiness**: segnala che il processo è up e in grado di servire richieste.

Nessun nuovo endpoint da aggiungere; le probe K8s useranno questo percorso.

---

### 2.3 Migrazioni DB “safe” per Kubernetes

- **Alembic** gestisce lo schema in modo versionato; vedi `docs/ALEMBIC_MIGRATIONS.md`.
- **Un solo processo di migrazione**: in produzione si applica `alembic upgrade head` in un singolo contesto (job pre-deploy o init container), non in parallelo su N repliche. Questa pratica è già documentata e compatibile con K8s (Job o step di pipeline).
- **Migrazioni idempotenti** dove possibile (es. baseline con `CREATE TABLE IF NOT EXISTS`); rollback con `alembic downgrade`.
- **Nessuna logica applicativa nelle migrazioni**: solo DDL; nessun side-effect che dipenda dall’istanza.

Per Kubernetes: le migrazioni si eseguiranno **prima** del rollout dei Pod (o in un Job dedicato); i Pod dell’API non devono eseguire migrazioni in concorrenza. Zero refactor del codice applicativo; solo definizione del momento in cui si lancia `alembic upgrade head` (CI/CD o Job K8s).

---

## 3. Riepilogo mappatura

| Concetto Docker / Compose | Concetto Kubernetes | Stato |
|--------------------------|---------------------|--------|
| Immagine API (Dockerfile) | Container nel Pod (stessa immagine) | Pronto |
| Servizio `api` (rete, porta) | Deployment + Service (ClusterIP/LoadBalancer) | Solo manifest da aggiungere |
| Servizio `redis` | Service (+ Deployment/StatefulSet) | Solo manifest da aggiungere |
| `.env` / `environment` | ConfigMap + Secret (stesse variabili) | Pronto (solo definizione risorse) |
| `healthcheck` API | livenessProbe + readinessProbe (GET /api/v1/health) | Pronto |
| `healthcheck` Redis | livenessProbe (redis-cli ping) | Pronto |
| Scalabilità (`--scale api=2`) | `replicas` nel Deployment | Pronto |
| Restart su crash | restartPolicy + liveness in K8s | Comportamento già allineato |

---

## 4. Cosa non fare ora (vincoli rispettati)

- **NON** creare manifest Kubernetes (YAML) in questo progetto.
- **NON** introdurre codice runtime che dipenda da Kubernetes (API, env specifici K8s, ecc.).
- **SOLO** analisi e preparazione documentale.

Quando si deciderà il deploy su Kubernetes, basterà:

1. Definire Deployment e Service per API e Redis (e eventuale DB gestito).
2. Definire ConfigMap e Secret con le stesse variabili d’ambiente usate oggi.
3. Configurare liveness/readiness (e opzionalmente startup) puntando a `/api/v1/health` e a `redis-cli ping`.
4. Eseguire le migrazioni Alembic in un Job o step di pipeline prima del rollout.

**Zero refactor** dell’applicazione: l’architettura attuale è già allineata a Pod, Service, Deployment, ConfigMap, Secret e probe di salute.
