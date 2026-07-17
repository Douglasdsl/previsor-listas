#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

find src -type d -name '__pycache__' -prune -exec rm -rf {} +
python -m py_compile src/feedback.py src/methods.py src/multi_predict.py src/api.py src/service.py src/storage.py src/validacao.py src/features.py src/evaluate.py

python - <<'PY'
from src.feedback import parse_feedback_text
sample = "frequencia_acumulada;Frequência acumulada;10\nfrequencia_movel_50;Frequência móvel 50;11"
itens = parse_feedback_text(sample)
assert len(itens) == 2 and itens[1]['nota'] == 11
print('FEEDBACK PARSE OK')
PY

sudo systemctl restart previsor-listas.service
sleep 2
./scripts/healthcheck_web.sh

echo "[OK] Fase 5D aplicada e serviço reiniciado."
echo "Acesse: http://192.168.15.25:8015/metodos"
echo "Resumo feedback: http://192.168.15.25:8015/feedback-resumo"
