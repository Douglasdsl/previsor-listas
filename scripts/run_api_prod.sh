#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

HOST="${PREVISOR_HOST:-0.0.0.0}"
PORT="${PREVISOR_PORT:-8015}"

exec uvicorn src.api:app --host "$HOST" --port "$PORT"
