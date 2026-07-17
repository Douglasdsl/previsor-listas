#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

find src -type d -name '__pycache__' -prune -exec rm -rf {} +
python -m py_compile src/api.py src/feedback.py src/multi_predict.py src/methods.py src/service.py src/storage.py src/validacao.py src/features.py src/evaluate.py

python - <<'PY'
from pathlib import Path
from src.feedback import parse_feedback_text
sample = "RELATORIO_PONTUACAO_CEGA_SEM_NUMEROS\nbase_total_listas=3736\nlista_indice=3737\nfrequencia_movel_50;Frequencia movel 50;11\nensemble_rank_baselines;Ensemble por ranking;11"
itens = parse_feedback_text(sample)
assert len(itens) == 2
assert itens[0]["nota"] == 11
assert Path("static/metodos.js").exists()
print("PARSE E STATIC JS OK")
PY

sudo systemctl restart previsor-listas.service
sleep 2
./scripts/healthcheck_web.sh

echo "[OK] Fase 5D-R4 aplicada."
echo "Acesse com hard refresh: http://192.168.15.25:8015/metodos"
