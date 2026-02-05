# Docker Build

Per buildare l'immagine:

```bash
docker build -t spyadspro-web .
```

Per avviare il container:

```bash
docker run -p 8000:8000 spyadspro-web
```

Per l'orchestrazione con Compose (API + Redis, failure e self-healing):

- `docker compose up -d` — avvio stack
- Vedi **docs/DOCKER_FAILURE_BEHAVIOR.md** per comportamento in caso di failure (Redis opzionale, restart policy, healthcheck).
- Vedi **docs/KUBERNETES_PREPARATION.md** per la mappatura concettuale verso un futuro deploy Kubernetes (Pod, Service, ConfigMap, Secret, liveness/readiness).
