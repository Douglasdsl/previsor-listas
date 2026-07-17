#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

python -m py_compile src/features.py src/evaluate.py src/baselines.py src/validacao.py src/diagnostico.py
python -m src.baselines

echo "[OK] Fase 1 aplicada e validada."
