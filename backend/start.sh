#!/bin/bash
set -e

echo "[start.sh] PORT=${PORT}"
echo "[start.sh] PYTHONPATH=${PYTHONPATH}"
echo "[start.sh] DATABASE_URL prefix=$(echo ${DATABASE_URL} | cut -c1-30)..."

echo "[start.sh] Running alembic upgrade head..."
python -m alembic upgrade head
echo "[start.sh] Alembic done."

echo "[start.sh] Starting uvicorn on 0.0.0.0:${PORT:-8000}..."
exec python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --log-level info
