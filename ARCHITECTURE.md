# Albero architetturale – Microservizio FastAPI

## 1) Albero architetturale completo

```
app/
  main.py                    # Bootstrap applicazione (solo wiring)
  __init__.py
  api/
    __init__.py
    v1/
      __init__.py
      health.py              # SOLO routing + response model
  services/
    __init__.py
    health_service.py        # SOLO business logic
  repositories/
    __init__.py
    health_repository.py     # SOLO accesso dati (anche mock)
  core/
    __init__.py
    config.py                # Settings, env, config
    dependencies.py          # Dependency injection
tests/
  conftest.py                # Fixture pytest (app, client)
  test_api_health.py         # Test endpoint (no business logic)
  test_service_health.py     # Test service puro
```

*(I file `__init__.py` sono minimi per permettere i package Python; non contengono logica.)*

---

## 2) Ruolo di ogni cartella

| Cartella       | Responsabilità unica | Divieti |
|----------------|----------------------|--------|
| **app/**       | Radice applicazione  | Nessuna logica in `main.py`, solo wiring |
| **app/api/**   | Strato HTTP          | Nessuna logica business; solo routing e modelli di risposta |
| **app/api/v1/**| API versionata       | Come `api/` |
| **app/services/** | Logica di business | Non conosce FastAPI/HTTP; dipende solo da repository/core |
| **app/repositories/** | Accesso dati      | Non conosce HTTP; ritorna dati puri |
| **app/core/**  | Configurazione e DI  | Solo config, env e factory per iniezione dipendenze |
| **tests/**     | Test                 | API via TestClient; service con mock; nessun server reale |

Flusso dipendenze (sempre rispettato):

```
api → services → repositories
(mai repositories → services → api)
```

---

## 3–4) Codice

Vedi file sotto `app/` e `tests/`.

---

## 5) Comandi per eseguire app e test

**Dipendenze (da project root, con venv attivo):**

```bash
pip install -r requirements.txt
```

**Avvio applicazione:**

```bash
uvicorn app.main:app --reload
```

Endpoint: `GET http://127.0.0.1:8000/api/v1/health`

**Esecuzione test (nessun server reale):**

Da project root (`c:\Users\albim\spyadspro-web`), con venv attivo:

```bash
python -m pytest tests/ -v
```
