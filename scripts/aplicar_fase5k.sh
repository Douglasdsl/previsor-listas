#!/usr/bin/env bash
set -euo pipefail
cd /srv/factory/apps/previsor-listas
source .venv/bin/activate
find src -type d -name '__pycache__' -prune -exec rm -rf {} +
python -m py_compile src/gestao_ciclo.py src/gerador_oficial_v2.py src/feedback.py src/methods.py src/features.py src/validacao.py
python -m src.gestao_ciclo
python -m src.gerador_oficial_v2
chmod +x scripts/status_operacional.sh scripts/gerar_lista_oficial_v2.sh
printf '[OK] Fase 5K aplicada.\n'
