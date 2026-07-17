#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

mkdir -p reports docs scripts
find src -type d -name '__pycache__' -prune -exec rm -rf {} +

python -m py_compile src/comparar_modelos.py src/gerar_relatorio_fase3.py src/features.py src/evaluate.py src/validacao.py
python -m src.comparar_modelos
python -m src.gerar_relatorio_fase3

echo "[OK] Fase 3 aplicada e validada."
