# unijobs-backend

## Local Run With YDB

Backend can be started locally with YDB in Docker Compose:

```bash
docker compose up --build
```

Services:

- Backend API: `http://localhost:8000/api`
- Health check: `http://localhost:8000/api/healthz`
- YDB gRPC: `localhost:2136`
- YDB web UI: `http://localhost:8765`

The backend container waits for local YDB, runs `alembic upgrade head`, then starts Uvicorn with `src.presentation.http.app:create_app`.

To start the frontend against this backend, run in `unijobs-ui` without Docker:

```bash
VITE_API_BASE_URL=http://localhost:8000/api npm run dev -- --host 0.0.0.0
```

Seed local YDB after migrations are applied:

```bash
DATABASE_BACKEND=ydb \
YDB_ENDPOINT=grpc://localhost:2136 \
YDB_DATABASE=/local \
YDB_AUTH_MODE=anonymous \
YDB_DISABLE_DISCOVERY=1 \
poetry run python seed_db.py
```

Seed cloud YDB with a short-lived IAM token:

```bash
DATABASE_BACKEND=ydb \
YDB_ENDPOINT=grpcs://<ydb-endpoint>:2135 \
YDB_DATABASE=<database-path> \
YDB_AUTH_MODE=access_token \
YDB_ACCESS_TOKEN="$(yc iam create-token)" \
poetry run python seed_db.py
```

Seed cloud YDB from a Yandex Cloud runtime with metadata credentials:

```bash
DATABASE_BACKEND=ydb \
YDB_ENDPOINT=grpcs://<ydb-endpoint>:2135 \
YDB_DATABASE=<database-path> \
YDB_AUTH_MODE=metadata \
poetry run python seed_db.py
```

Stop local services:

```bash
docker compose down
```
