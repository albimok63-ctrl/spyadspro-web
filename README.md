## Docker Ready

Questo microservizio FastAPI è pronto per essere eseguito in container Docker.

---

## Observability

L’API espone un endpoint **GET /metrics** (root, non versionato) in formato Prometheus, tramite [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator). Nessuna autenticazione.

### Verificare le metriche con curl

Con l’app in esecuzione (locale o in container):

```bash
curl -s http://localhost:8000/metrics
```

Risposta attesa: **HTTP 200** e body in testo piano con metriche (es. `http_requests_total`, `http_request_duration_seconds`, `health_checks_total`).

Dopo aver chiamato un endpoint API (es. health), le metriche si aggiornano:

```bash
curl -s http://localhost:8000/api/v1/health
curl -s http://localhost:8000/metrics
```

In `/metrics` compariranno le richieste a `/api/v1/health` (label `handler`, `method`, ecc.). Compatibile con scraping Prometheus e con Grafana (configurando Prometheus come datasource).
