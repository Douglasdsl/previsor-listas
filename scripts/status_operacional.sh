#!/usr/bin/env bash
set -euo pipefail
cd /srv/factory/apps/previsor-listas
source .venv/bin/activate
python -m src.gestao_ciclo
