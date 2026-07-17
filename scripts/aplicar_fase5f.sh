#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

find src -type d -name '__pycache__' -prune -exec rm -rf {} +
python -m py_compile src/feedback.py src/multi_predict.py src/recomendacao.py src/api.py src/methods.py src/service.py src/storage.py src/validacao.py src/features.py src/evaluate.py

python - <<'PY'
from src.feedback import parse_feedback_text, canonicalizar_feedbacks_keep_first
sample = "RELATORIO_PONTUACAO_CEGA_SEM_NUMEROS\nbase_total_listas=3736\nlista_indice=3737\nfrequencia_movel_50;Frequencia movel 50;11"
itens = parse_feedback_text(sample)
assert len(itens) == 1 and itens[0]['nota'] == 11
print('PARSE OK')
print('Canonicalizacao disponivel:', callable(canonicalizar_feedbacks_keep_first))
PY

# Limpa duplicidade existente preservando o primeiro feedback por bloco, conforme solicitado.
python - <<'PY'
from src.feedback import canonicalizar_feedbacks_keep_first
resultado = canonicalizar_feedbacks_keep_first()
print('CANONICALIZACAO:', resultado)
PY

python -m src.recomendacao
sudo systemctl restart previsor-listas.service
sleep 2
./scripts/healthcheck_web.sh

echo "[OK] Fase 5F aplicada."
echo "Acesse: http://192.168.15.25:8015/feedback-resumo"
echo "Acesse: http://192.168.15.25:8015/recomendacao"
