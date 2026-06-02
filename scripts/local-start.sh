#!/bin/sh
set -eu

python scripts/wait-for-ydb.py
alembic upgrade head
exec uvicorn src.presentation.http.app:create_app --factory --host 0.0.0.0 --port 8000
