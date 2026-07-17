#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

# Parar servidor anterior, se estiver rodando.
pkill -f "uvicorn src.api:app" 2>/dev/null || true
sleep 1

find src -type d -name '__pycache__' -prune -exec rm -rf {} +

# Validacao sem TestClient e sem dependencia httpx2.
python -m py_compile src/api.py src/service.py src/storage.py src/validacao.py src/features.py src/evaluate.py
python - <<'PY'
from src.api import app
from src.service import obter_status, gerar_previsao

status = obter_status()
assert status['total_listas'] >= 3736, status
print(f"IMPORT OK: app={app.title} total_listas={status['total_listas']}")

prev = gerar_previsao()
assert len(prev['previsao']) == 15, prev
print(f"PREVISAO OK: {prev['previsao_formatada']}")
PY

echo "[OK] Patch Fase 5A-R2 aplicado e validado sem TestClient/httpx2."
echo "Inicie novamente com: ./scripts/run_api.sh"
