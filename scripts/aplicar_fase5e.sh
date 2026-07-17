#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

find src -type d -name '__pycache__' -prune -exec rm -rf {} +
python -m py_compile src/recomendacao.py src/api.py src/feedback.py src/multi_predict.py src/methods.py src/service.py src/storage.py src/validacao.py src/features.py src/evaluate.py
python -m src.recomendacao

sudo systemctl restart previsor-listas.service
sleep 2
./scripts/healthcheck_web.sh

echo "[OK] Fase 5E aplicada."
echo "Acesse: http://192.168.15.25:8015/recomendacao"
