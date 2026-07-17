#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

mkdir -p reports docs scripts
find src -type d -name '__pycache__' -prune -exec rm -rf {} +

python -m py_compile src/gerar_relatorio_decisorio.py src/predict_baseline.py src/features.py src/validacao.py
python src/gerar_relatorio_decisorio.py
python -m src.predict_baseline

echo "[OK] Fase 4 aplicada e validada."
