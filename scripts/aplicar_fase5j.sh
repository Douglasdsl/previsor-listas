#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

find src -type d -name '__pycache__' -prune -exec rm -rf {} +
python -m py_compile src/gerador_oficial.py src/feedback.py src/methods.py src/features.py src/validacao.py
python -m src.gerador_oficial

echo "[OK] Fase 5J aplicada. Relatório: reports/lista_oficial.md"
