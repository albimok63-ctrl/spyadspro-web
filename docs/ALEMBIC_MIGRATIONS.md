# Linee guida migrazioni DB (Alembic)

Il database è sotto controllo versione tramite Alembic. Lo schema evolve solo tramite migrazioni versionate.

---

## 1. Quando creare una migrazione

- **Ogni modifica allo schema**: nuove tabelle, colonne, indici, vincoli, rinominazioni.
- **Dopo aver modificato i modelli ORM** in `app/models/item_orm.py` o in `app/db/models/`: generare una migrazione che rifletta le differenze.
- **Non** creare migrazioni per modifiche solo di logica (repository, service, API) senza cambi allo schema.

---

## 2. Come versionare le migrazioni

- **Naming file**: `alembic/versions/NNN_descrizione_breve.py` (es. `002_add_items_updated_at.py`).
- **Revision ID**: lasciare che Alembic generi l’hash (autogenerate) oppure usare ID brevi sequenziali (es. `001`, `002`) se già in uso.
- **Messaggio**: descrittivo e in inglese o italiano, es. `add items updated_at column`, `create users table`.
- **Una modifica logica per migrazione**: una migrazione = un passo di schema ben definito, per rollback e review più semplici.

---

## 3. Workflow locale

```bash
# 1. Modificare i modelli ORM (app/models/item_orm.py o app/db/models/)

# 2. Generare la migrazione (rileva le differenze con il DB)
alembic revision --autogenerate -m "descrizione modifica"

# 3. Controllare il file generato in alembic/versions/ (correggere se necessario)

# 4. Applicare la migrazione
alembic upgrade head

# 5. Verificare
alembic current
pytest -q
```

---

## 4. Applicazione in produzione

- **Prima del deploy**: applicare le migrazioni sul DB di produzione (o in uno step dedicato subito dopo il deploy).
- **Comando**: `alembic upgrade head` (con env/config che punta al DB di produzione).
- **Backup**: fare backup del DB prima di `upgrade head` in produzione.
- **Rollback**: in caso di problemi usare `alembic downgrade -1` (o la revisione desiderata); verificare che il downgrade sia testato in staging.
- **Non** eseguire migrazioni in parallelo su più istanze senza coordinamento; preferire un singolo processo di migrazione (job o istanza dedicata).

---

## 5. Comandi rapidi

| Comando | Descrizione |
|--------|-------------|
| `alembic current` | Revisione attuale del DB |
| `alembic history` | Cronologia migrazioni |
| `alembic upgrade head` | Applica tutte le migrazioni pendenti |
| `alembic downgrade -1` | Torna indietro di una revisione |
| `alembic downgrade base` | Rimuove tutte le migrazioni (schema vuoto) |
| `alembic revision --autogenerate -m "msg"` | Genera una nuova migrazione da diff ORM/DB |

---

## 6. Regole da rispettare

- **Un solo storico**: un solo ramo di migrazioni (no branch multipli in produzione).
- **Idempotenza**: dove possibile (es. SQLite) usare `CREATE TABLE IF NOT EXISTS` / `DROP TABLE IF EXISTS` per migrazioni baseline o riparazioni.
- **Test**: dopo aver creato o modificato una migrazione, eseguire `alembic upgrade head` e `pytest -q` prima del commit.
- **Nessuna logica in migrazione**: solo DDL (e Dati di riferimento se necessario); niente logica applicativa.
- **Base e URL**: Alembic usa la `Base` e l’URL definiti in `app` (vedi `alembic/env.py`); non duplicare engine o modelli.

---

## 7. Verifica stato progetto

- **Test**: `pytest -q` deve passare (i test usano un DB in-memory dedicato; il DB “reale” resta sotto Alembic).
- **Revisione**: `alembic current` deve mostrare l’ultima revisione applicata (es. `001 (head)`).
- **DB sotto controllo**: la tabella `alembic_version` traccia la revisione applicata; ogni modifica allo schema avviene tramite migrazioni.

Alembic è configurato e pronto per le evoluzioni future dello schema.
